import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QSizePolicy
from PyQt5.QtCore import QCoreApplication

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Création du widget central et du layout
        widget = QWidget()
        self.setCentralWidget(widget)
        grid = QGridLayout()
        widget.setLayout(grid)

        # Création des composants
        lab = QLabel("Saisir votre prénom")
        self.edit_prenom = QLineEdit("")
        ok = QPushButton("OK")
        quitter = QPushButton("Quitter")

        # Ajout des composants au layout
        grid.addWidget(lab, 0, 0, 1, 2)  # Le label occupe deux colonnes
        grid.addWidget(self.edit_prenom, 1, 0, 1, 2)  # Le champ de saisie occupe deux colonnes
        grid.addWidget(ok, 2, 0)
        grid.addWidget(quitter, 2, 1)

        # Connexion des signaux aux méthodes correspondantes
        ok.clicked.connect(self.__action_ok)
        quitter.clicked.connect(self.__action_quitter)

        # Réglage de la taille de la fenêtre
        self.setGeometry(100, 100, 400, 200)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Taille fixe
        self.setWindowTitle("Exercice PyQt")

    def __action_ok(self):
        prenom = self.edit_prenom.text()
        if prenom:
            message = f'Bonjour {prenom} !'
            self.statusBar().showMessage(message)
        else:
            self.statusBar().showMessage('Veuillez entrer un prénom.')

    def __action_quitter(self):
        QCoreApplication.exit(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
