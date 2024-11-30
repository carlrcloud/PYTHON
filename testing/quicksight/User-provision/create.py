import boto3
import json
import os

quicksight = boto3.client('quicksight')


def create_group(account_id, group_name, description):
    try:
        quicksight.create_group(
            AwsAccountId=account_id,
            Namespace='default',
            GroupName=group_name,
            Description=description
        )
        print(f"Created group: {group_name}")
    except quicksight.exceptions.ResourceExistsException:
        print(f"Group {group_name} already exists.")
    except Exception as e:
        print(f"Error creating group {group_name}: {e}")


def add_user_to_group(account_id, group_name, username):
    try:
        quicksight.create_group_membership(
            AwsAccountId=account_id,
            Namespace='default',
            GroupName=group_name,
            MemberName=username
        )
        print(f"Added user {username} to group {group_name}")
    except quicksight.exceptions.ResourceExistsException:
        print(f"User {username} is already in group {group_name}.")
    except Exception as e:
        print(f"Error adding user {username} to group {group_name}: {e}")


def lambda_handler(event, context):
    # Extract account ID from the event
    account_id = event.get('account_id')
    if not account_id:
        raise ValueError("Account ID is required in the event payload.")

    # Extract groups and users from the environment variable
    data = json.loads(os.environ['USERS_AND_GROUPS'])

    # Process groups
    for group in data['groups']:
        create_group(account_id, group['name'], group['description'])

    # Process users
    for user in data['users']:
        add_user_to_group(account_id, user['group'], user['username'])

    return {"statusCode": 200, "body": "Groups and users processed successfully"}
