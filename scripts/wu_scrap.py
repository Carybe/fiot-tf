#!/usr/bin/env python

import os

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException

import datetime

gecko_path = os.environ["VIRTUAL_ENV"] + \
	'/lib/python3.7/site-packages/pygeckodriver/geckodriver_linux64'

#          [0]          [1]          [3]          [5]       [7]       [8]          [10]          [12]       [14]        [16]
classes = ['Time', 'Temperature', 'Dew Point', 'Humidity', 'Wind', 'Wind Speed', 'Wind Gust', 'Pressure', 'Precip.', 'Condition']

dataset = dict()
for clas in classes:
	dataset[clas] = []

#url_base="https://www.wunderground.com/history/daily/br/s%C3%A3o-paulo/SBSP/date/"
url_base="https://www.wunderground.com/history/daily/us/ny/new-york-city/KLGA/date/"

year = 2000
month = 1
day = 1

#records = 500
records = 200000

#output='out.csv'
output='wu_ny.csv'

date = datetime.date(year, month, day)

options = Options()
options.add_argument("--headless")

driver = Firefox(options=options, executable_path=gecko_path)
driver.implicitly_wait(10)
#wait = WebDriverWait(driver, 10)

with open(output, 'w') as file:

	# CSV Header
	file.write(';'.join(classes))
	file.write('\n')

	count = 0
	for i in range(records):
		print(date)

		url = url_base + str(date)
		driver.get(url)

		year = date.year
		month = date.month
		day = date.day

		while True:
			try:
				table = driver.find_elements_by_xpath("//*[@role = 'rowgroup']//*[@class = 'ng-star-inserted']")
				break
			except IndexError as e:
				driver.refresh()
				print("Retrying ", date)

		for row_index in range(0, len(table), 17):

			# Time (Epoch)
			cell_time = table[row_index + 0].text
			time_epoch = -1
			if cell_time:
				time_struct = datetime.datetime.strptime("%d-%.2d-%.2d %s" % (year, month, day, cell_time), "%Y-%m-%d %I:%M %p")
				time_epoch = datetime.datetime.strftime(time_struct, "%s")
			dataset['Time'].append(time_epoch)

			# Temperature (Celsius)
			cell_temp = table[row_index + 1].text
			temperature = -273
			if cell_temp:
				temperature = (float(cell_temp.split(' ')[0]) - 32.0) / 1.8
			dataset['Temperature'].append(temperature)

			# Dew Point (Celsius)
			cell_dew = table[row_index + 3].text
			dew_point = -273
			if cell_dew:
				dew_point = (float(cell_dew.split(' ')[0]) - 32.0) / 1.8
			dataset['Dew Point'].append(dew_point)

			# Humidity (percentage)
			cell_hum = table[row_index + 5].text
			humidity = -1
			if cell_hum:
				humidity = float(cell_hum.split(' ')[0])/100
			dataset['Humidity'].append(humidity)

			# Wind Direction (categorical)
			cell_wind = table[row_index + 7].text
			wind_direction = "N/A"
			if cell_wind:
				wind_direction = cell_wind
			dataset['Wind'].append(wind_direction)

			# Wind Speed (m/s)
			cell_wind_sp = table[row_index + 8].text
			wind_speed = -1
			if cell_wind_sp:
				wind_speed = float(cell_wind_sp.split(' ')[0]) * 0.44704
			dataset['Wind Speed'].append(wind_speed)

			# Wind Gust (m/s)
			cell_wind_gust = table[row_index + 10].text
			wind_gust = -1
			if cell_wind_gust:
				wind_gust = float(cell_wind_gust.split(' ')[0]) * 0.44704
			dataset['Wind Gust'].append(wind_gust)

			# Atmospheric Pressure (hPa)
			cell_pres = table[row_index + 12].text
			pressure = -1
			if cell_pres:
				pressure = float(cell_pres.split(' ')[0]) * 33.863800000001
			dataset['Pressure'].append(pressure)

			# Preciptation (mm)
			cell_prec = table[row_index + 14].text
			precipitation = -1
			if cell_prec:
				preciptation = float(cell_prec.split(' ')[0]) / 0.039370
			dataset['Precip.'].append(preciptation)

			# Condition (categorical)
			cell_con = table[row_index + 16].text
			condition = "N/A"
			if cell_con:
				condition = cell_con
			dataset['Condition'].append(condition)

			file.write(';'.join(map(str, [dataset[x][count] for x in classes])))
			file.write('\n')
			count += 1

		date += datetime.timedelta(days=1)
		file.flush()

#print(dataset)

#	for i in range(len(dataset['Condition'])):

