import boto3
import csv

def check_security_groups():
    # Create AWS client session
    ec2_client = boto3.client('ec2')
    
    # Fetch all security groups
    security_groups = ec2_client.describe_security_groups()["SecurityGroups"]
    
    # Fetch all EC2 instances
    instances = ec2_client.describe_instances()
    
    # Fetch instance to security group mapping
    instance_sg_map = {}
    instance_name_map = {}
    attached_sg_ids = set()
    
    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_name = next(
                (tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"), "N/A"
            )
            for sg in instance["SecurityGroups"]:
                sg_id = sg["GroupId"]
                attached_sg_ids.add(sg_id)
                if sg_id not in instance_sg_map:
                    instance_sg_map[sg_id] = []
                instance_sg_map[sg_id].append({"InstanceId": instance_id, "InstanceName": instance_name})

    # Analyze security groups
    sg_report = []
    attached_sgs = []
    unattached_sgs = []

    for sg in security_groups:
        sg_id = sg["GroupId"]
        sg_name = sg["GroupName"]
        is_attached = sg_id in attached_sg_ids

        if is_attached:
            attached_sgs.append({"SecurityGroupId": sg_id, "SecurityGroupName": sg_name})
        else:
            unattached_sgs.append({"SecurityGroupId": sg_id, "SecurityGroupName": sg_name})
        
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
                        "IsAttached": is_attached
                    })
    
    return sg_report, attached_sgs, unattached_sgs

def write_to_csv(report, attached_sgs, unattached_sgs, file_name="security_group_report.csv"):
    with open(file_name, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["SecurityGroupId", "SecurityGroupName", "OpenToWorld", "InstanceId", "InstanceName", "IsAttached"])
        
        # Write data for security groups open to the world
        for item in report:
            sg_id = item["SecurityGroupId"]
            sg_name = item["SecurityGroupName"]
            open_to_world = item["OpenToWorld"]
            is_attached = item["IsAttached"]
            attached_instances = item["AttachedInstances"]
            
            if attached_instances:
                for instance in attached_instances:
                    writer.writerow([sg_id, sg_name, open_to_world, instance["InstanceId"], instance["InstanceName"], is_attached])
            else:
                writer.writerow([sg_id, sg_name, open_to_world, "None", "None", is_attached])

    # Write attached security groups list
    with open("attached_security_groups.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["SecurityGroupId", "SecurityGroupName"])
        writer.writerows([[sg["SecurityGroupId"], sg["SecurityGroupName"]] for sg in attached_sgs])

    # Write unattached security groups list
    with open("unattached_security_groups.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["SecurityGroupId", "SecurityGroupName"])
        writer.writerows([[sg["SecurityGroupId"], sg["SecurityGroupName"]] for sg in unattached_sgs])

if __name__ == "__main__":
    report, attached_sgs, unattached_sgs = check_security_groups()
    write_to_csv(report, attached_sgs, unattached_sgs)
    print("Reports have been written to 'security_group_report.csv', 'attached_security_groups.csv', and 'unattached_security_groups.csv'")
