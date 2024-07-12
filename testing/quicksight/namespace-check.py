import boto3
import json
import logging
import cfnresponse
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

quicksight = boto3.client('quicksight')
iam = boto3.client('iam')

def lambda_handler(event, context):
    response_data = {}
    try:
        request_type = event['RequestType']
        aws_account_id = event['ResourceProperties']['AwsAccountId']
        namespace = event['ResourceProperties']['Namespace']
        group_name = event['ResourceProperties']['GroupName']
        users = event['ResourceProperties']['Users']
        policy_arn = event['ResourceProperties']['PolicyArn']

        if request_type == 'Create':
            def namespace_exists():
                try:
                    response = quicksight.describe_namespace(
                        AwsAccountId=aws_account_id,
                        Namespace=namespace
                    )
                    logger.info('Describe namespace response: %s', response)
                    if 'CreationStatus' in response:
                        status = response['CreationStatus']
                        logger.info('Namespace creation status: %s', status)
                        if status == 'CREATED':
                            return True
                    return False
                except quicksight.exceptions.ResourceNotFoundException as e:
                    logger.warning('Namespace not found: %s', e)
                    return False
                except Exception as e:
                    logger.error('An error occurred: %s', e)
                    cfnresponse.send(event, context, cfnresponse.FAILED, response_data, "CustomResourcePhysicalID")
                    raise e

            def create_namespace():
                try:
                    response = quicksight.create_namespace(
                        AwsAccountId=aws_account_id,
                        Namespace=namespace,
                        IdentityStore='QUICKSIGHT'
                    )
                    logger.info('Namespace creation initiated: %s', response)
                    return response.get('Arn', None)
                except quicksight.exceptions.ResourceExistsException as e:
                    logger.warning('Namespace already exists: %s', e)
                    return None
                except Exception as e:
                    logger.error('An error occurred: %s', e)
                    cfnresponse.send(event, context, cfnresponse.FAILED, response_data, "CustomResourcePhysicalID")
                    raise e

            def wait_for_namespace_creation(max_retries=20, delay=30):
                for _ in range(max_retries):
                    if namespace_exists():
                        return True
                    time.sleep(delay)
                return False

            def create_group():
                try:
                    response = quicksight.create_group(
                        GroupName=group_name,
                        AwsAccountId=aws_account_id,
                        Namespace=namespace
                    )
                    logger.info('Group creation successful: %s', response)
                    return response.get('Group', None)
                except quicksight.exceptions.ResourceExistsException as e:
                    logger.warning('Group already exists: %s', e)
                except Exception as e:
                    logger.error('An error occurred: %s', e)
                    cfnresponse.send(event, context, cfnresponse.FAILED, response_data, "CustomResourcePhysicalID")
                    raise e

            def create_user(user_name, email, role='AUTHOR'):
                try:
                    response = quicksight.register_user(
                        IdentityType='QUICKSIGHT',
                        Email=email,
                        UserRole=role,
                        AwsAccountId=aws_account_id,
                        Namespace=namespace,
                        UserName=user_name
                    )
                    logger.info('User creation successful: %s', response)
                    return response.get('User', None)
                except quicksight.exceptions.ResourceExistsException as e:
                    logger.warning('User already exists: %s', e)
                except Exception as e:
                    logger.error('An error occurred: %s', e)
                    cfnresponse.send(event, context, cfnresponse.FAILED, response_data, "CustomResourcePhysicalID")
                    raise e

            def add_user_to_group(user_name):
                try:
                    response = quicksight.create_group_membership(
                        MemberName=user_name,
                        GroupName=group_name,
                        AwsAccountId=aws_account_id,
                        Namespace=namespace
                    )
                    logger.info('Added user to group: %s', response)
                except Exception as e:
                    logger.error('An error occurred: %s', e)
                    cfnresponse.send(event, context, cfnresponse.FAILED, response_data, "CustomResourcePhysicalID")
                    raise e

            def create_iam_policy_assignment(user_name):
                try:
                    response = quicksight.create_iam_policy_assignment(
                        AwsAccountId=aws_account_id,
                        AssignmentName=f'{user_name}_PolicyAssignment',
                        AssignmentStatus='ENABLED',
                        PolicyArn=policy_arn,
                        Identities={
                            'USER': [user_name]
                        },
                        Namespace=namespace
                    )
                    logger.info('IAM Policy Assignment creation successful: %s', response)
                except Exception as e:
                    logger.error('An error occurred while creating IAM Policy Assignment: %s', e)
                    cfnresponse.send(event, context, cfnresponse.FAILED, response_data, "CustomResourcePhysicalID")
                    raise e

            # Create Namespace if it does not exist
            if not namespace_exists():
                create_namespace()

            # Wait for Namespace to be created
            if not wait_for_namespace_creation():
                raise Exception('Namespace is not ready after retries')

            # Create Group
            create_group()

            # Create Users, add them to the group, and create IAM policy assignments
            for user in users:
                user_info = create_user(user['user_name'], user['email'], user['role'])
                if user_info:
                    add_user_to_group(user['user_name'])
                    create_iam_policy_assignment(user['user_name'])

            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data, "CustomResourcePhysicalID")

        elif request_type in ['Update', 'Delete']:
            # Handle updates and deletes here if needed
            logger.info(f'{request_type} request received')
            # No specific update or delete logic for this example
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data, "CustomResourcePhysicalID")

    except Exception as e:
        logger.error('Error processing request: %s', str(e))
        cfnresponse.send(event, context, cfnresponse.FAILED, response_data, "CustomResourcePhysicalID")
