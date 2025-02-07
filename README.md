# GuiGui TChat - Messagerie Professionnelle

## 📌 Introduction
GuiGui TChat est une application de messagerie conçue pour optimiser la communication en entreprise. Elle permet aux employés de collaborer efficacement à travers des salons de discussion sécurisés.

## 🚀 Fonctionnalités
- Connexion sécurisée avec identifiant et mot de passe.
- Création et gestion des comptes utilisateurs.
- Salons de discussion (Topics) pour échanges ciblés.
- Liste des utilisateurs connectés en temps réel.
- Interface intuitive développée avec PyQt5.
- Gestion des sanctions (bannissement, kick temporaire).
- Administration centralisée des utilisateurs.

## 🛠 Installation

### 1️⃣ Configuration de la Base de Données
1. Installer **MySQL** ou **MariaDB**.
2. Exécuter les commandes SQL fournies dans `Guide SQL pour la Configuration d'une Base de Données - sae_r309.pdf`.
3. Vérifier que la base de données `GuiGuiTchat` est active.
4. S'assurer que le serveur MySQL/MariaDB est démarré.

### 2️⃣ Installation du Serveur
1. Télécharger et accéder au répertoire du serveur :
2. Suivez la Notice d'utilisation du Serveur dans : `Serveur/Notice d'utilisation Serveur Administrateur GuiGui Tchat.pdf`
   
### 3️⃣ Installation du Client
1. Télécharger et accéder au répertoire du client :
2. Suivez la Notice d'utilisation du Serveur dans : `Client/Notice D'utilisation Client GuiGui Tchat.pdf`

## 🔄 Connexion et Gestion des Comptes
- **Connexion** : Entrer identifiant et mot de passe.
- **Création de compte** : Renseigner nom, prénom, e-mail, identifiant et mot de passe.
- **Gestion des utilisateurs** : Affichage du profil et liste des membres connectés.

## 🔧 Administration du Serveur
L’administrateur dispose de plusieurs commandes pour gérer les utilisateurs et le serveur :

```sh
showdemande        # Voir les demandes de changement de topic.
accept@identifiant # Accepter un changement de topic.
refuser@identifiant # Refuser un changement de topic.
ban@identifiant    # Bannir un utilisateur.
kick@identifiant   # Expulser temporairement un utilisateur.
showban            # Voir la liste des utilisateurs bannis.
unban@identifiant  # Lever un bannissement.
showcommande       # Afficher toutes les commandes disponibles.
```

## 🔍 Développement
- **Langage** : Python 3
- **Interface** : PyQt5
- **Base de données** : MySQL/MariaDB
- **Communication réseau** : Sockets

## 📧 Support
📩 Contact : [olivier.guittet@uha.fr](mailto:olivier.guittet@uha.fr)

© 2025 GuiGui TChat - Tous droits réservés.
