
# let's ask the user to provide an integer.
number = int(input(f"please provide me a number between 0 and 50.\n"))
# defined some empty list to capture the differnts multiple # extra
modulo_both = []  # multple of 5 and 7
modulo_five = []  # multiple of 5
modulo_seven = []  # multiple of 7

if number <=50: 

    for n in range(number+1):
        if n%5 ==0 and n%7==0:
            modulo_both.append(n)
            print("foobar")
        elif n%5 ==0:
            modulo_five.append(n)
            print("foo")
        elif n%7 ==0:
            modulo_seven.append(n)
            print("bar")

    print(f"This list contains the multiple of 5 and 7 inferior to {number}: {modulo_both}")
    print(f"This list contains the multiple of 5 inferior to {number}: {modulo_five}")
    print(f"This list contains the multiple of 7 inferior to {number}: {modulo_seven}")

else:
    print(f"Please enter a valid number.")
