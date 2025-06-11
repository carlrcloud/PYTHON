import boto3

ec2 = boto3.client("ec2")
OWNED_BY = "309956199498"  # Red Hat official account

def extract_minor_version(name):
    # Example: RHEL-9.6.0_HVM-... → return 6
    prefix = name.split("_")[0]  # 'RHEL-9.6.0'
    return int(prefix.split("-")[1].split(".")[1])

def lambda_handler(event, context):
    print("🔍 Fetching RHEL 9 AMIs...")
    response = ec2.describe_images(
        Owners=[OWNED_BY],
        Filters=[
            {"Name": "name", "Values": ["RHEL-9.*_HVM-*x86_64*GP3"]},
            {"Name": "state", "Values": ["available"]}
        ]
    )

    images = response["Images"]
    print(f"📦 Total AMIs fetched: {len(images)}")

    # Step 1: Find the highest minor version
    highest_minor = -1
    candidates = []

    for img in images:
        name = img.get("Name", "")
        minor = extract_minor_version(name)

        if minor > highest_minor:
            highest_minor = minor
            candidates = [img]  # start fresh
        elif minor == highest_minor:
            candidates.append(img)

    print(f"🔢 Highest minor version: {highest_minor}")
    print(f"📋 AMIs with minor version {highest_minor}: {len(candidates)}")

    # Step 2: Among candidates, find the latest by CreationDate
    candidates.sort(key=lambda x: x["CreationDate"], reverse=True)
    latest = candidates[0]

    print(f"✅ Latest AMI: {latest['ImageId']} - {latest['Name']}")
    return {
        "ImageId": latest["ImageId"],
        "Name": latest["Name"],
        "MinorVersion": highest_minor
    }
