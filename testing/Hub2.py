import boto3
import csv
import datetime
import os

def fetch_filtered_findings(region, max_pages=5):
    """Fetch critical, high, medium severity findings with compliance status = FAILED."""
    securityhub = boto3.client('securityhub', region_name=region)
    findings = []

    # Filter for severity and compliance status = FAILED
    filters = {
        "SeverityLabel": [
            {"Value": "CRITICAL", "Comparison": "EQUALS"},
            {"Value": "HIGH", "Comparison": "EQUALS"},
            {"Value": "MEDIUM", "Comparison": "EQUALS"}
        ],
        "ComplianceStatus": [
            {"Value": "FAILED", "Comparison": "EQUALS"}
        ]
    }

    # Use paginator for large results
    paginator = securityhub.get_paginator('get_findings')
    page_iterator = paginator.paginate(Filters=filters, PaginationConfig={"MaxItems": max_pages * 1000})

    pages_fetched = 0
    for page in page_iterator:
        pages_fetched += 1
        print(f"Processing page {pages_fetched}...")

        for finding in page['Findings']:
            findings.append({
                'Title': finding['Title'],
                'Description': finding['Description'],
                'Severity': finding['Severity']['Label'],
                'ComplianceStatus': finding['Compliance']['Status'] if 'Compliance' in finding else 'N/A',
                'ResourceType': finding['Resources'][0]['Type'] if finding['Resources'] else 'Unknown',
                'ResourceId': finding['Resources'][0]['Id'] if finding['Resources'] else 'Unknown',
                'UpdatedAt': finding['UpdatedAt'],
                'Remediation': finding.get('Remediation', {}).get('Recommendation', {}).get('Text', 'N/A'),
            })

        if pages_fetched >= max_pages:
            print(f"Reached the max page limit: {max_pages}")
            break

    return findings

def save_grouped_findings(findings, output_folder):
    """Save findings grouped by resource type into separate CSV files."""
    grouped_findings = {}

    # Group findings by resource type
    for finding in findings:
        resource_type = finding['ResourceType']
        if resource_type not in grouped_findings:
            grouped_findings[resource_type] = []
        grouped_findings[resource_type].append(finding)

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Save each group to its own CSV file
    for resource_type, items in grouped_findings.items():
        filename = f"{output_folder}/{resource_type.replace('::', '_')}.csv"
        headers = ['Title', 'Description', 'Severity', 'ComplianceStatus', 'ResourceType', 'ResourceId', 'UpdatedAt', 'Remediation']
        
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(items)
        print(f"Saved {len(items)} findings to: {filename}")

def main():
    region = 'us-east-1'
    max_pages = 5  # Set your max pages here
    output_folder = f"security_hub_findings_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

    print(f"Fetching Security Hub findings (Critical, High, Medium) with ComplianceStatus=FAILED for region: {region}")
    findings = fetch_filtered_findings(region, max_pages=max_pages)

    if findings:
        print(f"Total findings fetched: {len(findings)}")
        save_grouped_findings(findings, output_folder)
        print(f"Findings grouped by resource type and saved in folder: {output_folder}")
    else:
        print("No findings with compliance status FAILED found.")

if __name__ == "__main__":
    main()
