# 🇨🇲 ADAPTATION CAMEROUNAISE - Gestion des Comptes Bancaires

## Contexte d'Utilisation
Cette application est adaptée au contexte camerounais avec utilisation du **Franc CFA (F CFA)** comme devise unique.

## ✅ Changements Effectués

### 1. Devise Monétaire
- **Avant:** € (Euro)
- **Après:** F CFA (Franc CFA)
- Tous les montants sont maintenant affichés en F CFA
- Mise à jour de tous les templates HTML et vues Python

### 2. Format IBAN
- **Avant:** FR76 XXXXXXXXXXXX (Format français)
- **Après:** CM76 XXXXXXXXXXXX (Format camerounais)
- Les nouveaux IBANs générés utilisent le préfixe camerounais

### 3. Données d'Exemple
Deux scripts sont disponibles :

#### Script Original (données françaises)
```bash
python create_sample_data.py
```
- Clients français (Jean Dupont, Marie Martin)
- Montants: 1000€, 2000€, 500€

#### Script Camerounais (données camerounaises)
```bash
python create_sample_data_cameroun.py
```
- Clients camerounais (Emmanuel Tandjigora, Sarah Kamgueu)
- Montants: 500 000 F CFA, 1 000 000 F CFA, 250 000 F CFA

### 4. Plafonds et Limites Adaptés
- **Plafond de retrait journalier:** 500 000 F CFA (au lieu de 1000€)
- **Seuil de virement:** 100 000 F CFA (pour confirmation double)
- Approprié au contexte économique camerounais

### 5. Textes et Terminologie
- **Établissement:** "Gestion des Comptes Bancaires Camerounais (GCBC)"
- **Contact:** support@gcbc-cameroun.cm
- Messages en français camerounais
- Références géographiques: Douala, Yaoundé, Cameroun

## 📋 Structure Créée

### Fichiers Modifiés
```
banking/views.py                  ← Constantes et logique d'affaires
banking/urls.py                   ← Routes
banking/templates/banking/
  ├── base.html                   ← Footer adapté
  ├── dashboard.html              ← Devise F CFA
  ├── depot.html                  ← Devise F CFA
  ├── retrait.html                ← Plafonds camerounais
  ├── virement.html               ← Devise F CFA
  ├── statistiques.html           ← Graphiques avec F CFA
  ├── liste_comptes.html          ← Devise F CFA
  └── ...
```

### Fichiers Créés
```
adapt_cameroun.py                 ← Script d'adaptation
create_sample_data_cameroun.py    ← Données camerounaises
CONTEXTE_CAMEROUNAIS.md           ← Ce fichier
```

## 🚀 Utilisation

### Installation
```bash
# Clone le repo
git clone ...
cd GESTION-DES-COMPTES-BANCAIRES-COURANTS-D-UN-CLIENT-

# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Charger les données camerounaises
python create_sample_data_cameroun.py

# Lancer le serveur
python manage.py runserver
```

### Accès
- **Interface:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/
  - Identifiant: admin
  - Mot de passe: admin123

## 💰 Montants D'Exemple

| Client | Compte | Type | Solde |
|--------|--------|------|-------|
| Emmanuel Tandjigora | CM76... | Courant | 500 000 F CFA |
| Sarah Kamgueu | CM76... | Courant | 1 000 000 F CFA |
| Emmanuel Tandjigora | CM76... | Épargne | 250 000 F CFA |

## ⚙️ Constantes Configurées

```python
# Sécurité et Limites
PLAFOND_RETRAIT_JOURNALIER = 500 000 F CFA  # Max par jour
SEUIL_VIREMENT_CONFIRMATION = 100 000 F CFA  # Virements > ce montant
DEVISE = "F CFA"                              # Devise affichée
```

## 📊 Fonctionnalités Disponibles

### Gestion Clients
- ✅ Liste des clients camerounais
- ✅ Profil avec détails
- ✅ Modification d'informations
- ✅ Création de comptes

### Opérations Bancaires
- ✅ **Dépôt** - En F CFA
- ✅ **Retrait** - Avec plafond de 500 000 F CFA/jour
- ✅ **Virement** - Entre comptes camerounais
- ✅ **Historique** - En F CFA

### Fonctionnalités Avancées
- 📄 **Export PDF**
  - RIB en format camerounais
  - Relevé mensuel en F CFA
- 📊 **Statistiques et Graphiques**
  - Évolution sur 90 jours
  - Statistiques 30 jours
- 🔐 **Sécurité**
  - Plafonds journaliers
  - Transactions atomiques
  - Validation des soldes

## 🔧 Développement Futur

Possibilités d'amélioration:
- [ ] Intégration SMS MTN/Orange pour confirmations
- [ ] Support des numéros de téléphone camerounais (+237...)
- [ ] Codes régionaux (Douala 237-1, Yaoundé 237-2, etc.)
- [ ] Intégration avec banques camerounaises réelles
- [ ] Support du français camerounais uniquement

## 📝 Notes Importantes

1. **CNI:** Les numéros de CNI sont au format camerounais (CM-XXXXXXXXXX)
2. **Téléphones:** Format international +237 (Cameroun)
3. **Adresses:** Références camerounaises (villes, quartiers)
4. **Devise:** Tous les calculs sont en F CFA
5. **Plafonds:** 500 000 F CFA ≈ 760€ - adapté à l'économie locale

## 🎓 Utilisation Pédagogique

Cette adaptation montre comment adapter une application Django pour:
- Changer la devise de base
- Adapter les plafonds au contexte économique
- Localiser le contenu
- Générer des IBAN régionaux
- Utiliser des données représentatives

---

**Date de création:** 3 février 2026
**Contexte:** Cameroun 🇨🇲
**Devise:** Franc CFA (F CFA)
