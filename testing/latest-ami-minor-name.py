import boto3
import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SSM_PARAMETER_NAME = "/cfpb/test/rhel9/latest-ami-id"
OWNED_BY = "309956199498"

ec2 = boto3.client("ec2")
ssm = boto3.client("ssm")

def extract_minor_version(name):
    # Expected format: RHEL-9.X.0_HVM...
    try:
        version_part = name.split("_")[0]  # RHEL-9.X.0
        minor_version = int(version_part.split("-")[1].split(".")[1])
        return minor_version
    except (IndexError, ValueError):
        return -1  # invalid format

def lambda_handler(event, context):
    try:
        logger.info("Fetching RHEL 9 AMIs...")
        response = ec2.describe_images(
            Owners=[OWNED_BY],
            Filters=[
                {"Name": "name", "Values": ["RHEL-9.*_HVM-*x86_64*GP3"]},
                {"Name": "state", "Values": ["available"]}
            ]
        )

        images = response["Images"]
        logger.info(f"Found {len(images)} images.")

        # Extract minor version for sorting
        versioned_images = []
        for img in images:
            name = img.get("Name", "")
            minor = extract_minor_version(name)
            if minor >= 0:
                versioned_images.append((minor, img["CreationDate"], img))

        if not versioned_images:
            raise Exception("No valid RHEL-9.X.0 AMIs found.")

        # Sort by minor version, then creation date
        versioned_images.sort(key=lambda x: (x[0], x[1]), reverse=True)
        latest_ami = versioned_images[0][2]
        latest_ami_id = latest_ami["ImageId"]
        latest_ami_name = latest_ami["Name"]

        logger.info(f"Latest RHEL AMI: {latest_ami_id} - {latest_ami_name}")

        # Check current value in SSM
        try:
            current = ssm.get_parameter(Name=SSM_PARAMETER_NAME)
            current_ami_id = current["Parameter"]["Value"]
        except ssm.exceptions.ParameterNotFound:
            current_ami_id = None

        if current_ami_id != latest_ami_id:
            ssm.put_parameter(
                Name=SSM_PARAMETER_NAME,
                Value=latest_ami_id,
                Type="String",
                Overwrite=True,
                Description=f"Updated on {datetime.datetime.utcnow().isoformat()} UTC"
            )
            logger.info("✅ SSM updated.")
        else:
            logger.info("ℹ️  SSM already up to date.")

        return {
            "LatestAmiId": latest_ami_id,
            "Name": latest_ami_name
        }

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise
