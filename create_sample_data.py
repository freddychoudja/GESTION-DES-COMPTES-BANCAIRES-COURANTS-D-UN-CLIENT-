#!/usr/bin/env python3
"""
Script to create sample data for testing the banking application
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
    print("Creating sample data...")
    
    # Create superuser if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("✓ Superuser created (username: admin, password: admin123)")
    
    # Create clients
    client1, created = Client.objects.get_or_create(
        cni='CNI123456',
        defaults={
            'nom': 'Dupont',
            'prenom': 'Jean',
            'email': 'jean.dupont@example.com',
            'telephone': '+33123456789',
            'adresse': '123 Rue de Paris, 75001 Paris'
        }
    )
    if created:
        print("✓ Client 1 created: Jean Dupont")
    
    client2, created = Client.objects.get_or_create(
        cni='CNI789012',
        defaults={
            'nom': 'Martin',
            'prenom': 'Marie',
            'email': 'marie.martin@example.com',
            'telephone': '+33987654321',
            'adresse': '456 Avenue des Champs, 75008 Paris'
        }
    )
    if created:
        print("✓ Client 2 created: Marie Martin")
    
    # Create accounts
    compte1, created = Compte.objects.get_or_create(
        iban='FR7612345678901234567890123',
        defaults={
            'client': client1,
            'solde': Decimal('1000.00'),
            'type_compte': 'COURANT'
        }
    )
    if created:
        print("✓ Compte 1 created for Jean Dupont (1000€)")
    
    compte2, created = Compte.objects.get_or_create(
        iban='FR7698765432109876543210987',
        defaults={
            'client': client2,
            'solde': Decimal('2000.00'),
            'type_compte': 'EPARGNE'
        }
    )
    if created:
        print("✓ Compte 2 created for Marie Martin (2000€)")
    
    compte3, created = Compte.objects.get_or_create(
        iban='FR7611111111111111111111111',
        defaults={
            'client': client1,
            'solde': Decimal('500.00'),
            'type_compte': 'EPARGNE'
        }
    )
    if created:
        print("✓ Compte 3 created for Jean Dupont (500€)")
    
    print("\nSample data created successfully!")
    print("\nYou can now:")
    print("1. Access admin panel: http://localhost:8000/admin/")
    print("   Username: admin")
    print("   Password: admin123")
    print("2. View accounts: http://localhost:8000/")

if __name__ == '__main__':
    create_sample_data()
