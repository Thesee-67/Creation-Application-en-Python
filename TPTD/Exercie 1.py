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
    flag = False
    while not flag:
        try:
            x = int(input("x: ")) 
            y = int(input("y: "))
            print(divEntier(x,y))
            flag = True
        except ValueError as err:
            print(f"Merci de renter un nombre entier: {err}")
        except RecursionError:
            print("Le calcul est infini")
    else:
        flag = True