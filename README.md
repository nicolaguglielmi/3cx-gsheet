# 3cx-gsheet
### 3cx call logs to google sheet

This is a small python script that parse the 3cx main call logfile and write some data of dialed calls to a google sheet file.
This is a workaroud to give users access to the 3cx call log without give high level access to the dashboard.

To make it working you need a few steps:
  - Create the access to gsheet through the API
  - Install the dependencies in python3
  - Configure the script parameters to your needs
  - run it, at your own risk, it's an early write :)
  
### Google sheet access

1. Open the Google API Console and create a new project, you can use this shortcut: https://console.cloud.google.com/apis/api/sheets.googleapis.com
2. Enable the API for that project
3. Create a credential set, select web server, application data
5. Grant the service account the "Editor" level in Project Role menu
6. Download the JSON file
7. Put it in the same folder of the script and name it client_secret.json
8. don't forget: *open the JSON, find the "client_email" and note it. Open the google sheet you wish to update and share to this email account with write permission*


### Python libs

The script is for python3, the libs that you need are:
1. gspread
2. oauth2client

Install the required libs with:
```
pip3 install gspread oauth2client
```

### Script configuration

The only mandatory mods that you have to do is the name of the google sheet inside the script:
```python
#ghoogle sheet name, please type your :)
gsheetname='Your gsheet name'
```
if you need you can change the extensions matching regex to fit your extension setup, 
the script is ready to use for 3 digits extensions starting with a 2, eg:200, 201 etc...


### Run

Start the script with:
```
python3 log_parser.py
```

Start and leave in background after the console logout:
```
nohup python3 log_parser.py &
```
