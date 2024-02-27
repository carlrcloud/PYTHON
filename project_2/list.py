# This python program print the largest and the smallest values in a list.
# the nested list
list = [[3,4,5,6],[-1, -2, -3, -4],[0, 0, 0, 0],[]]

# let's loop inside our list.
for l in list:
    if l==[]:
        print("Nome")
    else:
        print(f"The largest in {l} is {max(l)} and the smallest is {min(l)}.")

