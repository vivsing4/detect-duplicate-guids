import requests
import sys
from time import sleep
from prettytable import PrettyTable

f=open("api_creds.txt","r")
fi=open("output.txt","w")
lines=f.readlines()
Third_Party_API_Client_ID = lines[0]
if Third_Party_API_Client_ID.endswith('\n'):
    Third_Party_API_Client_ID = Third_Party_API_Client_ID[:-1]
API_Key = lines[1]
if API_Key.endswith('\n'):
    API_Key = API_Key[:-1]
Cloud = lines[2]
if Cloud.endswith('\n'):
    Cloud = Cloud[:-1]
f.close()

if Cloud == "NAM" or Cloud == "nam" or Cloud == "Nam":
    cloud_base = "api.amp.cisco.com"
elif Cloud == "APJC" or Cloud == "apjc" or Cloud == "Apjc":
    cloud_base = "api.apjc.amp.cisco.com"
elif Cloud == "EU" or Cloud == "eu" or Cloud == "Eu":
    cloud_base = "api.eu.amp.cisco.com"
else:
    fi.write("ERROR: AMP Cloud incorrect. Please Enter Correct Region for AMP Cloud: NAM/EU/APJC.")
    sys.exit("Exiting...")

# Initialize parameters for pagination
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

while True:
    # Construct the URL with limit and offset parameters
    url = f"https://{Third_Party_API_Client_ID}:{API_Key}@{cloud_base}/v1/audit_logs?audit_log_type=Computer&event=update&limit={limit}&offset={offset}"

    response = requests.request("GET", url, headers=headers, data = payload, files = files)

    if response.status_code != 200:
        fi.write (f"ERROR: API Error with code {response.status_code} and reason as {response.reason}. Please re-verify the API credentials in api_creds.txt file.")
        sys.exit("Exiting...")

    jsondata = response.json()
    
    # Extract metadata for pagination
    metadata_results = jsondata.get('metadata', {}).get('results', {})
    
    # Set total_records on the first iteration
    if total_records is None:
        total_records = metadata_results.get('total', 0) # Use 0 if 'total' is unexpectedly missing
    
    current_page_data = jsondata.get('data', [])
    
    # Add current page data to the overall list
    all_audit_logs.extend(current_page_data)
    
    # Update offset for the next request using current_item_count from metadata
    offset += metadata_results.get('current_item_count', 0)

    # Break condition: if the current offset has reached or exceeded the total number of records
    # or if no data was returned (might happen if total_records was 0 or on an empty last page)
    if offset >= total_records or not current_page_data:
        break
    
    # Optional: Add a small delay to avoid hitting rate limits, if necessary
    sleep(1) 

# Now, all_audit_logs contains all the audit log entries
# The rest of your script can process this combined list

uuid_raw=[]
ohost=[]
nhost=[]
uuid= {}
ahost={}

for item in all_audit_logs: # Process the combined list of all audit logs
    for key, value in item.items():
        if key == 'old_attributes':
            # Ensure 'hostname' exists in both old_attributes and new_attributes
            if 'hostname' in item.get('old_attributes', {}) and 'hostname' in item.get('new_attributes', {}):
                uuid_raw.append(item["audit_log_id"])
                ohost.append(item["old_attributes"]["hostname"])
                nhost.append(item["new_attributes"]["hostname"])

def duplicates(lst, item):
    return [i for i, x in enumerate(lst) if x == item]

for i in uuid_raw:
    uuid[i]= duplicates(uuid_raw, i)

for i in ohost:
    if i in nhost:
        index = ohost.index(i)
        if len(uuid[uuid_raw[index]]) > 1:
            for j in uuid[uuid_raw[index]]:
                try:
                    len(ahost[uuid_raw[index]])>=1
                except KeyError:
                    ahost[uuid_raw[index]]=[]
                if ohost[j] not in ahost[uuid_raw[index]]:
                    ahost[uuid_raw[index]].append(ohost[j])
                if nhost[j] not in ahost[uuid_raw[index]]:
                    ahost[uuid_raw[index]].append(nhost[j])

flag = "turn-on"

if len(ahost) > 0:
    for uui, hos in ahost.items():
        if flag == "turn-on":
            t = PrettyTable(['UUID', '# of dup.', 'Dup. Hostname'])
        t.add_row([str(uui), str(len(hos)), str(hos)])
        flag = "turn-off"
    fi.write(str(t))
else:
    fi.write("No Duplicate UUID found in your Organisation.")

sys.exit("Exiting...")
