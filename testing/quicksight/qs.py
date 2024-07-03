import boto3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Initialize the QuickSight client
quicksight = boto3.client('quicksight', region_name='us-east-1')  # Specify your region

# Function to create QuickSight account subscription
def create_quicksight_subscription(aws_account_id, email_address):
    try:
        response = quicksight.create_account_subscription(
            AwsAccountId=aws_account_id,
            AccountName='carlcloudQuickSightAccount',  # Replace with your desired account name
            Edition='STANDARD',  # Change to 'STANDARD' if needed
            NotificationEmail=email_address,
            AuthenticationMethod='IAM_AND_QUICKSIGHT'  # Can be 'IAM_AND_QUICKSIGHT' or 'ACTIVE_DIRECTORY'
        )
        logger.info('QuickSight subscription successful: %s', response)
    except quicksight.exceptions.AccessDeniedException as e:
        logger.error('AccessDeniedException: %s', e)
    except Exception as e:
        logger.error('An error occurred: %s', e)

# Replace with your AWS Account ID and email address
aws_account_id = '533824384467'
email_address = 'yontacarlos1958@gmail.com'

# Create the QuickSight account subscription
create_quicksight_subscription(aws_account_id, email_address)
