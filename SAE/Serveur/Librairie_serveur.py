import subprocess
import sys

def install_package(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

def install_dependencies():
    # Socket
    install_package('socket')

    # Threading
    install_package('threading')

    # MySQL Connector
    install_package('mysql-connector-python')

    # Regular Expressions
    install_package('re')

    # Datetime
    install_package('datetime')

    # Logging
    install_package('logging')

    # JSON
    install_package('json')

    # Time
    install_package('time')

if __name__ == "__main__":
    install_dependencies()
    print("Dépendances installées avec succès.")
