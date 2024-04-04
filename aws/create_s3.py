import boto3
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def create_s3_bucket(bucket_name):
    """
    Create an S3 bucket.
    let's create an aws s3 bucket in us-east-1
    """

    logger.info('Start of s3 creation')
    try:
        # Initialize S3 client
        s3_client = boto3.client('s3')

        # Create S3 bucket
        response = s3_client.create_bucket(Bucket=bucket_name)

        logging.info(f"S3 bucket {bucket_name} created successfully. Response: {response}")
        return True
    except Exception as e:
        logging.error(f"Failed to create S3 bucket {bucket_name}: {e}")
        return False

def main():

    # Bucket name
    bucket_name = 'my-python24-class-bucket-123'  
    # Create S3 bucket
    create_s3_bucket(bucket_name)
    # if create_s3_bucket(bucket_name):
    #     print(f"S3 bucket {bucket_name} created successfully!")
    # else:
    #     print(f"Failed to create S3 bucket {bucket_name}.")

if __name__ == '__main__':
    main()
