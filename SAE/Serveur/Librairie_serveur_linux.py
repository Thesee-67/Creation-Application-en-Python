import subprocess
import sys

def install_package(package):
    subprocess.call(["sudo", "apt", "install", "-y", package])

def install_dependencies():
    # Socket
    install_package('python3-socket')
    # MySQL Connector
    install_package('python3-mysql-connector')
    
if __name__ == "__main__":
    install_dependencies()
    print("Dépendances installées avec succès.")
