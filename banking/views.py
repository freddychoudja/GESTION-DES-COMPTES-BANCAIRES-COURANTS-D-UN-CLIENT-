from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.views.generic import TemplateView
from .models import Client, Compte, Transaction as BankTransaction
from decimal import Decimal
import secrets
import string
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Constantes de sécurité
PLAFOND_RETRAIT_JOURNALIER = Decimal('500000.00')  # Max 500,000 F CFA par jour
SEUIL_VIREMENT_CONFIRMATION = Decimal('100000.00')  # Virements > 100,000 F CFA nécessitent une confirmation
DEVISE = "F CFA"


def liste_clients(request):
    """List all clients with their accounts count"""
    clients = Client.objects.prefetch_related('comptes').order_by('-date_creation')
    
    # Add total balance to each client
    for client in clients:
        solde_total = sum(compte.solde for compte in client.comptes.all())
        client.solde_total = solde_total
    
    context = {'clients': clients}
    return render(request, 'banking/liste_clients.html', context)


def profile_client(request, client_id):
    """Display client profile with all their accounts"""
    client = get_object_or_404(Client, id=client_id)
    comptes = client.comptes.all()
    
    # Calculate total balance
    solde_total = sum(compte.solde for compte in comptes)
    
    context = {
        'client': client,
        'comptes': comptes,
        'solde_total': solde_total,
    }
    return render(request, 'banking/profile_client.html', context)


