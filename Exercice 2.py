if __name__ == '__main__':
    try:
        file_name = "a.txt"
        with open(file_name, 'r') as f:
            for l in f:
                l = l.rstrip("\n\r")
                print(l)
    except FileExistsError:
        print(f"le fichier {file_name} existe deja.")
    except PermissionError:
        print(f"permission non autoriser pour le fichier {file_name}.")
    except FileNotFoundError:
        print(f"le fichier {file_name} n'existe pas.")
    except IOError:
        print(f"le fichier n'arrive pas a lire {file_name}.")