import csv
import json

def csv_to_json(csv_file_path, json_file_path):
    # Open the CSV file
    with open(csv_file_path, mode='r') as csv_file:
        # Read the CSV data
        csv_reader = csv.DictReader(csv_file)
        
        # Convert CSV data to JSON format
        data = []
        for row in csv_reader:
            data.append(row)
        
        # Write JSON data to a file
        with open(json_file_path, mode='w') as json_file:
            json.dump(data, json_file, indent=4)

# Example usage:
csv_file = '/home/anuarrozman/FactoryApp_Dev/ATSoftwareDevelopmentTool/Test/csvtojson/exp_with_order_no.csv'
json_file = '/home/anuarrozman/FactoryApp_Dev/ATSoftwareDevelopmentTool/Test/csvtojson/output.json'

csv_to_json(csv_file, json_file)
