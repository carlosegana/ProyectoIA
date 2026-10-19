try:
    suma = 1 + 2
    print(suma)
except ValueError:
    print("Something went wrong")
finally:
    print("The 'try except' is finished")