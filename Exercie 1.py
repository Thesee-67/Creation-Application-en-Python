
def divEntier(x: int, y: int) -> int:
 if x < y:
    return 0
 else:
    x = x - y
    return divEntier(x, y) + 1
 
if __name__ == '__main__':
    try:
         x = int(input("a: ")) 
         y = int(input("b: "))
         print(divEntier(x,y))
    except ValueError:
        print("Veuillez rentrer un nombre entier")