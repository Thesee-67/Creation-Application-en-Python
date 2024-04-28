import subprocess
import sys

def install_package(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

def install_dependencies():
    # PyQt5
    install_package('PyQt5')

    # Socket
    install_package('socket')

    # Regular Expressions
    install_package('re')

    # JSON
    install_package('json')

if __name__ == "__main__":
    install_dependencies()
    print("Dépendances installées avec succès.")
