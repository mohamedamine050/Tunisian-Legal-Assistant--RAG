# 🏛️ Tunisian Legal Assistant - RAG

Un assistant juridique intelligent utilisant la technologie RAG (Retrieval-Augmented Generation) pour fournir des conseils juridiques basés sur la législation tunisienne.

## 📋 Table des matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Technologies utilisées](#technologies-utilisées)
- [Base de données juridique](#base-de-données-juridique)
- [API Documentation](#api-documentation)
- [Contribution](#contribution)
- [Licence](#licence)

## 🎯 Aperçu

Le **Tunisian Legal Assistant** est une application web intelligente qui combine l'intelligence artificielle avec une base de données complète de la législation tunisienne. Utilisant la technologie RAG (Retrieval-Augmented Generation), l'assistant peut répondre aux questions juridiques en se basant sur :

- Les codes juridiques tunisiens
- La constitution tunisienne
- Les lois et réglementations en vigueur

## ✨ Fonctionnalités

### 🤖 Assistant IA Juridique
- Réponses contextuelles basées sur la législation tunisienne
- Recherche sémantique dans la base de données juridique
- Citations des sources légales pertinentes
- Interface conversationnelle intuitive

### 📚 Base de données complète
- **50+ codes juridiques tunisiens** couvrant tous les domaines du droit
- **Constitution tunisienne** avec tous ses articles
- Versions traduites en anglais disponibles
- Mise à jour régulière du contenu juridique

### 🌐 Interface utilisateur moderne
- Interface React responsive
- Design Material-UI élégant
- Chat en temps réel
- Authentification des utilisateurs

### 🔧 API RESTful
- Documentation Swagger intégrée
- Endpoints sécurisés
- Support CORS pour les applications web
- Gestion des erreurs robuste

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   RAG System    │
│   (React)       │◄──►│   (Node.js)     │◄──►│   (FastAPI)     │
│                 │    │                 │    │                 │
│ • Material-UI   │    │ • Express.js    │    │ • FAISS         │
│ • Axios         │    │ • PostgreSQL    │    │ • Google AI     │
│ • Chat UI       │    │ • Passport.js   │    │ • Vector DB     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Installation

### Prérequis
- **Node.js** (v16 ou supérieur)
- **Python** (3.8 ou supérieur)
- **PostgreSQL** (pour la gestion des utilisateurs)
- **Git**

### 1. Cloner le repository

```bash
git clone https://github.com/mohamedamine050/Tunisian-Legal-Assistant--RAG.git
cd Tunisian-Legal-Assistant--RAG
```

### 2. Installation automatique

#### Windows
```batch
# Lancer le script d'installation
start_legallytn.bat
```

#### Installation manuelle

##### Backend (Node.js)
```bash
cd Full-App
npm install

cd server
npm install
```

##### Frontend (React)
```bash
cd Full-App/client
npm install
```

##### RAG System (Python)
```bash
cd RAG

# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# ou source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration

#### Variables d'environnement

Créer un fichier `.env` dans `Full-App/server/` :

```env
# Base de données
DATABASE_URL=postgresql://username:password@localhost:5432/legallytn_db

# Session
SESSION_SECRET=your_super_secret_session_key

# Google AI (pour le RAG)
GOOGLE_AI_API_KEY=your_google_ai_api_key

# Port
PORT=3001
```

#### Configuration de la base de données

1. Créer une base de données PostgreSQL
2. Importer le schéma (voir `Full-App/config/db.js`)

## 💻 Utilisation

### Démarrage rapide

1. **Démarrer le système RAG** :
```bash
cd RAG
start_rag.bat
```

2. **Démarrer le backend** :
```bash
cd Full-App/server
npm start
```

3. **Démarrer le frontend** :
```bash
cd Full-App/client
npm start
```

### Accès à l'application

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:3001
- **RAG System** : http://localhost:8000
- **API Documentation** : http://localhost:3001/api-docs

## 📁 Structure du projet

```
Tunisian-Legal-Assistant-RAG/
├── 📁 Full-App/                    # Application web complète
│   ├── 📁 client/                  # Frontend React
│   │   ├── 📁 src/
│   │   │   ├── App.js             # Composant principal
│   │   │   ├── App.css            # Styles
│   │   │   └── ...
│   │   ├── 📁 public/             # Assets publics
│   │   └── package.json           # Dépendances React
│   │
│   ├── 📁 server/                  # Backend Node.js
│   │   ├── server.js              # Serveur principal
│   │   ├── 📁 config/             # Configuration DB & Auth
│   │   ├── 📁 controllers/        # Logique métier
│   │   ├── 📁 middlewares/        # Middlewares Express
│   │   ├── 📁 models/             # Modèles de données
│   │   ├── 📁 routes/             # Routes API
│   │   └── swagger.js             # Documentation API
│   │
│   └── package.json               # Dépendances globales
│
├── 📁 RAG/                        # Système RAG (Python)
│   ├── 📁 app/
│   │   ├── main.py                # API FastAPI
│   │   ├── rag.py                 # Logique RAG
│   │   └── models.py              # Modèles Pydantic
│   │
│   ├── 📁 Data Base/              # Base de données juridique
│   │   ├── 📁 code-travail/       # Code du travail
│   │   ├── 📁 code-penal/         # Code pénal
│   │   ├── 📁 code-commerce/      # Code de commerce
│   │   ├── 📁 tunisian_constitution_articles/
│   │   └── ... (50+ codes juridiques)
│   │
│   ├── requirements.txt           # Dépendances Python
│   ├── setup_venv.py             # Script de setup
│   └── mangodb_fill.py           # Peuplement base vectorielle
│
├── 📄 README.md                   # Ce fichier
├── 📄 .gitignore                  # Fichiers ignorés par Git
└── 📜 start_legallytn.bat        # Script de démarrage Windows
```

## 🛠️ Technologies utilisées

### Frontend
- **React.js** - Bibliothèque UI
- **Material-UI** - Composants UI modernes
- **Axios** - Client HTTP
- **CSS3** - Styles

### Backend
- **Node.js** - Environnement d'exécution
- **Express.js** - Framework web
- **PostgreSQL** - Base de données relationnelle
- **Passport.js** - Authentification
- **Swagger** - Documentation API

### RAG System
- **FastAPI** - Framework Python moderne
- **FAISS** - Recherche vectorielle
- **Google Generative AI** - Modèle de langage
- **Sentence Transformers** - Embeddings
- **Uvicorn** - Serveur ASGI

### DevOps & Tools
- **Git** - Contrôle de version
- **npm** - Gestionnaire de packages Node.js
- **pip** - Gestionnaire de packages Python

## 📚 Base de données juridique

Notre système contient une base de données complète de la législation tunisienne :

### Codes juridiques inclus (50+)
- 📋 **Code du travail** - Relations employeur/employé
- ⚖️ **Code pénal** - Infractions et sanctions
- 💼 **Code de commerce** - Droit des affaires
- 🏛️ **Constitution tunisienne** - Loi fondamentale
- 🏠 **Code des obligations et contrats** - Droit civil
- 🌊 **Code des eaux** - Ressources hydriques
- ✈️ **Code de l'aéronautique civile** - Aviation
- 🚢 **Code maritime** - Droit maritime
- 🏗️ **Code de l'urbanisme** - Aménagement territoire
- 💰 **Codes fiscaux** - Taxation et impôts
- 🎬 **Code du cinéma** - Industries culturelles
- ⛏️ **Code minier** - Ressources minières
- 🌳 **Code forestier** - Protection environnementale
- 📺 **Code des télécommunications** - Secteur télécom
- 📮 **Code postal** - Services postaux
- Et bien d'autres...

### Fonctionnalités de recherche
- **Recherche sémantique** dans tous les codes
- **Citations exactes** des articles de loi
- **Traductions anglaises** disponibles
- **Recherche par domaine** juridique

## 📖 API Documentation

### Endpoints principaux

#### RAG System (FastAPI)
```http
POST /query
Content-Type: application/json

{
  "query": "Quels sont les droits du salarié en cas de licenciement ?",
  "max_results": 5
}
```

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
