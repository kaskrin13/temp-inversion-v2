# David Fisher
# 5/19/2017

import urllib.request
import codecs
import csv
import datetime, time
import re

# gets lowest temperature of the day by
# searching entries in table (2d list) between the beginning
# of the current day and the last entry (most recent time)
# inputs: currentTime = datetime, data = 2d list
# output: lowTemp = tuple(int, datetime)
def getLowTemp(currentTime, data):
	currentDay = []
	#Adds timestamps from current day to new list
	for row in data[1:]:
		if row[0].month == currentTime.month and row[0].day == currentTime.day:
			currentDay.append(row)
			
	lowTemp = currentDay[0][2]
	index = 0

	#Search new list for lowest temp
	for i in range(0, len(currentDay), 1):
		if currentDay[i][2] < lowTemp:
			lowTemp = currentDay[i][2]
			index = i
	return (lowTemp, currentDay[index][0])

# gets highest temperature of the day by
# searching entries in table (2d list) between the beginning
# of the current day and the last entry (most recent time)
# inputs: currentTime = datetime, data = 2d list
# output: highTemp = tuple(int, datetime)
def getHighTemp(currentTime, data):
	currentDay = []
	#Adds timestamps from current day to new list
	for row in data[1:]:
		if row[0].month == currentTime.month and row[0].day == currentTime.day:
			currentDay.append(row)
			
	highTemp = currentDay[0][2]
	index = 0

	#Search new list for highest temp
	for i in range(0, len(currentDay), 1):
		if currentDay[i][2] > highTemp:
			highTemp = currentDay[i][2]
			index = i
	return (highTemp, currentDay[index][0])

# converts datetime object from UTC to local timezone
# input: utc = datetime
# output: utc+offset = datetime
def utcToLocal(utc):
	epoch = time.mktime(utc.timetuple())
	offset = datetime.datetime.fromtimestamp(epoch) - datetime.datetime.utcfromtimestamp(epoch)
	return utc + offset

