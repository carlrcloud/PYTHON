"""
This python program will a student for their grade in 5 subjects.
calculate the  average grade and give the final result.
"""

Maths = float(input(f"What is your note score in Maths this semester?\n"))
physics = float(input(f"What is your note score in Physics this semester?\n"))
Biology = float(input(f"What is your note score in Biology this semester?\n"))
Chemestry = float(input(f"What is your note score in Chemestry this semester?\n"))
Information_Technology = float(input(f"What is your note score in Information_technology this semester?\n"))

# calculate the average

Average = (Maths+physics+Biology+Chemestry+Information_Technology)/5
result1 = "Failed"
result2 = "Passed"
if Average >= 60:
    print(f"Result: {result2}")
    if 60 <= Average < 70:
        print(f"Your final score is: {Average} and your grade is D ")
    elif 70 <= Average < 80:
        print(f"Your final score is: {Average} and your grade is C ")
    elif 80 <= Average < 90:
        print(f"Your final score is: {Average} and your grade is B ")
    else:
        print(f"Your final score is: {Average} and your grade is A ")

else:
    print(f"Result: {result1}")
    print("your grade is : E")
