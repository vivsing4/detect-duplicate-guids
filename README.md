# detect-duplicate-guids
This script will help to detect duplicate UUIDs on Cisco Secure Endpoint Console

Prerequisits:
=============
1) Need AMP API credentials. (both client-id and api-key)

2) You should know the AMP Cloud region where your business account is configured. (NAM, EU or APJC)


Usage:
======
1) Unarchive the DupUUIDdetect.zip on your endpoint.

2) You will find following three files: 
DupUUIDdetect.exe, 
api_creds.txt and 
README.txt(this file)

3) Please read the 'README.txt' thoroughly.

4) Modify the 'api_creds.txt' with your AMP API credentials and AMP Cloud.
On first line, input your AMP 3rd Party API Client ID
On second line, input corresponding AMP API Key
On third line, input the AMP Cloud region: type 'NAM' or 'EU' or 'APJC'

5) Following is an example of the contents of 'api_creds.txt':
1a798d33c029a5exxxxx
3fbxxxxx-65xx-42xx-8fxx-44a918bxxxxx
NAM

6) Execute the script 'DupUUIDdetect.exe' by double-clicking on it.

7) Once the script is executed, you should see a output.txt file generated in the same folder.

8) Content on output.txt can be as follows:
a) After successful run for AMP business account having duplicate UUID:

+--------------------------------------+-----------+-----------------------------------------------------------+
|                 UUID                 | # of dup. |                       Dup. Hostname                       |
+--------------------------------------+-----------+-----------------------------------------------------------+
| 0aexxxxx-bbxx-41xx-bbxx-7590b0cxxxxx |     2     | ['ABC-Windows-Test1', 'ABC-Windows-Test2']                |
| c2axxxxx-57xx-4cxx-b0xx-c2fc7c7xxxxx |     3     | ['XYZ-Linux-Test1', 'XYZ-Linux-Test2', 'XYZ-Linux-Test3'] |
+--------------------------------------+-----------+-----------------------------------------------------------+

b) After successful run for AMP business account not having duplicate UUID:
No Duplicate UUID found in your Organisation.

c) Getting API Error:
ERROR: API Error with code 401 and reason as Unauthorized. Please re-verify the API credentials in api_creds.txt file.

d) Getting Incorrect AMP Cloud Error:
ERROR: AMP Cloud incorrect. Please Enter Correct Region for AMP Cloud: NAM/EU/APJC.

9) Based on the output.txt you can start remediation as mentioned in following article:
https://techzone.cisco.com/t5/AMP-Public-Cloud/How-to-find-Duplicate-UUID-in-my-AMP-business-organisation/ta-p/1577327
(Link is internal, will change it to external once approved)
