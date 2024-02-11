"""
Write a propython program that will ask for a user body weight in pound (lbs) and convert it in kilogram (Kg).
"""

# ask for body weight to the user in pound

weight_in_pounds = float(input("What is your weight?\n"))
print(f"You weight {weight_in_pounds}lbs. Now let's convert it to Kilogram.")
#conertion to Kg
weight_in_kilogram = weight_in_pounds*0.453592
# w = round(weight_in_kilogram, 3)
# print(f"The equivalent of your weight {weight_in_pounds}Lbs is: {w}Kg.")
print(f"The equivalent of your weight {weight_in_pounds}Lbs in kilogram is: {weight_in_kilogram:.3f}Kg.")

