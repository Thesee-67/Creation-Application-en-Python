def divEntier(x: int, y: int) -> int:
    if x < 0 or y < 0:
        raise ValueError("les nombres doivent être positifs")
    elif y == 0:
        raise ValueError("Y doit être différent de 0")
    else:
        if x < y:
            return 0
        else:
            x = x - y
            return divEntier(x, y) + 1

if __name__ == '__main__':
    try:
         x = int(input("x: ")) 
         y = int(input("y: "))
         print(divEntier(x,y))
    except RecursionError:
        if y == 0:
            raise ValueError("Veuiller rentre dans Y un nombre différent de 0")
    except ValueError as err:
        print(f"Merci de renter un nombre entier: {err}")
