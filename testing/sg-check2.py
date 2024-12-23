import boto3
import csv

def check_security_groups():
    # Create AWS client sessions
    ec2_client = boto3.client('ec2')
    security_groups = ec2_client.describe_security_groups()["SecurityGroups"]
    instances = ec2_client.describe_instances()
    
    # Fetch instance to security group mapping
    instance_sg_map = {}
    instance_name_map = {}
    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_name = next(
                (tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"), "N/A"
            )
            for sg in instance["SecurityGroups"]:
                sg_id = sg["GroupId"]
                if sg_id not in instance_sg_map:
                    instance_sg_map[sg_id] = []
                instance_sg_map[sg_id].append({"InstanceId": instance_id, "InstanceName": instance_name})
    
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
                        "AttachedInstances": attached_instances,
                    })
    
    return sg_report

def write_to_csv(report, file_name="security_group_report.csv"):
    with open(file_name, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["SecurityGroupId", "SecurityGroupName", "OpenToWorld", "InstanceId", "InstanceName"])
        
        # Write data
        for item in report:
            sg_id = item["SecurityGroupId"]
            sg_name = item["SecurityGroupName"]
            open_to_world = item["OpenToWorld"]
            attached_instances = item["AttachedInstances"]
            
            if attached_instances:
                for instance in attached_instances:
                    writer.writerow([sg_id, sg_name, open_to_world, instance["InstanceId"], instance["InstanceName"]])
            else:
                writer.writerow([sg_id, sg_name, open_to_world, "None", "None"])

if __name__ == "__main__":
    report = check_security_groups()
    write_to_csv(report)
    print("Report has been written to 'security_group_report.csv'")
