import boto3
import re

# === Configuration ===
REGION = "us-east-1"
SSM_PARAMETER_NAME = "/rhel9/latest-ami-id"  # Change as needed
IMAGE_BUILDER_PIPELINE_NAME = "rhel9-imagebuilder-pipeline"  # Replace with your pipeline name

def parse_rhel_version(name):
    match = re.search(r"RHEL-(9)\.(\d+)\.(\d+)", name)
    if match:
        return tuple(map(int, match.groups()))
    return (0, 0, 0)

def lambda_handler(event, context):
    ec2 = boto3.client("ec2", region_name=REGION)
    ssm = boto3.client("ssm", region_name=REGION)
    imagebuilder = boto3.client("imagebuilder", region_name=REGION)

    # Step 1: Get latest AMI
    response = ec2.describe_images(
        Owners=["309956199498"],  # Red Hat AWS Account
        Filters=[
            {"Name": "name", "Values": ["RHEL-9.*_HVM-*-x86_64-*-GP3"]},
            {"Name": "architecture", "Values": ["x86_64"]},
            {"Name": "root-device-type", "Values": ["ebs"]},
            {"Name": "virtualization-type", "Values": ["hvm"]}
        ]
    )

    images = response["Images"]
    images.sort(
        key=lambda img: (parse_rhel_version(img["Name"]), img["CreationDate"]),
        reverse=True
    )

    if not images:
        print("No valid AMIs found.")
        return {"error": "No AMI found."}

    latest_ami = images[0]
    ami_id = latest_ami["ImageId"]
    ami_name = latest_ami["Name"]

    print(f"Latest AMI ID: {ami_id}, Name: {ami_name}")

    # Step 2: Store in SSM
    ssm.put_parameter(
        Name=SSM_PARAMETER_NAME,
        Value=ami_id,
        Type="String",
        Overwrite=True,
        Tier="Standard"
    )

    print(f"Stored AMI ID in SSM: {SSM_PARAMETER_NAME}")

    # Step 3: Trigger EC2 Image Builder Pipeline
    imagebuilder.start_image_pipeline_execution(
        imagePipelineName=IMAGE_BUILDER_PIPELINE_NAME
    )

    print(f"Triggered Image Builder pipeline: {IMAGE_BUILDER_PIPELINE_NAME}")

    return {
        "AMI_ID": ami_id,
        "AMI_Name": ami_name,
        "SSM": SSM_PARAMETER_NAME,
        "Pipeline": IMAGE_BUILDER_PIPELINE_NAME
    }
