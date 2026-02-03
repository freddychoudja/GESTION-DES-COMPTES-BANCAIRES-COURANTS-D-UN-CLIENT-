from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from .models import Client, Compte, Transaction as BankTransaction
from decimal import Decimal


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
                
                messages.success(request, f"Dépôt de {montant}€ effectué avec succès")
                return redirect('dashboard', compte_id=compte.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    context = {'compte': compte}
    return render(request, 'banking/depot.html', context)


def retrait(request, compte_id):
    """Withdrawal form and handler"""
    compte = get_object_or_404(Compte, id=compte_id)
    
    if request.method == 'POST':
        try:
            montant = Decimal(request.POST.get('montant', 0))
            description = request.POST.get('description', '')
            
            if montant <= 0:
                messages.error(request, "Le montant doit être supérieur à 0")
            elif montant > compte.solde:
                messages.error(request, "Solde insuffisant pour effectuer ce retrait")
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
                
                messages.success(request, f"Retrait de {montant}€ effectué avec succès")
                return redirect('dashboard', compte_id=compte.id)
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    context = {'compte': compte}
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
                
                messages.success(request, f"Virement de {montant}€ effectué avec succès vers {compte_destination.iban}")
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
