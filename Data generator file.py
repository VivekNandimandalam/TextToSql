import pandas as pd
import random
 
# Function to generate random data
def generate_dummy_data(num_rows):
    data = []
    resource_types = ['VirtualMachine', 'SQLDatabase', 'StorageAccount', 'AppService', 'DataFactory', 'Firewall']
    locations = ['East US', 'West Europe', 'South Central US', 'North Europe', 'Southeast Asia']
    service_names = ['Virtual Machines', 'SQL Database', 'Storage', 'App Services', 'Data Factory', 'Networking']
    service_tiers = ['Standard', 'Premium', 'Basic']
    meters = ['Compute Hours', 'Storage Capacity', 'Pipeline Activity', 'Data Transfer']
    currencies = ['USD']
 
    for i in range(num_rows):
        resource = f"Resource{i+1:04}"
        resource_id = f"R{i+1:04}"
        resource_type = random.choice(resource_types)
        resource_group_name = f"RG-{random.choice(['Production', 'Development', 'Test'])}"
        resource_group_id = f"RG{random.randint(1, 50):03}"
        resource_location = random.choice(locations)
        subscription_name = f"{random.choice(['Prod', 'Dev', 'Test'])}-Subscription"
        subscription_id = f"S{random.randint(1, 100):03}"
        service_name = random.choice(service_names)
        service_tier = random.choice(service_tiers)
        meter = random.choice(meters)
        part_number = f"P{random.randint(1, 50):03}"
        cost = round(random.uniform(100, 5000), 2)
        cost_usd = cost
        currency = random.choice(currencies)
        data.append([resource, resource_id, resource_type, resource_group_name, resource_group_id, resource_location, 
                     subscription_name, subscription_id, service_name, service_tier, meter, part_number, cost, cost_usd, currency])
    return data
 
# Generate 1000 rows of dummy data
num_rows = 1000
dummy_data = generate_dummy_data(num_rows)
 
# Define columns
columns = ['Resource', 'ResourceId', 'ResourceType', 'ResourceGroupName', 'ResourceGroupId', 'ResourceLocation', 
           'SubscriptionName', 'SubscriptionId', 'ServiceName', 'ServiceTier', 'Meter', 'PartNumber', 'Cost', 'CostUSD', 'Currency']
 
# Create DataFrame
df = pd.DataFrame(dummy_data, columns=columns)
 
# Export to Excel
df.to_excel('dummy_cost_data.xlsx', index=False)
 
print("Excel file 'dummy_cost_data.xlsx' has been generated with 1000 rows.")