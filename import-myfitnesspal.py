#!/usr/local/bin/python

####   Author: Luka Ramishvili

import datetime
import csv
import myfitnesspal
from pprint import pprint
#import sqlite3
import json
import os.path
import moment # pip install moment
import calendar

# from https://stackoverflow.com/a/6558571/324220
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

# takes a date d, and returns the monday of the date d's week (with hours 00:00:0000)
def start_of_week(d):
    next_monday = next_weekday(d, 0)
    this_week_monday = next_monday - datetime.timedelta(7)
    this_week_monday = this_week_monday.replace(minute=0, hour=0, second=0, microsecond=0)
    return this_week_monday
# takes a date d, and returns the sunday of the date d's week (with hours 23:59:999999)
def end_of_week(d):
    this_week_monday = start_of_week(d)
    this_week_sunday = this_week_monday + datetime.timedelta(6)
    this_week_sunday = this_week_sunday.replace(minute=59, hour=23, second=59, microsecond=999999)
    return this_week_sunday

# returns the same day but with 00:00:0000 hours
def start_of_day(d):
    return d.replace(minute=0, hour=0, second=0, microsecond=0)

# returns the same day but with 00:00:0000 hours
def end_of_day(d):
    return d.replace(minute=59, hour=23, second=59, microsecond=999999)

def weeks_match(d1, d2):
    # this works because start_of_week returns monday 00:00:0000
    # ... and end_of_week returns sunday 23:59
    return start_of_week(d2) <= d1 <= end_of_week(d2)

def day_matches(d1,d2):
    return start_of_day(d2) <= d1 <= end_of_day(d2)

# returns only weights in the week of date d (from monday including sunday)
# example output (for 19/3/2018):
# [[u'2018-03-25', 105.3], [u'2018-03-24', 105.1], [u'2018-03-23', 106.0], [u'2018-03-22', 106.5], [u'2018-03-21', 106.1], [u'2018-03-20', 105.0], [u'2018-03-19', 105.1]]
def weights_of_week_of_day(d):
    # filter 'weights' to only include records in the same week as date 'd'
    return list(filter(lambda pair: weeks_match(moment.date(pair[0]).date, d), weights))

def weight_on_day(d):
    # filter 'weights' to only include records in the same week as date 'd'
    list_with_only_this_day = list(filter(lambda pair: day_matches(moment.date(pair[0]).date, d), weights))
    if len(list_with_only_this_day) > 0:
        return list_with_only_this_day[0][1]
    else:
        return 0.0

# returns average weight for a week ('d' must be a day in that week)
def avg_weight_of_week_of_day(d):
    week_weight_pairs = weights_of_week_of_day(d)
    week_weights = list(map(lambda pair: pair[1], week_weight_pairs))
    # reason for if/else: even if we use initial value 0 on reduce, we still have to divide the reduced sum by len(), so we'd divide by 0 if there are no pairs
    if len(week_weights) > 0:
        return reduce(lambda a1, a2: a1 + a2, week_weights) / len(week_weights)
    else:
        return 0.0

# returns a diff of weight compared to previous week
# e.g. avg weight in the week of 2018/03/25 was 105.58, the previous week (2018/03/18) was 106.44, so this function will return 105.58-106.44=-0.86 (lost weight=negative number result)
def avg_change_from_prev_week(d):
    return avg_weight_of_week_of_day(d) - avg_weight_of_week_of_day(d - datetime.timedelta(7))

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

### this script can also work without MyFitnessPal, if we provide a list of date/weight pairs (e.g. [ ['2018-03-26',107.6],... ])

# always restore from json, even when the data was loaded above
# this is to ensure data structure is always the same, whether freshly loaded or restored
# if we didn't do this, then data ('weights' variable), when api-loaded, would be a dict with datetime.date keys and restored data from file would be a string-keyed dict
todayFile = open(todayBackupFile, "r")
weights = json.loads(todayFile.read())
todayFile.close()

# return all mondays of weeks with recorded weights (list of datetime.datetime)
def all_recorded_mondays():
    # converting to a set and back leaves only unique values
    # this works because all dates returned by start_of_week have the same day/month/year (obviously) and the same hour/second/microsecond 00:00:0000(for comparisons to work)
    # we also sort and reverse in descending (most recent monday first)
    return list(reversed(sorted(list(set(list(map(lambda pair: start_of_week(moment.date(pair[0]).date), weights)))))))

#in $ python repl, use execfile("import-myfitnesspal.py") to include this file in-place

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


# this is a simple vertical list of dates and weights
'''
cols, rows = ["Date", "Weight"], []
for key, value in weights:
    #keys.append(key)
    rows.append([key, value])
'''

# this creates a row of week records (each week has 1-7 vertical rows in its column)
cols = []
rows = []
all_mondays = all_recorded_mondays()
cols.append("Title") # first column contains row titles (e.g. Weekday, Avg.Change, etc)
# create column titles (each week gets one column)
for monday in all_mondays:
    thisMonWeekNumber = monday.strftime('%V')
    # "26-03-2018 WEEK_NUMBER/YEAR"
    cols.append(thisMonWeekNumber+'/'+monday.strftime('%Y')+' ('+monday.strftime("%d-%m-%Y")+')')
# add a row that holds the average weight for each column's week
weightAvgRow = []
weightAvgRow.append('Avg. weight')
for monday in all_mondays:
    weightAvgRow.append(avg_weight_of_week_of_day(monday))
rows.append(weightAvgRow)
# add a row that holds the change in average weight for each column's week
weightChangeRow = []
weightChangeRow.append('Change in avg. weight')
for monday in all_mondays:
    weightChangeRow.append(avg_change_from_prev_week(monday))
rows.append(weightChangeRow)
# create one row for each weekday (the row will be populated with weights on that day)
# use [6,5,..1,0] instead of [0,1..6] so that weekdays are ordered in descending order
reverse_weekday_numbers = list(map(lambda x: x*-1, range(-6, 1)))
for i_row_weekday in reverse_weekday_numbers:
    nextRow = []
    # write weekday name in the first column
    nextRow.append(calendar.day_name[i_row_weekday])
    # write all the weights on that weekday
    for monday in all_mondays:
        that_day_date = monday + datetime.timedelta(i_row_weekday)
        nextRow.append(weight_on_day(that_day_date))
    rows.append(nextRow)



### output the csv stored in 'cols' and 'rows'
filename = "weights/" + datetime.datetime.now().strftime("%d-%m-%Y.%H.%M.%S")+"."+dateFrom.strftime("%d%m%Y")+"-"+dateTo.strftime("%d%m%Y")+".csv"

with open(filename, "w") as outfile:
    csvwriter = csv.writer(outfile)
    csvwriter.writerow(cols)
    #csvwriter.writerow(values)
    for row in rows:
        csvwriter.writerow(row)

