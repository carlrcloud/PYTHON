"""
This program will ask a user for a number. than check if the number is EVEN or ODD.
The number should be between 1-100.
"""

# ask for the number 

number = int(input(f"please enter a number between 1-100.\n"))
# check if the number in [1,100]
if type(number) == int and number <= 100:
    print("Your number is valid.")
    modulo = number%2
    # print(f"{modulo}")
    if modulo == 0:
        print(f"The number {number} is an EVEN number.")
    else:
        print(f"The number {number} is an ODD number.")
else:
    print(f"The number {number} is not a valid number.\nplease enter valid number.")