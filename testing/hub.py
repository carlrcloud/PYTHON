import boto3
import csv
import datetime

def fetch_filtered_findings(region):
    """Fetch critical, high, and medium severity findings from AWS Security Hub."""
    securityhub = boto3.client('securityhub', region_name=region)

    findings = []
    paginator = securityhub.get_paginator('get_findings')
    
    # Filter findings by severity
    filters = {
        "SeverityLabel": [
            {"Value": "CRITICAL", "Comparison": "EQUALS"},
            {"Value": "HIGH", "Comparison": "EQUALS"},
            {"Value": "MEDIUM", "Comparison": "EQUALS"}
        ]
    }

    page_iterator = paginator.paginate(Filters=filters)

    for page in page_iterator:
        for finding in page['Findings']:
            findings.append({
                'Title': finding['Title'],
                'Description': finding['Description'],
                'Severity': finding['Severity']['Label'],
                'ResourceType': finding['Resources'][0]['Type'] if finding['Resources'] else 'Unknown',
                'ResourceId': finding['Resources'][0]['Id'] if finding['Resources'] else 'Unknown',
                'Region': region,
                'UpdatedAt': finding['UpdatedAt'],
                'Remediation': finding.get('Remediation', {}).get('Recommendation', {}).get('Text', 'N/A'),
            })
    return findings

def save_to_csv(findings, filename):
    """Save findings to a CSV file."""
    headers = ['Title', 'Description', 'Severity', 'ResourceType', 'ResourceId', 'Region', 'UpdatedAt', 'Remediation']

    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(findings)

def main():
    regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-south-1']  # Add your AWS regions here
    all_findings = []

    # Fetch findings from all regions
    for region in regions:
        print(f"Fetching findings (Critical, High, Medium) from region: {region}")
        findings = fetch_filtered_findings(region)
        all_findings.extend(findings)

    # Save results to a CSV file
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = f"security_hub_filtered_findings_{timestamp}.csv"
    save_to_csv(all_findings, report_file)

    print(f"Filtered findings report saved to: {report_file}")
    print(f"Total findings: {len(all_findings)}")

if __name__ == "__main__":
    main()
