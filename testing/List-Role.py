import boto3
import csv
from datetime import datetime, timedelta

# Initialize IAM client
iam_client = boto3.client('iam')

def list_iam_roles():
    """
    List all IAM roles and their last activity date.
    """
    roles_data = []

    # Paginate through roles
    paginator = iam_client.get_paginator('list_roles')
    for page in paginator.paginate():
        for role in page['Roles']:
            role_name = role['RoleName']
            role_creation_date = role['CreateDate']
            last_activity_date = get_last_activity(role_name)

            roles_data.append({
                'RoleName': role_name,
                'CreationDate': role_creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                'LastActivityDate': last_activity_date
            })

    return roles_data

def get_last_activity(role_name):
    """
    Get the last activity of an IAM role by checking the service last accessed information.
    """
    try:
        response = iam_client.generate_service_last_accessed_details(
            Arn=f"arn:aws:iam::{iam_client.meta.region_name}:role/{role_name}"
        )
        job_id = response['JobId']
        
        # Wait for the job to complete
        while True:
            status_response = iam_client.get_service_last_accessed_details(JobId=job_id)
            if status_response['JobStatus'] == 'COMPLETED':
                break
        
        # Parse the details for the last accessed service
        last_activity = None
        for service in status_response['ServicesLastAccessed']:
            if 'LastAuthenticated' in service:
                last_accessed = service['LastAuthenticated']
                if not last_activity or last_accessed > last_activity:
                    last_activity = last_accessed

        return last_activity.strftime('%Y-%m-%d') if last_activity else None
    except Exception as e:
        print(f"Error fetching last activity for role {role_name}: {e}")
        return None

def categorize_roles(roles):
    """
    Categorize roles into two groups: 'carl' prefix and others,
    and then further split them based on last activity.
    """
    carl_roles = {'<1 year': [], '1-2 years': [], '>2 years': []}
    other_roles = {'<1 year': [], '1-2 years': [], '>2 years': []}
    current_date = datetime.now()

    for role in roles:
        last_activity_date = role['LastActivityDate']
        if last_activity_date:
            last_activity_date = datetime.strptime(last_activity_date, '%Y-%m-%d')
            days_since_last_activity = (current_date - last_activity_date).days

            if days_since_last_activity < 365:
                category = '<1 year'
            elif 365 <= days_since_last_activity < 730:
                category = '1-2 years'
            else:
                category = '>2 years'
        else:
            # If no activity, categorize as '>2 years'
            category = '>2 years'

        if role['RoleName'].startswith('carl'):
            carl_roles[category].append(role)
        else:
            other_roles[category].append(role)

    return carl_roles, other_roles

def save_to_csv(data, filename):
    """
    Save categorized IAM role data to a CSV file.
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['RoleName', 'CreationDate', 'LastActivityDate'])
        writer.writeheader()
        for category, roles in data.items():
            writer.writerow({'RoleName': f'=== {category} ==='})
            writer.writerows(roles)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    print("Fetching IAM roles and their last activity...")
    roles = list_iam_roles()

    print("Categorizing roles...")
    carl_roles, other_roles = categorize_roles(roles)

    print("Saving categorized roles to CSV files...")
    save_to_csv(carl_roles, 'carl_roles.csv')
    save_to_csv(other_roles, 'other_roles.csv')

    print("Process completed.")
