"""
This program will extract a AWS account ID from a resource ARN
"""

# The reource ARN
ARN = "arn:aws:iam::123456789012:uer/Development/product_1234/*"
lenght = len(ARN)
print(f"The lentgh of the ARN is: {lenght}")

# Let's extract the account ID from this arn

account_Id = ARN[13:25]
print(f"The AWS account ID that content this resource is: {account_Id}")
