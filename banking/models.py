from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Client(models.Model):
    """Client model with unique CNI (Carte Nationale d'Identité)"""
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    cni = models.CharField(max_length=50, unique=True, verbose_name="CNI")
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom} {self.prenom} (CNI: {self.cni})"


class Compte(models.Model):
    """Compte bancaire with IBAN, balance, and type"""
    TYPE_CHOICES = [
        ('COURANT', 'Compte Courant'),
        ('EPARGNE', 'Compte Épargne'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='comptes')
    iban = models.CharField(max_length=34, unique=True, verbose_name="IBAN")
    solde = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name="Solde"
    )
    type_compte = models.CharField(max_length=10, choices=TYPE_CHOICES, default='COURANT')
    date_ouverture = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Compte"
        verbose_name_plural = "Comptes"
        ordering = ['-date_ouverture']
    
    def __str__(self):
        return f"{self.iban} - {self.client.nom} ({self.solde}€)"


class Transaction(models.Model):
    """Transaction model for Dépôt, Retrait, and Virement"""
    TYPE_CHOICES = [
        ('DEPOT', 'Dépôt'),
        ('RETRAIT', 'Retrait'),
        ('VIREMENT', 'Virement'),
    ]
    
    compte_source = models.ForeignKey(
        Compte, 
        on_delete=models.CASCADE, 
        related_name='transactions_sortantes',
        verbose_name="Compte source"
    )
    compte_destination = models.ForeignKey(
        Compte, 
        on_delete=models.CASCADE, 
        related_name='transactions_entrantes',
        null=True, 
        blank=True,
        verbose_name="Compte destination"
    )
    type_transaction = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    description = models.TextField(blank=True)
    date_transaction = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-date_transaction']
    
    def __str__(self):
        return f"{self.type_transaction} - {self.montant}€ - {self.date_transaction.strftime('%d/%m/%Y %H:%M')}"
    
    def clean(self):
        """Validate transaction rules"""
        if self.type_transaction == 'VIREMENT' and not self.compte_destination:
            raise ValidationError("Un virement nécessite un compte de destination")
        
        if self.type_transaction == 'RETRAIT':
            if self.montant > self.compte_source.solde:
                raise ValidationError("Solde insuffisant pour effectuer ce retrait")
        
        if self.type_transaction in ['RETRAIT', 'VIREMENT']:
            if self.montant > self.compte_source.solde:
                raise ValidationError("Solde insuffisant pour effectuer cette transaction")
