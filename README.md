# Django Banking Application - Gestion des Comptes Bancaires

Application Django de gestion de comptes bancaires avec PostgreSQL, incluant les fonctionnalités de dépôt, retrait et virement.

## Fonctionnalités

### Fonctionnalités de Base ✅

#### Gestion des Clients
- **Liste des clients** : Affichage de tous les clients avec CNI, email, téléphone
- **Profil client** : Vue détaillée avec tous les comptes et solde total
- **Modification client** : Édition des informations personnelles
- **Création d'identifiant unique** : CNI et email uniques

#### Gestion des Comptes
- **Création de compte** : Interface pour ouvrir de nouveaux comptes (Courant/Épargne)
- **IBAN automatique** : Génération unique pour chaque compte
- **Types de compte** : Compte Courant et Compte Épargne
- **Affichage du solde** : Solde en temps réel

#### Opérations Bancaires
- **Dépôt** : Créditer un compte en espèces
- **Retrait** : Débiter avec vérification du solde (sécurité)
- **Virement** : Transférer entre comptes avec `transaction.atomic`
- **Historique** : Relevé de compte complet avec dates et montants

### Logique Métier
- Utilisation de `transaction.atomic` pour les virements garantissant la cohérence des données
- Validation automatique empêchant les retraits avec solde insuffisant
- Gestion des transactions atomiques pour éviter les incohérences
- Validation des montants positifs
- Protection contre les soldes négatifs

### Interface Utilisateur
- Design responsive avec Bootstrap 5 et Bootstrap Icons
- Dashboard enrichi affichant solde et historique des transactions
- Formulaires intuitifs pour les dépôts, retraits et virements
- Messages de confirmation et d'erreur contextuels
- Navigation fluide entre clients et comptes

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

#### Page d'Accueil & Navigation
- **Liste des clients** (`/`) : Tableau avec tous les clients, comptes, et soldes
- Navigation intuitive via la barre de navigation Bootstrap

#### Gestion des Clients
1. **Voir le profil** : Affiche le client avec toutes ses informations et comptes
2. **Modifier le client** : Formulaire pour mettre à jour les coordonnées
3. **Créer un compte** : Ouvrir un nouveau compte pour le client

#### Opérations sur les Comptes
1. **Dashboard du compte** : 
   - Informations du titulaire
   - Solde actuel en gros caractères
   - 20 dernières transactions avec types et montants
   - Boutons d'action

2. **Opérations disponibles** :
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
│   ├── views.py               # 9 vues : clients, profil, modification, création compte, transactions
│   ├── admin.py               # Configuration admin Django
│   ├── urls.py                # 9 routes de l'application
│   └── templates/             # Templates Bootstrap 5
│       └── banking/
│           ├── base.html      # Template de base avec navbar
│           ├── liste_clients.html      # Liste de tous les clients
│           ├── profile_client.html     # Profil d'un client avec ses comptes
│           ├── edit_client.html        # Formulaire de modification
│           ├── create_compte.html      # Création de nouveau compte
│           ├── liste_comptes.html      # Liste des comptes actifs
│           ├── dashboard.html          # Dashboard avec solde et historique
│           ├── depot.html              # Formulaire de dépôt
│           ├── retrait.html            # Formulaire de retrait
│           └── virement.html           # Formulaire de virement
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
2. ✅ Affichage de la liste des clients avec statistiques
3. ✅ Consultation du profil client avec tous les comptes
4. ✅ Modification des informations d'un client
5. ✅ Création d'un nouveau compte via interface web
6. ✅ Affichage du dashboard avec solde et historique
7. ✅ Dépôt de fonds (augmentation du solde)
8. ✅ Retrait avec validation du solde insuffisant
9. ✅ Retrait valide (diminution du solde)
10. ✅ Virement entre comptes avec `transaction.atomic`
11. ✅ Vérification de la cohérence des soldes après virement
12. ✅ Navigation fluide entre clients et comptes

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

### Génération d'IBAN
- IBAN unique généré automatiquement pour chaque compte
- Format simplifié : FR76 suivi de caractères aléatoires hexadécimaux

---

## 🚀 Fonctionnalités Bonus (À Implémenter)

### 📄 Export PDF
- [ ] Télécharger le RIB (Relevé d'Identité Bancaire) en PDF
- [ ] Générer le relevé mensuel en PDF
- Technologies : `reportlab` ou `xhtml2pdf`

### 🔐 Sécurité Avancée
- [ ] Double authentification : Code de confirmation pour virements > 500€
- [ ] Gestion des plafonds : Limite de retrait journalier (ex: 1000€)
- [ ] Historique des tentatives échouées

### 📊 Analytics & Dashboard Admin
- [ ] Graphiques : Évolution du solde sur 3 mois
- [ ] Statistiques : Total des dépôts, virements, retraits
- [ ] Panel admin : Vue globale de tous les clients et transactions
- Technologies : `matplotlib`, `Chart.js`, ou `Plotly`

### 📧 Notifications
- [ ] Message de confirmation après chaque opération
- [ ] Alertes pour les retraits importants
- [ ] Historique des notifications

---

## Routes Disponibles

| URL | Vue | Description |
|-----|-----|-------------|
| `/` | `liste_clients` | Liste de tous les clients |
| `/clients/` | `liste_clients` | Alias de la page d'accueil |
| `/client/<id>/` | `profile_client` | Profil détaillé d'un client |
| `/client/<id>/edit/` | `edit_client` | Modification du profil client |
| `/client/<id>/new_compte/` | `create_compte` | Création d'un nouveau compte |
| `/comptes/` | `liste_comptes` | Liste de tous les comptes actifs |
| `/dashboard/<id>/` | `dashboard` | Dashboard d'un compte |
| `/depot/<id>/` | `depot` | Formulaire et traitement du dépôt |
| `/retrait/<id>/` | `retrait` | Formulaire et traitement du retrait |
| `/virement/<id>/` | `virement` | Formulaire et traitement du virement |
| `/admin/` | Django Admin | Interface d'administration |

## Licence

Ce projet est sous licence MIT.

## Auteur

Freddy Choudja - 2026