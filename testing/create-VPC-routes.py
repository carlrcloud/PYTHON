import boto3
import os

ec2 = boto3.client("ec2")
ssm = boto3.client("ssm")


def get_ssm_parameter(name):
    response = ssm.get_parameter(
        Name=name
    )
    return response["Parameter"]["Value"]


def lambda_handler(event, context):

    # ---------------------------------------------------------
    # SSM parameter names from Lambda environment variables
    # ---------------------------------------------------------
    vpc_id_param = os.environ["VPC_ID_SSM_PARAM"]
    cidr_list_param = os.environ["CIDR_LIST_SSM_PARAM"]
    tgw_id_param = os.environ["TGW_ID_SSM_PARAM"]

    # ---------------------------------------------------------
    # Get values from SSM Parameter Store
    # ---------------------------------------------------------
    vpc_id = get_ssm_parameter(vpc_id_param)

    transit_gateway_id = get_ssm_parameter(tgw_id_param)

    cidr_string = get_ssm_parameter(cidr_list_param)

    # Convert:
    # 10.10.0.0/16,10.20.0.0/16
    #
    # Into:
    # ["10.10.0.0/16", "10.20.0.0/16"]
    destination_cidrs = [
        cidr.strip()
        for cidr in cidr_string.split(",")
        if cidr.strip()
    ]

    print(f"Main VPC: {vpc_id}")
    print(f"Transit Gateway: {transit_gateway_id}")
    print(f"Destination CIDRs: {destination_cidrs}")

    # ---------------------------------------------------------
    # Find all route tables in the Main VPC
    # ---------------------------------------------------------
    response = ec2.describe_route_tables(
        Filters=[
            {
                "Name": "vpc-id",
                "Values": [vpc_id]
            }
        ]
    )

    route_tables = response["RouteTables"]

    if not route_tables:
        raise Exception(
            f"No route tables found for VPC {vpc_id}"
        )

    print(f"Found {len(route_tables)} route table(s)")

    results = []

    # ---------------------------------------------------------
    # Create routes
    # ---------------------------------------------------------
    for route_table in route_tables:

        route_table_id = route_table["RouteTableId"]

        print(f"\nProcessing route table: {route_table_id}")

        existing_cidrs = {
            route.get("DestinationCidrBlock")
            for route in route_table.get("Routes", [])
            if route.get("DestinationCidrBlock")
        }

        for destination_cidr in destination_cidrs:

            if destination_cidr in existing_cidrs:

                print(
                    f"SKIPPED: {destination_cidr} already exists "
                    f"in {route_table_id}"
                )

                results.append({
                    "route_table": route_table_id,
                    "destination": destination_cidr,
                    "status": "already-exists"
                })

                continue

            try:

                ec2.create_route(
                    RouteTableId=route_table_id,
                    DestinationCidrBlock=destination_cidr,
                    TransitGatewayId=transit_gateway_id
                )

                print(
                    f"CREATED: {destination_cidr} -> "
                    f"{transit_gateway_id} in {route_table_id}"
                )

                results.append({
                    "route_table": route_table_id,
                    "destination": destination_cidr,
                    "status": "created"
                })

            except Exception as error:

                print(
                    f"FAILED: {destination_cidr} in "
                    f"{route_table_id}: {error}"
                )

                results.append({
                    "route_table": route_table_id,
                    "destination": destination_cidr,
                    "status": "failed",
                    "error": str(error)
                })

    return {
        "vpc_id": vpc_id,
        "transit_gateway_id": transit_gateway_id,
        "route_tables_found": len(route_tables),
        "destination_cidrs": destination_cidrs,
        "results": results
    }
