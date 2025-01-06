import boto3
from datetime import datetime, timedelta

def delete_old_unattached_volumes():
    # Initialize the EC2 client
    ec2_client = boto3.client('ec2')

    # Get all volumes
    volumes = ec2_client.describe_volumes()['Volumes']

    # Get the current date and calculate the cutoff date (30 days ago)
    cutoff_date = datetime.utcnow() - timedelta(days=30)

    for volume in volumes:
        volume_id = volume['VolumeId']
        # Check if the volume is unattached and is older than 30 days
        if not volume['Attachments']:  # Unattached
            # Parse the volume's creation time
            creation_time = volume['CreateTime']
            if creation_time < cutoff_date:
                try:
                    # Delete the volume
                    print(f"Deleting volume {volume_id} created on {creation_time}")
                    ec2_client.delete_volume(VolumeId=volume_id)
                except Exception as e:
                    print(f"Failed to delete volume {volume_id}: {e}")
            else:
                print(f"Volume {volume_id} is unattached but not older than 30 days.")
        else:
            print(f"Volume {volume_id} is still attached.")

if __name__ == "__main__":
    delete_old_unattached_volumes()
