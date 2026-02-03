#!/usr/bin/env python3
"""
Script pour creer des donnees d'exemple pour l'application bancaire camerounaise
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_project.settings')
django.setup()

from banking.models import Client, Compte, Transaction as BankTransaction
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

def create_sample_data():
    print("Creation des donnees d'exemple - Contexte Camerounais\n")
    
    # Create superuser if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("✓ Superutilisateur cree (identifiant: admin, motdepasse: admin123)")
    
    # Create clients camerounais
    client1, created = Client.objects.get_or_create(
        cni='CM-1234567890123',
        defaults={
            'nom': 'Tandjigora',
            'prenom': 'Emmanuel',
            'email': 'emmanuel.tandjigora@example.cm',
            'telephone': '+237123456789',
            'adresse': '123 Rue Bilingual, Douala, Cameroun'
        }
    )
    if created:
        print("✓ Client 1 cree: Emmanuel Tandjigora")
    
    client2, created = Client.objects.get_or_create(
        cni='CM-9876543210987',
        defaults={
            'nom': 'Kamgueu',
            'prenom': 'Sarah',
            'email': 'sarah.kamgueu@example.cm',
            'telephone': '+237987654321',
            'adresse': '456 Avenue de la Republique, Yaounde, Cameroun'
        }
    )
    if created:
        print("✓ Client 2 cree: Sarah Kamgueu")
    
    # Create comptes - IBAN camerounais
    import secrets
    import string
    
    def generate_iban():
        """Generer un IBAN au format camerounais CM76"""
        return f"CM76{secrets.token_hex(14).upper()}"
    
    compte1, created = Compte.objects.get_or_create(
        client=client1,
        iban=generate_iban(),
        defaults={
            'solde': Decimal('500000.00'),  # 500,000 F CFA
            'type_compte': 'COURANT'
        }
    )
    if created:
        print("✓ Compte 1 cree pour Emmanuel Tandjigora (500 000 F CFA)")
    
    compte2, created = Compte.objects.get_or_create(
        client=client2,
        iban=generate_iban(),
        defaults={
            'solde': Decimal('1000000.00'),  # 1,000,000 F CFA
            'type_compte': 'COURANT'
        }
    )
    if created:
        print("✓ Compte 2 cree pour Sarah Kamgueu (1 000 000 F CFA)")
    
    compte3, created = Compte.objects.get_or_create(
        client=client1,
        iban=generate_iban(),
        defaults={
            'solde': Decimal('250000.00'),  # 250,000 F CFA
            'type_compte': 'EPARGNE'
        }
    )
    if created:
        print("✓ Compte 3 cree pour Emmanuel Tandjigora (250 000 F CFA) - Epargne")
    
    print("\nDonnees d'exemple creees avec succes!")
    print("\nVous pouvez maintenant:")
    print("1. Acceder au panneau d'administration: http://localhost:8000/admin/")
    print("   Identifiant: admin")
    print("   Motdepasse: admin123")
    print("2. Consulter les comptes: http://localhost:8000/")

if __name__ == '__main__':
    create_sample_data()
