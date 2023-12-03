import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Création du widget central et du layout
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Création des composants
        self.label_info = QLabel("Température en degrés Celsius:", self)
        self.edit_temperature = QLineEdit(self)
        self.button_convertir = QPushButton("Convertir", self)
        self.combo_conversion = QComboBox(self)
        self.label_resultat = QLabel("", self)
        self.button_information = QPushButton("Information", self)

        # Ajout des options de conversion au menu déroulant
        self.combo_conversion.addItem("Celsius vers Kelvin")
        self.combo_conversion.addItem("Kelvin vers Celsius")

        # Ajout des composants au layout
        layout.addWidget(self.label_info)
        layout.addWidget(self.edit_temperature)
        layout.addWidget(self.combo_conversion)
        layout.addWidget(self.button_convertir)
        layout.addWidget(self.label_resultat)
        layout.addWidget(self.button_information)

        # Connexion des signaux aux méthodes correspondantes
        self.button_convertir.clicked.connect(self.__convertir_temperature)
        self.button_information.clicked.connect(self.__afficher_information)

        # Réglage de la taille de la fenêtre
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle("Exercice 2 : Conversion de température")

    def __convertir_temperature(self):
        try:
            temperature = float(self.edit_temperature.text())
            conversion_type = self.combo_conversion.currentText()

            if conversion_type == "Celsius vers Kelvin":
                resultat = temperature + 273.15
            else:
                resultat = temperature - 273.15

            self.label_resultat.setText(f"Résultat de la conversion : {resultat:.2f}")
        except ValueError:
            self.label_resultat.setText("Veuillez entrer une température valide.")

    def __afficher_information(self):
        message = "Ce programme permet de convertir la température entre Celsius et Kelvin.\n\n" \
                  "- Pour la conversion de Celsius vers Kelvin, ajoutez 273.15.\n" \
                  "- Pour la conversion de Kelvin vers Celsius, soustrayez 273.15."
        QMessageBox.information(self, "Information", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
