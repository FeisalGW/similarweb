# -*- coding: utf-8 -*-
# 爬取similarweb該網址geogrphy traffic和該網址資訊
from bs4 import BeautifulSoup
from login import login
import requests
import json
import csv
import time
import datetime
import urllib
import os
import calendar



def collect_web(file_name):
	'''Collect domains from file_name.
	Args:
		file_name:csv file with domain on first column.
	Return:
		webs:domains list
	'''
	webs = []
	with open(file_name, "r") as f:
		reader = csv.reader(f, delimiter = ",")
		next(reader, None)  # ignore column name
		for i in reader:
			webs.append(i[0])

	return webs



def collect_country():
	'''Collect countries and its codes from country_code.csv
	Return:
		countries:countries dictionary with id as key, country names as value.
	'''
	countries = {}
	file_name = "../code info/country_code.csv"
	with open(file_name, "r") as f:
		reader = csv.reader(f, delimiter = ",")
		next(reader, None)  # ignore column name
		for i in reader:
			countries[i[0]] = i[2]

	return countries



def similarweb_crawler(file_name):
	'''Crawl domain infomatiion from similarweb.
	Args:
		file_name:csv file with domain on first column.
	'''

	webs = collect_web(file_name)

	# countries = collect_country("../code info/country_code.csv")
	countries = collect_country()

	### Login similarweb ###
	s = login()
	print "There are " + str(len(webs)) + " websites need to crawl."
	
	headers = {
		"referer":"https://pro.similarweb.com/",
		"user-agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
		"authority":"pro.similarweb.com",
		"method":"GET",
		"path":"/api/startup",
		"scheme":"https",
			"cookie":".SGTOKEN.SIMILARWEB.COM=gLj2mN7Kr0sHZ8HgWsk5X0z2Z6NwxYUlHJGt8ohNCspjbXncTnGWdoEs1FqTq1T2WvkIi0hygLlk18TmXoL5az3x3wbIogo21ZRQECWoqWhRjRfmsi0vMVF7y0HMTyFlw4YX2YUwKNjTnb7MJ18JTsQBX2pPHzoSbKDs250H8GbkIWhuhitTEBfmvVHFbRjfm8OqbNMjTtw09xoOCPNow6wy9FBqUgx6Cux5_HFIeUSAKYoPo5NAAp19y28ctvMufvHmRueulXiRaJWusceWng2;"
	}
	
	# category traffic data
	data_category = []
	data_category.append(["web", "Country traffic rank", "Country code", "Country", "Traffic share", "Avg. Visit Duration", "PagePerVisit", "BounceRate", "Rank"])
	# info data
	data_info = []
	data_info.append(["web", "main Domain Name", "tags", "global Ranking", "category", "category Ranking", "highest Traffic Country", "highest Traffic Country Ranking"])

	# date for url
	date_to = datetime.datetime.now()
	day = date_to.day
	
	if day < 15:
		last_month_day = calendar.monthrange(date_to.year, date_to.month)[1]
		date_to = date_to - datetime.timedelta(days = day+last_month_day)
		date_from = datetime.datetime.now() - datetime.timedelta(days = 90 + day + last_month_day)
	
	if day > 15:
		date_to = date_to - datetime.timedelta(days = day)
		date_from = datetime.datetime.now() - datetime.timedelta(days = 60 + day)
		
	date_to = str(date_to.year) + "|" + str(date_to.month).zfill(2) + "|" + str(date_to.day).zfill(2)
	date_from = str(date_from.year) + "|" + str(date_from.month).zfill(2) + "|" + str(date_from.day).zfill(2)


	
	for web in webs:
		print web

		# test if the url is .tw or no
		while True:
			try:
				res = requests.get("http://" + web, timeout = 30)
				redirection = res.url			
				break

			# except requests.exceptions.ConnectionError:
			# 	res.url = ""
			# 	break
			# except requests.exceptions.ReadTimeout:
			# 	res.url = ""
			# 	break
			# except:
			# 	res.url = ""
			# 	break
			except:
				redirection = ""
				break
			

		if ".tw" not in redirection:
			continue



		### WEB info ###
		url = "https://pro.similarweb.com/api/websiteanalysis/getheader?includeCrossData=true&keys=" + web + "&mainDomainOnly=true"
		#print url
		try:
			res = s.get(url, headers = headers)
		except:
			continue
		# print res.text.encode("utf-8")
		
		try:
			js = json.loads(res.text)[web]
		except:
			continue
		highestTrafficCountry = js["highestTrafficCountry"]

		if highestTrafficCountry == 0:
			print web + " NO DATA."
			data_category.append([web])
			data_info.append([web])
			continue

		tags = ""
		for i in js["tags"]:
			tags = tags + i.encode("big5", "ignore") + "\n"
		
		mainDomainName = js["mainDomainName"]
		tags = tags.strip()
		globalRanking = js["globalRanking"]
		category = js["category"]
		categoryRanking = js["categoryRanking"]
		highestTrafficCountry = js["highestTrafficCountry"]
		highestTrafficCountryRanking = js["highestTrafficCountry"]
		
		data_info.append([web, mainDomainName, tags, globalRanking, category, categoryRanking, highestTrafficCountry, highestTrafficCountryRanking])

		
		### Geography statistics ###
		# Parameter for url
		# country:999
		# from:urllib.quote(date_from)
		# includeSubDomains:true
		# isWindow:false
		# keys:web
		# metric:GeographyExtended
		# orderBy:TotalShare desc
		# timeGranularity:Monthly
		# to:urllib.quote(date_to)
		url = "https://pro.similarweb.com/widgetApi/WebsiteGeographyExtended/GeographyExtended/Table?country=999&from=" + urllib.quote(date_from) + "&includeSubDomains=true&isWindow=false&keys=" + web + "&metric=GeographyExtended&orderBy=TotalShare+desc&timeGranularity=Monthly&to=" + urllib.quote(date_to)

		res = s.get(url, headers = headers)
		ratio_ranking = 1

		try:
			js = json.loads(res.text)
		except:
			continue

		for i in js["Data"][:5]:
			country_code = i["Country"]
			ratio = round(i["Share"]*100, 2) # 國家流量佔比
			AvgVisitDuration = round(i["AvgVisitDuration"], 2) # 平均造訪停留時間
			PagePerVisit = round(i["PagePerVisit"], 2) # 訪客瀏覽平均頁數
			BounceRate = round(i["BounceRate"], 2)# 進入網站後在特定時間內只瀏覽了一個網頁就離開的訪客百分比
			Rank = i["Rank"] # country ranking
			data_category.append([web, ratio_ranking, country_code, countries[str(country_code)], ratio, AvgVisitDuration, PagePerVisit, BounceRate, Rank])
			ratio_ranking += 1
			
		print web + " is DONE!"
		time.sleep(3)
	
	### save files ###
	file_name = file_name[(file_name.rfind("/")+1):-4]
	with open("../../builtwith/similarweb info/" + file_name + "_WEB Geography Traffice.csv", "wb") as f:
		w = csv.writer(f)
		w.writerows(data_category)
	
	with open("../../builtwith/similarweb info/" + file_name + "_WEB info.csv", "wb") as f:
		w = csv.writer(f)
		w.writerows(data_info)

	print "Done!"



def main():

	# file_name = input("輸入要抓取的檔名:".decode("utf-8").encode("big5"))
	files = os.listdir("../../builtwith/raw data/")

	if files is []:
		print "There's no files for crawling."

	for file_name in files:
		if ".csv" not in file_name:
			continue

		print file_name
		similarweb_crawler("../../builtwith/raw data/" + file_name)
	
		# move file to done directory
		# os.rename("../../builtwith/raw data/" + file_name, "../../builtwith/raw data/done/" + file_name)





if __name__ == "__main__":

	main()