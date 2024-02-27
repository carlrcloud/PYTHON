# print the first 50 number and append them in a list.

numbers =[]
for n in range(100):
    if n%2 !=0:
        numbers.append(n)
contains = len(numbers)             
print(f"this list contais the first {contains} odd numbers: {numbers}")

