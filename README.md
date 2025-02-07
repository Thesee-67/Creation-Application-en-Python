GuiGui TChat - Messagerie Professionnelle

📌 Introduction

GuiGui TChat est une application de messagerie conçue pour optimiser la communication en entreprise. Elle permet aux employés de collaborer efficacement à travers des salons de discussion sécurisés.

🚀 Fonctionnalités

Connexion sécurisée avec identifiant et mot de passe.

Création et gestion des comptes utilisateurs.

Salons de discussion (Topics) pour échanges ciblés.

Liste des utilisateurs connectés en temps réel.

Interface intuitive développée avec PyQt5.

Gestion des sanctions (bannissement, kick temporaire).

Administration centralisée des utilisateurs.

🛠 Installation

1️⃣ Configuration de la Base de Données

Installer MySQL ou MariaDB.

Exécuter les commandes SQL fournies dans schema.sql.

Vérifier que la base de données GuiGuiTchat est active.

S'assurer que le serveur MySQL/MariaDB est démarré.

2️⃣ Installation du Serveur

Télécharger et accéder au répertoire du serveur :

cd /chemin/vers/le/serveur

Installer les dépendances :

pip install -r requirements.txt

Configurer la connexion à la base de données dans le fichier config.py.

Lancer le serveur :

python server.py

Vérifier que le serveur écoute sur le bon port et accepte les connexions clients.

3️⃣ Installation du Client

Télécharger et accéder au répertoire du client :

cd /chemin/vers/le/client

Installer les dépendances :

pip install -r requirements.txt

Lancer l'application :

python client.py

Se connecter avec les identifiants fournis.

📡 Connexion et Gestion des Comptes

Connexion : Entrer identifiant et mot de passe.

Création de compte : Renseigner nom, prénom, e-mail, identifiant et mot de passe.

Gestion des utilisateurs : Affichage du profil et liste des membres connectés.

🔄 Administration du Serveur

L’administrateur dispose de plusieurs commandes pour gérer les utilisateurs et le serveur :

showdemande : Voir les demandes de changement de topic.

accept@identifiant : Accepter un changement de topic.

refuser@identifiant : Refuser un changement de topic.

ban@identifiant : Bannir un utilisateur.

kick@identifiant : Expulser temporairement un utilisateur.

showban : Voir la liste des utilisateurs bannis.

unban@identifiant : Lever un bannissement.

showcommande : Afficher toutes les commandes disponibles.

🛠 Développement

Langage : Python 3

Interface : PyQt5

Base de données : MySQL/MariaDB

Communication réseau : Sockets

📧 Support

Contact : olivier.guittet@uha.fr

© 2025 GuiGui TChat - Tous droits réservés.
