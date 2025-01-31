import boto3

# AWS Clients
ec2_client = boto3.client("ec2", region_name="us-east-1")  # Change region if needed
ssm_client = boto3.client("ssm")
imagebuilder_client = boto3.client("imagebuilder")

# Constants
RHEL_OWNER_ID = "309956199498"  # Red Hat AWS account ID
RHEL_VERSION = "RHEL9*"  # Adjust as needed for specific versions
SSM_PARAM_X86 = "/custom/ami/rhel-latest-x86_64"
IMAGE_BUILDER_PIPELINE_ARN = "arn:aws:imagebuilder:us-east-1:123456789012:image-pipeline/my-image-pipeline"  # Replace with your ARN

def get_latest_ami():
    """Fetches the latest RHEL x86_64 AMI."""
    response = ec2_client.describe_images(
        Owners=[RHEL_OWNER_ID],
        Filters=[
            {"Name": "architecture", "Values": ["x86_64"]},
            {"Name": "description", "Values": [RHEL_VERSION]}
        ]
    )

    # Sort by CreationDate and get the latest
    images = sorted(response["Images"], key=lambda x: x["CreationDate"], reverse=True)
    
    if images:
        return images[0]["ImageId"]
    return None

def get_ssm_parameter(param_name):
    """Fetches the existing AMI ID from SSM Parameter Store."""
    try:
        response = ssm_client.get_parameter(Name=param_name)
        return response["Parameter"]["Value"]
    except ssm_client.exceptions.ParameterNotFound:
        return None

def update_ssm_parameter(param_name, new_ami):
    """Updates the AMI ID in SSM Parameter Store if it has changed."""
    current_ami = get_ssm_parameter(param_name)

    if current_ami != new_ami:
        print(f"Updating {param_name} with new AMI: {new_ami}")
        ssm_client.put_parameter(
            Name=param_name,
            Value=new_ami,
            Type="String",
            Overwrite=True
        )
        return True
    return False

def trigger_imagebuilder_pipeline():
    """Triggers EC2 Image Builder pipeline if a new AMI is found."""
    response = imagebuilder_client.start_image_pipeline_execution(imagePipelineArn=IMAGE_BUILDER_PIPELINE_ARN)
    print(f"Triggered EC2 Image Builder pipeline: {IMAGE_BUILDER_PIPELINE_ARN}")
    return response

def main():
    print("Fetching latest RHEL x86_64 AMI...")

    latest_ami_x86 = get_latest_ami()

    if not latest_ami_x86:
        print("No AMIs found. Exiting.")
        return

    updated_x86 = update_ssm_parameter(SSM_PARAM_X86, latest_ami_x86)

    # If AMI is updated, trigger the EC2 Image Builder pipeline
    if updated_x86:
        trigger_imagebuilder_pipeline()
    else:
        print("No changes detected. Skipping pipeline trigger.")

if __name__ == "__main__":
    main()
