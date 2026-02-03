from django.contrib import admin
from .models import Client, Compte, Transaction


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'cni', 'email', 'telephone', 'date_creation')
    search_fields = ('nom', 'prenom', 'cni', 'email')
    list_filter = ('date_creation',)


@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
    list_display = ('iban', 'client', 'type_compte', 'solde', 'actif', 'date_ouverture')
    search_fields = ('iban', 'client__nom', 'client__prenom')
    list_filter = ('type_compte', 'actif', 'date_ouverture')
    readonly_fields = ('solde',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('type_transaction', 'compte_source', 'compte_destination', 'montant', 'date_transaction')
    search_fields = ('compte_source__iban', 'compte_destination__iban', 'description')
    list_filter = ('type_transaction', 'date_transaction')
    readonly_fields = ('date_transaction',)