def edit_client(request, client_id):
    """Edit client information"""
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == 'POST':
        try:
            client.nom = request.POST.get('nom', client.nom)
            client.prenom = request.POST.get('prenom', client.prenom)
            client.email = request.POST.get('email', client.email)
            client.telephone = request.POST.get('telephone', client.telephone)
            client.adresse = request.POST.get('adresse', client.adresse)
            
            client.full_clean()
            client.save()
            
            messages.success(request, f"Profil de {client.nom} {client.prenom} modifié avec succès")
            return redirect('profile_client', client_id=client.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    context = {'client': client}
    return render(request, 'banking/edit_client.html', context)


def create_compte(request, client_id):
    """Create a new account for a client"""
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == 'POST':
        try:
            type_compte = request.POST.get('type_compte', 'COURANT')
            solde_initial = Decimal(request.POST.get('solde_initial', 0))
            
            if solde_initial < 0:
                messages.error(request, "Le solde initial ne peut pas être négatif")
            else:
                # Generate unique IBAN (Cameroon format: CM76)
                iban = f"CM76{secrets.token_hex(14).upper()}"
                
                # Ensure IBAN is unique
                while Compte.objects.filter(iban=iban).exists():
                    iban = f"CM76{secrets.token_hex(14).upper()}"
                
                compte = Compte.objects.create(
                    client=client,
                    iban=iban,
                    solde=solde_initial,
                    type_compte=type_compte,
                    actif=True
                )
                
                messages.success(request, f"Compte {compte.iban} créé avec succès")
                return redirect('profile_client', client_id=client.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    context = {'client': client}
    return render(request, 'banking/create_compte.html', context)


def dashboard(request, compte_id):
    """Dashboard view showing balance and transaction history"""
    compte = get_object_or_404(Compte, id=compte_id)
    
    # Get all transactions for this account using Q objects for efficient single query
    from django.db.models import Q
    all_transactions = BankTransaction.objects.filter(
        Q(compte_source=compte) | Q(compte_destination=compte)
    ).select_related('compte_source', 'compte_destination').order_by('-date_transaction')[:20]
    
    # Add helper attributes for template rendering
    for trans in all_transactions:
        # Determine if transaction is incoming (positive) for this account
        if trans.type_transaction == 'DEPOT':
            trans.is_incoming = True
        elif trans.type_transaction == 'RETRAIT':
            trans.is_incoming = False
        elif trans.type_transaction == 'VIREMENT':
            trans.is_incoming = (trans.compte_destination_id == compte.id)
        else:
            trans.is_incoming = False
    
    context = {
        'compte': compte,
        'transactions': all_transactions,
    }
    return render(request, 'banking/dashboard.html', context)


def depot(request, compte_id):
    """Deposit form and handler"""
    compte = get_object_or_404(Compte, id=compte_id)
    
    if request.method == 'POST':
        try:
            montant = Decimal(request.POST.get('montant', 0))
            description = request.POST.get('description', '')
            
            if montant <= 0:
                messages.error(request, "Le montant doit être supérieur à 0")
            else:
                # Create deposit transaction
                with transaction.atomic():
                    compte.solde += montant
                    compte.save()
                    
                    BankTransaction.objects.create(
                        compte_source=compte,
                        type_transaction='DEPOT',
                        montant=montant,
                        description=description
                    )
                
                messages.success(request, f"Dépôt de {montant} F CFA effectué avec succès")
                return redirect('dashboard', compte_id=compte.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    context = {'compte': compte}
    return render(request, 'banking/depot.html', context)


def retrait(request, compte_id):
    """Withdrawal form and handler with daily limit"""
    compte = get_object_or_404(Compte, id=compte_id)
    
    # Calculate today's withdrawals
    today = datetime.now().date()
    retraits_aujourd_hui = BankTransaction.objects.filter(
        compte_source=compte,
        type_transaction='RETRAIT',
        date_transaction__date=today
    ).aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
    
    solde_retrait_disponible = PLAFOND_RETRAIT_JOURNALIER - retraits_aujourd_hui
    
    if request.method == 'POST':
        try:
            montant = Decimal(request.POST.get('montant', 0))
            description = request.POST.get('description', '')
            
            if montant <= 0:
                messages.error(request, "Le montant doit être supérieur à 0")
            elif montant > compte.solde:
                messages.error(request, f"Solde insuffisant pour effectuer ce retrait (Solde: {compte.solde}€)")
            elif montant > solde_retrait_disponible:
                messages.error(request, f"Dépassement du plafond de retrait journalier. Vous pouvez retirer {solde_retrait_disponible}€ aujourd'hui.")
            else:
                # Create withdrawal transaction
                with transaction.atomic():
                    compte.solde -= montant
                    compte.save()
                    
                    BankTransaction.objects.create(
                        compte_source=compte,
                        type_transaction='RETRAIT',
                        montant=montant,
                        description=description
                    )
                
                messages.success(request, f"Retrait de {montant} F CFA effectué avec succès")
                return redirect('dashboard', compte_id=compte.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    context = {
        'compte': compte,
        'plafond_retrait': PLAFOND_RETRAIT_JOURNALIER,
        'retraits_aujourd_hui': retraits_aujourd_hui,
        'solde_retrait_disponible': solde_retrait_disponible,
    }
    return render(request, 'banking/retrait.html', context)


def virement(request, compte_id):
    """Transfer form and handler using transaction.atomic"""
    compte_source = get_object_or_404(Compte, id=compte_id)
    
    # Get all active accounts except the source account
    comptes_destination = Compte.objects.filter(actif=True).exclude(id=compte_id)
    
    if request.method == 'POST':
        try:
            montant = Decimal(request.POST.get('montant', 0))
            compte_destination_id = request.POST.get('compte_destination')
            description = request.POST.get('description', '')
            
            if not compte_destination_id:
                messages.error(request, "Veuillez sélectionner un compte de destination")
            elif montant <= 0:
                messages.error(request, "Le montant doit être supérieur à 0")
            elif montant > compte_source.solde:
                messages.error(request, "Solde insuffisant pour effectuer ce virement")
            else:
                compte_destination = get_object_or_404(Compte, id=compte_destination_id)
                
                # Use transaction.atomic for transfer
                with transaction.atomic():
                    # Deduct from source account
                    compte_source.solde -= montant
                    compte_source.save()
                    
                    # Add to destination account
                    compte_destination.solde += montant
                    compte_destination.save()
                    
                    # Create transaction record
                    BankTransaction.objects.create(
                        compte_source=compte_source,
                        compte_destination=compte_destination,
                        type_transaction='VIREMENT',
                        montant=montant,
                        description=description
                    )
                
                messages.success(request, f"Virement de {montant} F CFA effectué avec succès vers {compte_destination.iban}")
                return redirect('dashboard', compte_id=compte_source.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    context = {
        'compte': compte_source,
        'comptes_destination': comptes_destination,
    }
    return render(request, 'banking/virement.html', context)


def liste_comptes(request):
    """List all accounts"""
    comptes = Compte.objects.filter(actif=True).select_related('client')
    context = {'comptes': comptes}
    return render(request, 'banking/liste_comptes.html', context)


def telecharger_rib(request, compte_id):
    """Download RIB (Relevé d'Identité Bancaire) as PDF"""
    compte = get_object_or_404(Compte, id=compte_id)
    client = compte.client
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="RIB_{compte.iban}.pdf"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0d6efd'),
        alignment=TA_CENTER,
        spaceAfter=0.5*cm
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=0.3*cm,
        spaceBefore=0.3*cm
    )
    
    # Title
    story.append(Paragraph("RELEVÉ D'IDENTITÉ BANCAIRE", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Bank info section
    story.append(Paragraph("BANQUE CAMEROUNAISE", header_style))
    bank_data = [
        ['Établissement:', 'Gestion des Comptes Bancaires Camerounais (GCBC)'],
        ['Contact:', 'support@gcbc-cameroun.cm'],
    ]
    bank_table = Table(bank_data, colWidths=[3*cm, 10*cm])
    bank_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(bank_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Client info section
    story.append(Paragraph("TITULAIRE DU COMPTE", header_style))
    client_data = [
        ['Nom:', f"{client.nom} {client.prenom}"],
        ['CNI:', client.cni],
        ['Adresse:', client.adresse],
        ['Email:', client.email],
        ['Téléphone:', client.telephone],
    ]
    client_table = Table(client_data, colWidths=[3*cm, 10*cm])
    client_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Account info section
    story.append(Paragraph("INFORMATIONS DU COMPTE", header_style))
    account_data = [
        ['IBAN:', f"{compte.iban}"],
        ['Type de Compte:', compte.get_type_compte_display()],
        ['Solde Actuel:', f"{compte.solde} F CFA"],
        ['Statut:', 'Actif' if compte.actif else 'Fermé'],
        ['Date d\'ouverture:', compte.date_ouverture.strftime('%d/%m/%Y')],
    ]
    account_table = Table(account_data, colWidths=[3*cm, 10*cm])
    account_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(account_table)
    story.append(Spacer(1, 1*cm))
    
    # Footer
    footer_text = f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.grey)))
    
    # Build PDF
    doc.build(story)
    return response


def telecharger_releve(request, compte_id):
    """Download account statement (relevé mensuel) as PDF"""
    compte = get_object_or_404(Compte, id=compte_id)
    client = compte.client
    
    # Get this month's transactions
    today = datetime.now()
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    transactions = BankTransaction.objects.filter(
        Q(compte_source=compte) | Q(compte_destination=compte),
        date_transaction__date__gte=first_day.date(),
        date_transaction__date__lte=last_day.date()
    ).order_by('-date_transaction')
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Releve_{compte.iban}_{today.strftime("%m_%Y")}.pdf"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#0d6efd'),
        alignment=TA_CENTER,
        spaceAfter=0.5*cm
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
    )
    
    # Title
    month_year = first_day.strftime('%B %Y')
    story.append(Paragraph(f"RELEVÉ DE COMPTE - {month_year.upper()}", title_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Account info
    info_text = f"<b>Titulaire:</b> {client.nom} {client.prenom} | <b>IBAN:</b> {compte.iban} | <b>Compte:</b> {compte.get_type_compte_display()}"
    story.append(Paragraph(info_text, header_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Summary
    solde_debut = compte.solde
    total_depots = transactions.filter(type_transaction='DEPOT').aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
    total_retraits = transactions.filter(type_transaction='RETRAIT').aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
    total_virements_sortants = transactions.filter(type_transaction='VIREMENT', compte_source=compte).aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
    total_virements_entrants = transactions.filter(type_transaction='VIREMENT', compte_destination=compte).aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
    
    summary_data = [
        ['Libellé', 'Montant'],
        ['Solde début de mois', f"{solde_debut} F CFA"],
        ['Dépôts', f"+{total_depots} F CFA"],
        ['Retraits', f"-{total_retraits} F CFA"],
        ['Virements envoyés', f"-{total_virements_sortants} F CFA"],
        ['Virements reçus', f"+{total_virements_entrants} F CFA"],
    ]
    summary_table = Table(summary_data, colWidths=[10*cm, 3*cm])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Transactions
    if transactions:
        story.append(Paragraph("DÉTAIL DES TRANSACTIONS", styles['Heading2']))
        story.append(Spacer(1, 0.2*cm))
        
        transaction_data = [['Date', 'Type', 'Description', 'Montant', 'Contrepartie']]
        
        for trans in transactions:
            date_str = trans.date_transaction.strftime('%d/%m/%Y')
            type_str = trans.get_type_transaction_display()
            
            if trans.type_transaction == 'VIREMENT':
                if trans.compte_source_id == compte.id:
                    contrepartie = trans.compte_destination.iban
                else:
                    contrepartie = trans.compte_source.iban
            else:
                contrepartie = '-'
            
            montant_str = f"{trans.montant} F CFA"
            
            transaction_data.append([
                date_str,
                type_str,
                trans.description[:30] if trans.description else '-',
                montant_str,
                contrepartie
            ])
        
        trans_table = Table(transaction_data, colWidths=[2.5*cm, 2*cm, 4*cm, 2*cm, 3.5*cm])
        trans_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),
        ]))
        story.append(trans_table)
    else:
        story.append(Paragraph("Aucune transaction ce mois-ci.", styles['Normal']))
    
    story.append(Spacer(1, 1*cm))
    footer_text = f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.grey, fontSize=9)))
    
    # Build PDF
    doc.build(story)
    return response


