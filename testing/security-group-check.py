import boto3
import csv

def check_security_groups():
    # Create AWS client sessions
    ec2_client = boto3.client('ec2')
    security_groups = ec2_client.describe_security_groups()["SecurityGroups"]
    instances = ec2_client.describe_instances()
    
    # Fetch instance to security group mapping
    instance_sg_map = {}
    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            for sg in instance["SecurityGroups"]:
                sg_id = sg["GroupId"]
                if sg_id not in instance_sg_map:
                    instance_sg_map[sg_id] = []
                instance_sg_map[sg_id].append(instance_id)
    
    # Analyze security groups
    sg_report = []
    for sg in security_groups:
        sg_id = sg["GroupId"]
        sg_name = sg["GroupName"]
        for permission in sg["IpPermissions"]:
            for ip_range in permission.get("IpRanges", []):
                if ip_range["CidrIp"] == "0.0.0.0/0":
                    # Security Group is open to the world
                    attached_instances = instance_sg_map.get(sg_id, [])
                    sg_report.append({
                        "SecurityGroupId": sg_id,
                        "SecurityGroupName": sg_name,
                        "OpenToWorld": True,
                        "AttachedInstances": ", ".join(attached_instances) if attached_instances else "None",
                    })
    
    return sg_report

def write_to_csv(data, filename="security_groups_report.csv"):
    # Define CSV file headers
    headers = ["SecurityGroupId", "SecurityGroupName", "OpenToWorld", "AttachedInstances"]
    
    # Write to CSV file
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    report = check_security_groups()
    if report:
        write_to_csv(report)
        print("Report has been saved to 'security_groups_report.csv'")
    else:
        print("No security groups found open to 0.0.0.0/0.")
