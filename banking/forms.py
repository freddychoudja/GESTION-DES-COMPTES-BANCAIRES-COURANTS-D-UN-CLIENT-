from django import forms
from .models import Compte

class VirementForm(forms.Form):
    compte_source = forms.ModelChoiceField(
        queryset=Compte.objects.filter(actif=True),
        label="Compte source",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    iban_destination = forms.CharField(
        max_length=34,
        label="IBAN destination",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FR76...'})
    )
    montant = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        label="Montant",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        label="Description / Motif",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )

    def __init__(self, *args, **kwargs):
        client = kwargs.pop('client', None)
        super().__init__(*args, **kwargs)
        if client:
            self.fields['compte_source'].queryset = Compte.objects.filter(client=client, actif=True)

    def clean(self):
        cleaned_data = super().clean()
        compte_source = cleaned_data.get('compte_source')
        iban_destination = cleaned_data.get('iban_destination')
        montant = cleaned_data.get('montant')

        if compte_source and iban_destination and (compte_source.iban == iban_destination):
            raise forms.ValidationError("Le compte de destination ne peut pas être le même que le compte source.")

        if compte_source and montant and (compte_source.solde < montant):
            raise forms.ValidationError("Solde insuffisant sur le compte source.")
        
        return cleaned_data
