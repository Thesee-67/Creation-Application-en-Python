
def divEntier(x: int, y: int) -> int:
 if x < y:
    return 0
 else:
    x = x - y
    return divEntier(x, y) + 1
 
if __name__ == '__main__':
  print(divEntier(50,4))

