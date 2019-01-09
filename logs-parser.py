#3cx call log parse and write to gsheet
#V 0.6
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import datetime
import time

#refresh timer in seconds
refresh=10
#log filename
logfile='/var/lib/3cxpbx/Instance1/Data/Logs/3CXDialer.log'
#google sheet name, please type your :)
gsheetname='Call Logs'
#last call counter
last_call=0
#last update timestamp, workaround to the 100 calls/100 sec sliding windows limitation
last_update=datetime.datetime.now()

def sheet_write(values='',update=False):
    global last_update
    # use credentials in json to create a client to interact with the Google Sheet
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    # Find a workbook by name and open the first sheet
    sheet = client.open(gsheetname).sheet1
    
    #workaround for the api usage quotas
    while (datetime.datetime.now()-last_update).seconds <1:
        time.sleep(0.2)

    if update:
        #write to google sheet the new values
        sheet.insert_row(values.split(';'),2)
        print('Last update:',datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),values.split(';'))
        last_update=datetime.datetime.now()
        
    
    if not update:
       #write just the updated timestamp
       sheet.update_acell('F1','Last update:'+datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
       print('Last update:'+datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
       last_update=datetime.datetime.now()


def match_call(newline):
    global last_call
    call_num=0
    date=time=caller=called=""
    Sheet_Buffer=""
    #this matches an extension in the format 2xx, if you have another exensions numbering, please modify
    #the following part of the regex according to your needs: DN=[2][0-9]{2}.+ and put inside the regex below
    matches=re.findall(r'[0-9]{2}\/[0-9]{2}\/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.+\[\bDialing\].+DN=[2][0-9]{2}.+',newline)

    for line in matches:
        Result_Callnum=re.search(r'Call\(([\d]+)\)',line)
        Result_Date=re.search(r'[0-9]{2}\/[0-9]{2}\/[0-9]{2}',line)
        Result_Time=re.search(r'[0-9]{2}:[0-9]{2}:[0-9]{2}',line)
        Result_Caller=re.search(r'DN=([\d]+)',line)
        Result_Called=re.search(r'EP=([\d]+)',line)

        #check for each text match:
        if Result_Callnum and Result_Date and Result_Time and Result_Caller and Result_Called:
            call_num=int(Result_Callnum.group(1))
            date=Result_Date.group(0)
            date=date[-2:]+date[2:-2]+date[0:2]
            time=Result_Time.group(0)
            caller=Result_Caller.group(1)
            called=Result_Called.group(1)

            #insert the data in the second row, always. The first row is the header row
            if call_num>last_call:
                last_call=call_num
                sheet_write(';'.join([str(call_num),str(date),str(time),str(caller),str(called)]),True)

#open the logfile and wait for new lines
logfile_handle=open(logfile,"r")
logfile_handle.seek(0,2)
while True:
    newline = logfile_handle.readline()
    if not newline:
        sheet_write()
        time.sleep(refresh)
        continue
    else:
        match_call(newline)