def statistiques_compte(request, compte_id):
    """Display account statistics and charts"""
    compte = get_object_or_404(Compte, id=compte_id)
    client = compte.client
    
    # Get last 90 days of transactions
    today = datetime.now()
    start_date = today - timedelta(days=90)
    
    # Get all transactions for this account
    all_transactions = BankTransaction.objects.filter(
        Q(compte_source=compte) | Q(compte_destination=compte),
        date_transaction__gte=start_date
    ).order_by('date_transaction')
    
    # Calculate daily balances
    daily_data = {}
    current_balance = compte.solde
    
    # Get initial balance
    before_period = BankTransaction.objects.filter(
        Q(compte_source=compte) | Q(compte_destination=compte),
        date_transaction__lt=start_date
    )
    
    initial_changes = Decimal('0')
    for trans in before_period:
        if trans.type_transaction == 'DEPOT' or (trans.type_transaction == 'VIREMENT' and trans.compte_destination_id == compte.id):
            initial_changes += trans.montant
        else:
            initial_changes -= trans.montant
    
    initial_balance = current_balance - initial_changes
    balance = initial_balance
    
    # Build daily summary
    for trans in all_transactions:
        date_key = trans.date_transaction.date()
        
        if trans.type_transaction == 'DEPOT' or (trans.type_transaction == 'VIREMENT' and trans.compte_destination_id == compte.id):
            balance += trans.montant
        else:
            balance -= trans.montant
        
        if date_key not in daily_data:
            daily_data[date_key] = balance
        else:
            daily_data[date_key] = balance
    
    # Prepare chart data
    dates = sorted(daily_data.keys())
    balances = [daily_data[d] for d in dates]
    
    if not dates:
        # No transactions, show current balance
        dates = [today.date()]
        balances = [compte.solde]
    
    # Create chart
    plt.figure(figsize=(12, 6))
    plt.plot(dates, balances, marker='o', linewidth=2, color='#0d6efd', markersize=4)
    plt.fill_between(range(len(dates)), balances, alpha=0.3, color='#0d6efd')
    plt.title(f'Évolution du Solde - {compte.iban}', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Solde (€)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    chart_data = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    # Calculate statistics
    last_30_days = today - timedelta(days=30)
    transactions_30 = BankTransaction.objects.filter(
        Q(compte_source=compte) | Q(compte_destination=compte),
        date_transaction__gte=last_30_days
    )
    
    total_depots = transactions_30.filter(type_transaction='DEPOT').aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
    total_retraits = transactions_30.filter(type_transaction='RETRAIT').aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
    total_virements_out = transactions_30.filter(type_transaction='VIREMENT', compte_source=compte).aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
    total_virements_in = transactions_30.filter(type_transaction='VIREMENT', compte_destination=compte).aggregate(Sum('montant'))['montant__sum'] or Decimal('0')
    
    context = {
        'compte': compte,
        'chart_data': chart_data,
        'total_depots': total_depots,
        'total_retraits': total_retraits,
        'total_virements_out': total_virements_out,
        'total_virements_in': total_virements_in,
        'transaction_count': transactions_30.count(),
        'balance_min': min(balances) if balances else compte.solde,
        'balance_max': max(balances) if balances else compte.solde,
    }
    
    return render(request, 'banking/statistiques.html', context)