# get data from CSV file at URL and insert into table (2d list)
# then processes the data added to table (covert text to necessary formats)
# input: url = string
# output: data = 2d list
def getData(url):
	#url = "https://thingspeak.com/channels/211013/feed.csv"
	
	#Opens a CSV file at url and adds data to 2d list
	dataStream = urllib.request.urlopen(url)
	csvFile = csv.reader(codecs.iterdecode(dataStream, 'utf-8'))
	data = []
	for line in csvFile:
		data.append(line)

	#Remove last two rows, which are empty
	data = data[:-2]

	#Converts the timestamps from text to datetime objects
	dates = []
	#Skip first row in data which doesn't contain data
	for row in data[1:]:
			dates.append(datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S %Z"))

	#Converts the timestamps to central timezone
	for i in range(0, len(dates), 1):
		dates[i] = utcToLocal(dates[i])

	#Replaces the text timestamps with the corrected datetime objects
	j = 0
	for i in range(1, len(data), 1):
		data[i][0] = dates[j]
		j += 1

	#Convert temperature text to float
	for i in range(1, len(data), 1):
		data[i][2] = float(data[i][2])

	#Convert windspeed text to float
	for i in range(1, len(data), 1):
		data[i][3] = float(data[i][3])

	#Rename first row to labels
	data[0][2] = 'Air Temp'
	data[0][3] = 'Wind Speed'
	data[0][4] = 'Lux'
	data[0][5] = 'Batt Volt'
		
	return data

# determines whether there is a temperature inversion
# returns true if there is an inversion or false if not
# input: data = 2d list
# output: 8-tuple
def tempInv(data):
	#Get current data
	currentTime = data[-1][0]
	currentTemp = float(data[-1][2])
	currentWindSpeed = float(data[-1][3])

	#Get high and low temp
	lowTemp = getLowTemp(currentTime, data)
	highTemp = getHighTemp(currentTime, data)

	#Determine if there is an inversion
	if currentTime.time() < datetime.time(12):  	
		if currentTemp - lowTemp[0] > 3:
			# no inversion and spray OK
			return (False, currentTemp, str(currentTime)[11:], currentWindSpeed, lowTemp[0], str(lowTemp[1])[11:], highTemp[0], str(highTemp[1])[11:])
		else:
			if (currentTemp - lowTemp[0]) < 2:
				# strong inversion and no spray suggested
				return (True, currentTemp, str(currentTime)[11:], currentWindSpeed, lowTemp[0], str(lowTemp[1])[11:], highTemp[0], str(highTemp[1])[11:])
			else:
				if (currentTemp - lowTemp[0]) < 2 and currentWindSpeed > 4:
					# no inversion and spray OK
					return (False, currentTemp, str(currentTime)[11:], currentWindSpeed, lowTemp[0], str(lowTemp[1])[11:], highTemp[0], str(highTemp[1])[11:])
				else:
					# strong inversion and no spray suggested
					return (True, currentTemp, str(currentTime)[11:], currentWindSpeed, lowTemp[0], str(lowTemp[1])[11:], highTemp[0], str(highTemp[1])[11:])
	else:
		if abs(currentTemp - highTemp[0]) <= 5:
			# no inversion and spray OK
			return (False, currentTemp, str(currentTime)[11:], currentWindSpeed, lowTemp[0], str(lowTemp[1])[11:], highTemp[0], str(highTemp[1])[11:])
		else:
			if (currentTemp - highTemp[0]) >= 7:
				# strong inversion and no spray suggested
				return (True, currentTemp, str(currentTime)[11:], currentWindSpeed, lowTemp[0], str(lowTemp[1])[11:], highTemp[0], str(highTemp[1])[11:])
			else:
				if (currentTemp - highTemp[0]) >= 7 and currentWindSpeed > 4:
					# no inversion and spray OK
					return (False, currentTemp, str(currentTime)[11:], currentWindSpeed, lowTemp[0], str(lowTemp[1])[11:], highTemp[0], str(highTemp[1])[11:])
				else:
					# strong inversion and no spray suggested
					return (True, currentTemp, str(currentTime)[11:], currentWindSpeed, lowTemp[0], str(lowTemp[1])[11:], highTemp[0], str(highTemp[1])[11:])

# prints the data in a readible format for error checking
# input: data = 2d list
def printData(data):
	s = [[str(e) for e in row] for row in data]
	lens = [max(map(len, col)) for col in zip(*s)]
	fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
	table = [fmt.format(*row) for row in s]
	print ('\n'.join(table))

# prints a list of results for error checking
# input: results = 2d list
def printResults(results):
	print("| {0:^10} | {1:^20} | {2:^20} | {3:^21} | {4:^15} | {5:^20} | {6:^15} | {7:^20} |".format("Inversion", "Most Recent Temp", "Most Recent Time", "Most Recent Windspeed", "Low Temp", "Time of Low", "High Temp", "Time of High"))
	print("-"*165)
	for result in results:
		printResult(result)
	
# prints the result of the tempInv function in a readible format for error checking
# input: result = 8-tuple
def printResult(result):
	if result[0]:
		print("| {0:^10} | {1:^20} | {2:^20} | {3:^21} | {4:^15} | {5:^20} | {6:^15} | {7:^20} |".format("Yes", result[1], result[2], result[3], result[4], result[5], result[6], result[7]))
	else:
		print("| {0:^10} | {1:^20} | {2:^20} | {3:^21} | {4:^15} | {5:^20} | {6:^15} | {7:^20} |".format("No", result[1], result[2], result[3], result[4], result[5], result[6], result[7]))

# takes a list of results (8-tuple) and generates an HTML table
# the spaces at the beginning and the \n at the end of each line
# preserves the HTML formatting for writing to a file
# input: results = list
# output: html = string
def generateHTMLTable(results):
	#HTML table beginning tag and title row 
	html = """<table cellspacing="0" cellpadding="10" id="MainContent_GridView1" align="center" style="color:#333333;border-collapse:collapse;overflow-x:auto;">
						<tbody>
							<tr style="color:White;background-color:#5B9BD5;font-weight:bold;">
								<th scope="col">Station</th>
								<th scope="col" style="width:45px;">Current Temp  (&#176;F)</th>
								<th scope="col" style="width:85px;">Current Time</th>
								<th scope="col" style="width:50px;">Wind Speed (MPH)</th>
								<th scope="col" style="width:45px;">Low Temp  (&#176;F)</th>
								<th scope="col" style="width:85px;">Time Of Low</th>
								<th scope="col" style="width:45px;">High Temp  (&#176;F)</th>
								<th scope="col" style="width:85px;">Time Of High</th>
							</tr>\n"""
	
	for i in range(0, len(results), 1):
		#New row tag in table
		html += """							<tr style="color:#333333;background-color:#D2DEEF;">\n"""
		#First column in new row
		html += "								<td>{}</td>\n".format("Station "+str(i+1))
		#Determine color of second column based on whether or not there is an inversion
		if results[i][0]:
			html += """								<td align="center" style="background-color:Crimson;">{}</td>\n""".format(results[i][1])
		else:
			html += """								<td align="center" style="background-color:LightGreen;">{}</td>\n""".format(results[i][1])
		#Rest of columns
		for j in range(2, len(results[0]), 1):
			if isinstance(results[i][j], datetime.datetime):
				#Only print HH:MM:SS of datetime
				html += """								<td align="center">{}</td>\n""".format(str(results[i][j])[11:])
			else:
				html += """								<td align="center">{}</td>\n""".format(str(results[i][j]))
		#End of row tag in table
		html += "							</tr>\n"
	#End of table tag
	html += "					</table>"

	return html

# takes a new HTML table in the form of a string
# and an HTML file and overwrites the old table with the new one
# input: newHTML = string, fileName = string
def replaceHTML(newHTML, fileName):
	#Open file in read mode
	file = open(fileName, "r")
	htmlText = file.read()

	#Regex expression to find the table
	regex = r"(<table.*?>)(.*?)(<\/table>)"
	match = re.search(regex, htmlText, flags=re.DOTALL)

	#Replace old table with new table
	htmlText = htmlText.replace(htmlText[match.start():match.end()], newHTML)

	#Reopen file in write mode and write to file
	file.close()
	file = open(fileName, "w")
	file.write(htmlText)
	file.close()

# uses a hardcoded list of urls to get data from CSVs
# uses the data in the CSVs to generate a set of recommendations
# based on whether or not there is an inversion
# see method descriptions above for more detail
# output: results = 2d list
def main():
	#List of URLs with data, each URL represents one station
	urls = ["https://thingspeak.com/channels/211013/feed.csv"]
	results = []
	
	#Calculate results based on number of URLs
	for url in urls:
		data = getData(url)
		results.append(tempInv(data))

	#Print results for debugging
	
	printResults(results)
	

	#Directly edits html page, won't work for heroku/github
	'''
	#Generate new table
	html = generateHTMLTable(results)
	#Write to file
	replaceHTML(html, "index.html")
	'''

	#return 2d list with info for webpage
	return results

# automatically calls main function
if __name__ == "__main__":
	main()
