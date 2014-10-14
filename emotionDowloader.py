#! /usr/bin/python

import json, csv, sys
import urllib2
from time import sleep


starttime = 1401580800 #June 1st 2014, midnight UTC (00:00:00)
endtime = 1410393600 #Sept 11th 2014, midnight UTC (00:00:00)
timeperiod = 60*60*24


emotions = json.load(urllib2.urlopen("http://wefeel.csiro.au/api/emotions/tree"))
emotions = emotions["children"]
continents = json.load(urllib2.urlopen("http://wefeel.csiro.au/api/zones/tree"))
continents = continents["children"]

fieldnames = []

#create CSV headings
for emotion in emotions:
	fieldnames.append(emotion["name"]+"/*")
	for secondary in emotion["children"]:
		fieldnames.append(secondary["path"])
fieldnames.sort()

fieldnames.insert(0,"totalEngTweets")
fieldnames.insert(0,"timezone")
fieldnames.insert(0,"continent")
fieldnames.insert(0,"start")

out_file = 'final_data.csv'
with open(out_file, 'wb') as of:
	csvwriter = csv.DictWriter(of, delimiter=',', fieldnames=fieldnames)
	csvwriter.writeheader()

	rows = []
	for time in range(starttime, endtime, timeperiod):
		print "Starting download for timestamp: %d" % time
		stms = time*1000
		etms = (time+timeperiod)*1000
		for continent in continents:
			print "Starting continent %s" % (continent["id"])
			tweetTotals = json.load(urllib2.urlopen("http://wefeel.csiro.au/api/tweets/totals?continent=%s&start=%d&end=%d" % (continent["id"], stms, etms)))
			#print tweetTotals
			timezones = continent["children"]
			for timezone in timezones:
				row = {}
				tname = timezone["id"]
				tpath = timezone["path"]
				for emotion in emotions: 
					emotionTotals = json.load(urllib2.urlopen("http://wefeel.csiro.au/api/emotions/primary/%s/secondary/totals?continent=%s&start=%d&end=%d&timezone=%s" % (emotion["name"], continent["id"], stms, etms, tname)))
					row.update(emotionTotals)
				row["timezone"] = tname
				row["continent"] = continent["id"]
				row["start"] = time
				if tpath in tweetTotals:
					row["totalEngTweets"] = tweetTotals[tpath]
				else:
					row["totalEngTweets"] = 0
				rows.append(row)
				#write row to CSV file
				csvwriter.writerow(row)

				sys.stdout.write('.')
				sys.stdout.flush()
				sleep(0.750)
			print ""

with open("json_finaldata.json", "w") as of:
	json.dump(rows, of, indent=2)

print "Done writing data to CSV, recommended sorting in Excel is timezone, continent, start"
