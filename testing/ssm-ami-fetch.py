import boto3
import datetime

# Configurations
AMI_NAME_PREFIX = 'rhel-9-'  # Adjust this to your AMI naming pattern
SSM_PARAMETER_NAME = '/rhel9/latest-ami-id'
OWNED_BY = 'self'  # Only query your private AMIs

ec2 = boto3.client('ec2')
ssm = boto3.client('ssm')

def get_latest_private_rhel9_ami():
    response = ec2.describe_images(
        Owners=[OWNED_BY],
        Filters=[
            {'Name': 'name', 'Values': [f'{AMI_NAME_PREFIX}*']},
            {'Name': 'state', 'Values': ['available']},
        ]
    )

    images = response['Images']
    if not images:
        raise Exception("No AMIs found with the specified pattern.")

    # Sort by creation date descending
    images.sort(key=lambda x: x['CreationDate'], reverse=True)
    latest_ami = images[0]
    return latest_ami['ImageId']

def get_ssm_stored_ami_id():
    try:
        param = ssm.get_parameter(Name=SSM_PARAMETER_NAME)
        return param['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        return None

def update_ssm_parameter(new_ami_id):
    ssm.put_parameter(
        Name=SSM_PARAMETER_NAME,
        Value=new_ami_id,
        Type='String',
        Overwrite=True,
        Description=f'Latest RHEL 9 AMI ID updated on {datetime.datetime.utcnow().isoformat()} UTC'
    )

def main():
    latest_ami_id = get_latest_private_rhel9_ami()
    current_ssm_ami_id = get_ssm_stored_ami_id()

    if latest_ami_id != current_ssm_ami_id:
        print(f"Updating SSM Parameter Store: {current_ssm_ami_id} -> {latest_ami_id}")
        update_ssm_parameter(latest_ami_id)
    else:
        print("SSM already holds the latest AMI ID.")

if __name__ == "__main__":
    main()
