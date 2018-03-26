import datetime
import csv
import myfitnesspal
from pprint import pprint
#import sqlite3
import json
import os.path

client = myfitnesspal.Client('mail@luka.ge')
dateFrom = datetime.date.today() - datetime.timedelta(days=30000)
dateTo = datetime.date.today()

# if we already got data today, don't wait for the lengthy API call, restore from file
todayBackupFile = "json/"+datetime.datetime.now().strftime("%d-%m-%Y")+".json"
if os.path.exists(todayBackupFile) == False:
    weightsDict = client.get_measurements('Weight', dateFrom, dateTo)
    todayFile = open(todayBackupFile, "w")
    todayFile.write(json.dumps(weightsDict.items(), default=str))
    todayFile.close()

# always restore from json, even when the data was loaded above
# this is to ensure data structure is always the same, whether freshly loaded or restored
# if we didn't do this, then data ('weights' variable), when api-loaded, would be a dict with datetime.date keys and restored data from file would be a string-keyed dict
todayFile = open(todayBackupFile, "r")
weights = json.loads(todayFile.read())
todayFile.close()
    

#https://docs.python.org/2/library/json.html
#json_decode json.loads('')
#json_encode json.dumps(object)
# https://stackoverflow.com/a/36142844/324220
# use json.dumps(object, default=str) to allow serializing toString-able objects e.g. dates (but they will stay in string form when decoding)


#TODO find monday of week of day, get_measurements(mon, fri), add to weeks[]
#def getWeekWeights(day):
#--
#weeks = []
#for w from 1 to e.g. 10 (10 weeks):
#    this will order by date desc (desired ordering)
#    weeks.append(getWeekWeights(datetime.date.today() - datetime.timedelta(days=7*w)))

#keys, values = [], []
#for key, value in weights:
#    keys.append(key)
#    values.append(value)
cols, rows = ["Date", "Weight"], []
for key, value in weights:
    #keys.append(key)
    rows.append([key, value])

pprint(weights)

'''
filename = "weights/" + datetime.datetime.now().strftime("%d-%m-%Y.%H.%M.%S")+"."+dateFrom.strftime("%d%m%Y")+"-"+dateTo.strftime("%d%m%Y")+".csv"

with open(filename, "w") as outfile:
    csvwriter = csv.writer(outfile)
    csvwriter.writerow(cols)
    #csvwriter.writerow(values)
    for row in rows:
        csvwriter.writerow(row)
'''
