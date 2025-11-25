import boto3
import csv
from datetime import datetime, timezone

def list_provisioned_products():
    client = boto3.client("servicecatalog")

    # This API call DOES NOT use NextPageToken
    response = client.list_provisioned_products()

    provisioned_products = []

    for prod in response.get("ProvisionedProducts", []):
        provisioned_products.append({
            "ProvisionedProductId": prod.get("Id", ""),
            "ProductId": prod.get("ProductId", ""),
            "ProvisionedProductName": prod.get("Name", ""),
            "Status": prod.get("Status", ""),
            "CreatedTime": prod.get("CreatedTime").astimezone(timezone.utc).isoformat()
                           if prod.get("CreatedTime") else ""
        })

    return provisioned_products

def save_to_csv(data, filename="service_catalog_products.csv"):
    fieldnames = ["ProvisionedProductId", "ProductId", "ProvisionedProductName", "Status", "CreatedTime"]

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"CSV file created: {filename}")


if __name__ == "__main__":
    products = list_provisioned_products()

    if products:
        save_to_csv(products)
    else:
        print("No provisioned Service Catalog products found.")
