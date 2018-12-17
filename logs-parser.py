#3cx call log parse and write to gsheet
#V4
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import datetime
import time

#refresh timer in seconds
refresh=10
#log filename
logfile='/var/lib/3cxpbx/Instance1/Data/Logs/3CXDialer.log'
#ghoogle sheet name, please type your :)
gsheetname='Call Logs'


#last call counter
last_call=0

def sheet_write(values='',update=True):
    #call_num,date,time,caller,called
    # use credentials in json to create a client to interact with the Google Sheet
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    # Find a workbook by name and open the first sheet
    sheet = client.open(gsheetname).sheet1
    
    if not update:
        #write to google sheet the new values
        sheet.insert_row(values.split(';'),2)
        print('Last update:',now_time.strftime("%d/%m/%Y %H:%M:%S"),values.split(';'))
    
    if update:
       #write just the updated timestamp
       sheet.update_acell('F1','Last update:'+now_time.strftime("%d/%m/%Y %H:%M:%S"))
       print('Last update:'+now_time.strftime("%d/%m/%Y %H:%M:%S"))

def match_call(newline):
    global last_call
    call_num=0
    date=time=caller=called=""
    
    #this matches an extension in the format 2xx, if you have another exensions numbering, please modify
    #the following part of the regex according to your needs: DN=[2][0-9]{2}.+ and put inside the regex below
    matches=re.findall(r'[1-9]{2}\/[1-9]{2}\/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.+\[\bDialing\].+DN=[2][0-9]{2}.+',newline)
    for line in matches:
        call_num=int(re.search(r'Call\(([\d]+)\)',line).group(1))
        date=re.search(r'[1-9]{2}\/[1-9]{2}\/[0-9]{2}',line).group(0)
        date=date[-2:]+date[2:-2]+date[0:2]
        time=re.search(r'[0-9]{2}:[0-9]{2}:[0-9]{2}',line).group(0)
        caller=re.search(r'DN=([\d]+)',line).group(1)
        called=re.search(r'EP=([\d]+)',line).group(1)
        #insert the data in the second row, always. The first row is the header row
        if call_num>last_call:
            last_call=call_num
            sheet_write(';'.join([str(call_num),str(date),str(time),str(caller),str(called)]),False)



logfile_handle=open(logfile,"r")
logfile_handle.seek(0,2)

while True:
    newline = logfile_handle.readline()

    if not newline:
        now_time=datetime.datetime.now()
        sheet_write()
        time.sleep(refresh)
        continue
    match_call(newline)


