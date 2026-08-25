import boto3
import json

# --------------------------------------------------
# Configuration
# --------------------------------------------------

stack_id = "arn:aws:cloudformation:us-east-1:123456789012:stack/my-stack/abc123"

TAG_KEY = "AWS_Solutions"
TAG_VALUE = "CustomStack"

region = stack_id.split(":")[3]

print("=" * 80)
print("Starting tag process")
print(f"Stack ID : {stack_id}")
print(f"Region   : {region}")
print(f"Tag      : {TAG_KEY}={TAG_VALUE}")
print("=" * 80)

cfn = boto3.client("cloudformation", region_name=region)
cloudcontrol = boto3.client("cloudcontrol", region_name=region)

paginator = cfn.get_paginator("list_stack_resources")

resource_count = 0
tagged_count = 0
skipped_count = 0
failed_count = 0

print("\nGetting resources from CloudFormation...")

for page in paginator.paginate(StackName=stack_id):

    print(
        f"Found {len(page['StackResourceSummaries'])} "
        f"resources in this page."
    )

    for resource in page["StackResourceSummaries"]:

        resource_count += 1

        resource_type = resource["ResourceType"]
        resource_id = resource.get("PhysicalResourceId")

        print("\n" + "-" * 80)
        print(f"Resource #{resource_count}")
        print(f"Logical ID  : {resource['LogicalResourceId']}")
        print(f"Type        : {resource_type}")
        print(f"Physical ID : {resource_id}")
        print(f"Status      : {resource.get('ResourceStatus')}")

        if not resource_id:
            print("SKIPPED: No PhysicalResourceId")
            skipped_count += 1
            continue

        try:
            print("Calling Cloud Control get_resource()...")

            response = cloudcontrol.get_resource(
                TypeName=resource_type,
                Identifier=resource_id
            )

            print("Cloud Control successfully returned resource.")

            properties = json.loads(
                response["ResourceDescription"]["Properties"]
            )

            print(
                "Properties returned:",
                list(properties.keys())
            )

            # Check whether Tags exists
            if "Tags" not in properties:
                print("SKIPPED: No Tags property found.")
                skipped_count += 1
                continue

            tags = properties.get("Tags") or []

            print(f"Current tags: {tags}")

            existing_tags = {
                tag["Key"]: tag["Value"]
                for tag in tags
                if isinstance(tag, dict)
                and "Key" in tag
                and "Value" in tag
            }

            if TAG_KEY in existing_tags:
                print(
                    f"SKIPPED: {TAG_KEY} already exists "
                    f"with value '{existing_tags[TAG_KEY]}'"
                )

                skipped_count += 1
                continue

            print(
                f"Adding tag: {TAG_KEY}={TAG_VALUE}"
            )

            tags.append(
                {
                    "Key": TAG_KEY,
                    "Value": TAG_VALUE
                }
            )

            patch = [
                {
                    "op": "add",
                    "path": "/Tags",
                    "value": tags
                }
            ]

            print(f"Patch document: {json.dumps(patch)}")
            print("Calling Cloud Control update_resource()...")

            update_response = cloudcontrol.update_resource(
                TypeName=resource_type,
                Identifier=resource_id,
                PatchDocument=json.dumps(patch)
            )

            print(
                "Request Token:",
                update_response["ProgressEvent"].get(
                    "RequestToken"
                )
            )

            print("TAG UPDATE SUBMITTED")

            tagged_count += 1

        except cloudcontrol.exceptions.ResourceNotFoundException as e:
            print("SKIPPED: Resource not supported/found by Cloud Control")
            print(f"Details: {e}")
            skipped_count += 1

        except Exception as e:
            print("FAILED")
            print(f"Exception Type : {type(e).__name__}")
            print(f"Exception      : {e}")
            failed_count += 1


print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80) PM
print(f"Resources found : {resource_count}")
print(f"Tag submitted   : {tagged_count}")
print(f"Skipped         : {skipped_count}")
print(f"Failed          : {failed_count}")
print("=" * 80)
