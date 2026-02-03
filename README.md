# Django Banking Application - Gestion des Comptes Bancaires

Application Django de gestion de comptes bancaires avec PostgreSQL, incluant les fonctionnalités de dépôt, retrait et virement.

## Fonctionnalités

### Modèles
- **Client** : Gestion des clients avec CNI unique
- **Compte** : Comptes bancaires avec IBAN, solde, et type (Courant/Épargne)
- **Transaction** : Historique des transactions (Dépôt/Retrait/Virement)

### Logique Métier
- Utilisation de `transaction.atomic` pour les virements garantissant la cohérence des données
- Validation automatique empêchant les retraits avec solde insuffisant
- Gestion des transactions atomiques pour éviter les incohérences

### Interface Utilisateur
- Design responsive avec Bootstrap 5
- Dashboard affichant le solde et l'historique des transactions
- Formulaires intuitifs pour les dépôts, retraits et virements
- Messages de confirmation et d'erreur contextuels
- Navigation simplifiée entre les comptes

## Installation

### Prérequis
- Python 3.8+
- PostgreSQL 12+ (optionnel, SQLite par défaut pour le développement)

### Configuration

1. Cloner le repository
```bash
git clone https://github.com/freddychoudja/GESTION-DES-COMPTES-BANCAIRES-COURANTS-D-UN-CLIENT-.git
cd GESTION-DES-COMPTES-BANCAIRES-COURANTS-D-UN-CLIENT-
```

2. Créer un environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Configuration de la base de données

**Pour SQLite (développement)** : Aucune configuration nécessaire, utilisé par défaut.

**Pour PostgreSQL (production)** :
Créer un fichier `.env` avec les variables suivantes :
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=banking_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
```

5. Créer la base de données PostgreSQL (si utilisée)
```bash
psql -U postgres
CREATE DATABASE banking_db;
\q
```

6. Appliquer les migrations
```bash
python manage.py migrate
```

7. Créer des données de test
```bash
python create_sample_data.py
```

8. Lancer le serveur de développement
```bash
python manage.py runserver
```

L'application sera accessible à : http://localhost:8000/

## Utilisation

### Interface d'Administration
Accédez à l'interface d'administration Django pour créer des clients et des comptes :
- URL : http://localhost:8000/admin/
- Identifiants par défaut (après exécution de create_sample_data.py) :
  - Username : `admin`
  - Password : `admin123`

### Interface Utilisateur

1. **Liste des comptes** : Page d'accueil affichant tous les comptes actifs
2. **Dashboard** : Vue détaillée d'un compte avec :
   - Informations du titulaire
   - Solde actuel
   - Historique des 20 dernières transactions
   - Boutons d'action (Dépôt, Retrait, Virement)

3. **Opérations disponibles** :
   - **Dépôt** : Ajouter des fonds à un compte
   - **Retrait** : Retirer des fonds (avec validation du solde)
   - **Virement** : Transférer des fonds entre comptes (utilise `transaction.atomic`)

## Architecture Technique

### Modèles de Données

**Client**
- `nom`, `prenom` : Nom et prénom du client
- `cni` : Carte Nationale d'Identité (unique)
- `email` : Email (unique)
- `telephone`, `adresse` : Coordonnées

**Compte**
- `client` : Lien vers le client propriétaire
- `iban` : IBAN du compte (unique)
- `solde` : Solde actuel (avec validation >= 0)
- `type_compte` : COURANT ou EPARGNE
- `actif` : Compte actif ou non

**Transaction**
- `compte_source` : Compte d'origine
- `compte_destination` : Compte destinataire (pour virements)
- `type_transaction` : DEPOT, RETRAIT, ou VIREMENT
- `montant` : Montant de la transaction
- `description` : Description optionnelle

### Sécurité et Validation

- Validation du solde insuffisant pour les retraits et virements
- Utilisation de `transaction.atomic()` pour garantir l'intégrité des virements
- Validation des montants positifs
- Protection CSRF sur tous les formulaires
- Validation au niveau modèle et vue

### Technologies Utilisées

- **Backend** : Django 4.2
- **Base de données** : PostgreSQL (avec support SQLite)
- **Frontend** : Bootstrap 5, Bootstrap Icons
- **ORM** : Django ORM avec transactions atomiques

## Structure du Projet

```
.
├── banking/                    # Application Django principale
│   ├── models.py              # Modèles Client, Compte, Transaction
│   ├── views.py               # Vues pour dashboard, dépôt, retrait, virement
│   ├── admin.py               # Configuration admin Django
│   ├── urls.py                # Routes de l'application
│   └── templates/             # Templates Bootstrap
│       └── banking/
│           ├── base.html      # Template de base
│           ├── liste_comptes.html
│           ├── dashboard.html
│           ├── depot.html
│           ├── retrait.html
│           └── virement.html
├── banking_project/           # Configuration Django
│   ├── settings.py            # Configuration (DB, apps, etc.)
│   └── urls.py                # Routes principales
├── manage.py                  # Script de gestion Django
├── requirements.txt           # Dépendances Python
├── create_sample_data.py      # Script de données de test
└── README.md                  # Ce fichier
```

## Tests Manuels

L'application a été testée avec les scénarios suivants :
1. ✅ Création de clients et comptes via l'admin
2. ✅ Affichage de la liste des comptes
3. ✅ Consultation du dashboard avec solde et historique
4. ✅ Dépôt de fonds (augmentation du solde)
5. ✅ Retrait avec validation du solde insuffisant
6. ✅ Retrait valide (diminution du solde)
7. ✅ Virement entre comptes avec `transaction.atomic`
8. ✅ Vérification de la cohérence des soldes après virement

## Fonctionnalités Avancées

### Transaction Atomique
Les virements utilisent `transaction.atomic()` de Django pour garantir que :
- Le débit du compte source ET le crédit du compte destination se font ensemble
- En cas d'erreur, aucune des deux opérations n'est effectuée (rollback automatique)
- Les données restent cohérentes même en cas de problème

### Validation du Solde
- Les retraits et virements vérifient le solde disponible
- Messages d'erreur clairs en cas de solde insuffisant
- Validation côté serveur pour la sécurité

## Licence

Ce projet est sous licence MIT.

## Auteur

Freddy Choudja - 2026