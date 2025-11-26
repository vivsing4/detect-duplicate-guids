import requests
import sys
from time import sleep
import csv # Import the csv module

# --- File I/O for API credentials ---
try:
    with open("api_creds.txt","r") as f:
        lines = f.readlines()
        Third_Party_API_Client_ID = lines[0].strip()
        API_Key = lines[1].strip()
        Cloud = lines[2].strip()
except FileNotFoundError:
    print("ERROR: api_creds.txt not found. Please create it with Client ID, API Key, and Cloud region on separate lines.")
    sys.exit("Exiting...")
except IndexError:
    print("ERROR: api_creds.txt is improperly formatted. Ensure it has Client ID, API Key, and Cloud region on separate lines.")
    sys.exit("Exiting...")

# --- Cloud Region Configuration ---
cloud_base = ""
if Cloud.lower() == "nam":
    cloud_base = "api.amp.cisco.com"
elif Cloud.lower() == "apjc":
    cloud_base = "api.apjc.amp.cisco.com"
elif Cloud.lower() == "eu":
    cloud_base = "api.eu.amp.cisco.com"
else:
    print("ERROR: AMP Cloud incorrect. Please Enter Correct Region for AMP Cloud: NAM/EU/APJC.")
    sys.exit("Exiting...")

# --- API Request Setup ---
limit = 500  # Max limit per request as per API documentation
offset = 0
all_audit_logs = []
total_records = None # Will be set from metadata.results.total

payload = {}
files = {}
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# --- Pagination Loop to Fetch All Audit Logs ---
print("Fetching audit logs, please wait...")
while True:
    url = f"https://{Third_Party_API_Client_ID}:{API_Key}@{cloud_base}/v1/audit_logs?audit_log_type=Computer&event=update&limit={limit}&offset={offset}"

    try:
        response = requests.request("GET", url, headers=headers, data = payload, files = files)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"ERROR: API Request failed: {e}")
        sys.exit("Exiting...")

    jsondata = response.json()
    
    metadata_results = jsondata.get('metadata', {}).get('results', {})
    
    if total_records is None:
        total_records = metadata_results.get('total', 0)
        print(f"Total audit logs to process: {total_records}")
    
    current_page_data = jsondata.get('data', [])
    
    all_audit_logs.extend(current_page_data)
    
    offset += metadata_results.get('current_item_count', 0)
    print(f"Fetched {len(all_audit_logs)} of {total_records} logs...")

    if offset >= total_records or not current_page_data:
        break
    
    sleep(1) # Small delay to avoid hitting rate limits

# --- Process Audit Logs for Duplicates ---
print("Processing audit logs to find duplicate UUIDs...")
uuid_raw=[] # List of audit_log_ids in order of appearance
ohost=[]    # List of old hostnames in order of appearance
nhost=[]    # List of new hostnames in order of appearance
uuid_indices = {} # Maps audit_log_id to a list of indices where it appears in uuid_raw

for item in all_audit_logs:
    old_attrs = item.get('old_attributes', {})
    new_attrs = item.get('new_attributes', {})
    
    if 'hostname' in old_attrs and 'hostname' in new_attrs:
        audit_log_id = item.get("audit_log_id")
        if audit_log_id:
            uuid_raw.append(audit_log_id)
            ohost.append(old_attrs["hostname"])
            nhost.append(new_attrs["hostname"])

            # Populate uuid_indices for quick lookup of all entries for a given UUID
            if audit_log_id not in uuid_indices:
                uuid_indices[audit_log_id] = []
            uuid_indices[audit_log_id].append(len(uuid_raw) - 1) # Store the index

ahost = {} # Stores UUID: set of unique hostnames involved in its duplicate entries

for uui, indices in uuid_indices.items():
    if len(indices) > 1: # This UUID has multiple audit log entries
        ahost[uui] = set() # Use a set to store unique hostnames for this UUID
        for idx in indices:
            ahost[uui].add(ohost[idx])
            ahost[uui].add(nhost[idx])

# Convert sets back to sorted lists for consistent output
for uui in ahost:
    ahost[uui] = sorted(list(ahost[uui]))


# --- Generate CSV Output ---
if len(ahost) > 0:
    output_filename = "output.csv"
    with open(output_filename, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Write header row as per the example
        csv_writer.writerow(['UUID', 'No. of dup.', 'Duplicates'])
        
        # Write data rows
        for uui, hos in ahost.items():
            # The row should be [UUID, count] + [hostname1, hostname2, ...]
            row_data = [str(uui), str(len(hos))] + hos
            csv_writer.writerow(row_data)
    print(f"Output successfully written to {output_filename}")
else:
    print("No Duplicate UUID found in your Organisation.")

sys.exit("Exiting...")
