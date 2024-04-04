import boto3
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def sns_topic_ec2_generator():
    #define the  sns client
    sns_client = boto3.client('sns')
    # call the create method
    response = sns_client.create_topic(Name=topic_name)
    topic_arn = response['TopicArn']

    response2 = sns_client.subscribe(
    TopicArn=topic_arn,
    Protocol='email',
    Endpoint='yontacarlos1958@gmail.com' #email_adress
)
    # email_adresses = ['yontacarlos1958@gmail.com', 'yontacarlos@yahoo.fr']

if __name__ == '__main__':
    topic_name = "ec2__generator_topic"
    sns_topic_ec2_generator()

