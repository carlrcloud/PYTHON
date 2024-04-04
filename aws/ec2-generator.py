import boto3
import csv
import logging
from botocore.exceptions import ClientError

# setup loggers
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Global vars
REPORT_NAME = 'report.csv'
BUCKET_NAME = 'my-python24-class-bucket-123'
KEY = 'report.csv'

def list_ec2_instances():
    """
    Gather all EC2 from a specified region
    :param NONE: 
    :return list_of_ec2_instances: return a list
    """

    # setup the EC2 boto3 client
    ec2_client = boto3.client('ec2')

    # gather all ec2 instances
    response = ec2_client.describe_instances()

    list_of_ec2_instances = []

    # loop through all the reservations in the reponse 
    for reservation in response["Reservations"]:
        # loop through all the instances in reservation
        for instance in reservation["Instances"]:
            instance_id = instance['InstanceId']
            image_id = instance['ImageId']
            instance_type = instance['InstanceType']
            state = instance['State']['Name']
            instance_name = instance['Tags'][0]['Value']

            # adding all the values needed inside a list
            list_of_ec2_instances.append([instance_name, instance_id, image_id, instance_type, state])

    return list_of_ec2_instances

def generate_csv_report(instances):
    """
    This function will generate a report in a form of a CSV file.

    :param instances: list of instances
    :return True: if the file has been created successfully else false
    """
    # CSV header
    fieldnames = ['instance_name', 'instance_id', 'image_id', 'instance_type', 'state']
    
    try:
        with open(REPORT_NAME, 'w', newline='') as csvfile:
            csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # write header
            csvwriter.writeheader()

            # write to the csv file
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(instances)
    except FileNotFoundError as error:
        logger.error(f'file may not exist! {error}')
        return False
    return True

def upload_to_s3():
    """
    upload report to S3 bucket
    :param NONE: 
    :Return: True if file uploaded successfully else false
    """

    # set the s3 client
    s3_client = boto3.client('s3')

    try: 
        response = s3_client.upload_file(REPORT_NAME, BUCKET_NAME, KEY)
    except ClientError as e:
        logging.error(e)
        return False # STOP!
    return True

def send_sns_meassage():

    client = boto3.client('sns')
    response = client.publish(
    TopicArn="arn:aws:sns:us-east-1:533824384467:ec2__generator_topic",
    Message=f"list of EC2 in your AWS account with some keys details.\n the report can be find in the file {REPORT_NAME} ",
    Subject='EC2 report',
)


if __name__ == '__main__':

    # list of instance
    instances = list_ec2_instances()

    # generate report
    generate_csv_report(instances)
    logging.info(f'Your EC2 report {REPORT_NAME} has been generated succesfully!')

    # upload report to S3
    print(upload_to_s3())
    logging.info(f'Your EC2 report: {REPORT_NAME} has been uploaded to bucket: {BUCKET_NAME} succesfully!')

    # send the email to the customer
    send_sns_meassage()