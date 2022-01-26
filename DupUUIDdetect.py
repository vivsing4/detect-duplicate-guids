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

url = "https://"+Third_Party_API_Client_ID+":"+API_Key+"@"+cloud_base+"/v1/audit_logs?audit_log_type=Computer&event=update"

payload = {}
files = {}
headers = {
	'Content-Type': 'application/json',
	'Accept': 'application/json'
}

response = requests.request("GET", url, headers=headers, data = payload, files = files)

if response.status_code != 200:
    fi.write ("ERROR: API Error with code "+str(response.status_code)+" and reason as "+str(response.reason)+". Please re-verify the API credentials in api_creds.txt file.")
    sys.exit("Exiting...")

raw_data = response.json()
jsondata = response.json()

uuid_raw=[]
ohost=[]
nhost=[]
uuid= {}
ahost={}

for item in jsondata['data']:
    for key, value in item.items():
        if key == 'old_attributes':
            for key1, value1 in value.items():
                if key1 == 'hostname':
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