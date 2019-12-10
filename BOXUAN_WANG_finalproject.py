#!/usr/bin/env python
# coding: utf-8

# In[11]:


import re
from lxml import html
import requests
from bs4 import BeautifulSoup
import json
import argparse
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
import seaborn as sns


def parse_args():
    description = "Please add parameter"
    pars = argparse.ArgumentParser(description=description)
    pars.add_argument('-source', type=str, help='Where the source from')
    args = pars.parse_args()
    return args


def findUrl(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        soup = None
        return soup
    else:
        soup = BeautifulSoup(r.content, 'lxml')
        return soup


def fetchCountry(source):
    if(source == "remote"):
        print('############################## Fetch CountryInitial start...')
        countryName = []
        countryTwo = []
        countryThree = []
        url = "https://laendercode.net/en/countries.html"
        soup = findUrl(url)
        main_table = soup.findAll("body")[0].find("div")
        b = main_table.findAll("div", {"class": "table-responsive"})[0]
        c = b.findAll("tr")
        for items in c:
            if items.find("a") != None:
                countryName.append(items.findAll(
                    "a")[0].contents[0].contents[1])
                twoInitial = items.findAll("a")[1].contents[0]
                countryTwo.append(twoInitial)
                threeInitial = items.findAll("a")[2].contents[0]
                countryThree.append(threeInitial)

        result_dict = {}
        for i in range(len(countryName)):
            result_dict.setdefault(
                countryThree[i], [countryName[i], countryTwo[i]])

        df = pd.DataFrame.from_dict(result_dict)

        df.to_csv("./data/CountryInitial.csv")
        print('############################## Fetch CountryInitial successful.')

        return result_dict
    elif (source == "local"):
        try:
            df = pd.read_csv("./data/CountryInitial.csv")
            print('############################## Local CountryInitial has been loaded.')
            return df.to_dict('list')
        except:
            print(
                '############################## No local CountryInitial found, fetch again...')
            return fetchCountry("remote")


def fetchHoildyDaysCounts(source, year, countryCode):
    if(source == "remote"):
        print('############################## Fetch HoildyDays start...')

        date = []
        localName = []
        name = []
        count = 0
        dayCount = []
        dayCountNumber = 0
        dataframeHoildyDays = pd.DataFrame({"date": date, "localName": localName, "name": name})
        dataframeLongWeek = pd.DataFrame({"dayCount": dayCount})

        print('fetching year: ' + str(year) + ', with country: ' + str(countryCode))

        try:

            url = f'https://date.nager.at/api/v2/publicholidays/{year}/{countryCode}'
            r = requests.get(url)
            j = json.loads(r.content)
            count = len(j)

            for c in j:
                date.append(c['date'])
                localName.append(c['localName'])
                name.append(c['name'])

            dataframeHoildyDays = pd.DataFrame({"date": date, "localName": localName, "name": name})
            

            urlLongWeek = f'https://date.nager.at/Api/v2/LongWeekend/{year}/{countryCode}'
            rl = requests.get(urlLongWeek)
            jl = json.loads(rl.content)

            for c in jl:
                dayCount.append(c['dayCount'])
                dayCountNumber += c['dayCount']

            dataframeLongWeek = pd.DataFrame({"dayCount": dayCount})

            # print('success')
        except:
            # print('failed')
            count = 0

        dataframeHoildyDays.to_csv(f'./data/publicholidays/HoildyDays-{year}-{countryCode}.csv')
        dataframeLongWeek.to_csv(f'./data/LongWeeks/LongWeeks-{year}-{countryCode}.csv')

        print('############################## Fetch HoildyDays & LongWeeks finish.')
        return count, dayCountNumber
    elif (source == "local"):
        count = 0
        dayCountNumber = 0

        try:
            dataframeHoildyDays = pd.read_csv(f'./data/publicholidays/HoildyDays-{year}-{countryCode}.csv')
            dataframeLongWeek = pd.read_csv(f'./data/LongWeeks/LongWeeks-{year}-{countryCode}.csv')
            count = len(dataframeHoildyDays.values.tolist())
            for index, row in dataframeLongWeek.iterrows():
                dayCountNumber += row['dayCount']
            print(f'############################## {year} - {countryCode}, Local HoildyDays & LongWeeks has been loaded.')
            return count, dayCountNumber
        except:
            print(f'############################## No {year} - {countryCode} local HoildyDays & LongWeeks found, fetch again...')
            return fetchHoildyDaysCounts("remote", year, countryCode)


def fetchGdpByYearToList(source, year):
    if(source == "remote"):
        print('############################## Fetch GdpByYear start...')

        country_lst = []
        year_gdp_lst = []
        result = pd.DataFrame({})
        try:
            r = requests.get("http://www.8pu.com/gdp/ranking_" + str(year) + ".html")
            tree = html.fromstring(r.content)
            gdp_tree = tree.xpath(
                "/html/body/div[4]/div[1]/div[4]/table/tbody/tr/td[3]/font")
            country_tree = tree.xpath("//*[@id='US_']/td/a/@href")
            country_lst = [re.findall("[^/]+(?!.*/)", country_tree[i][:-1])[0]
                        for i in range(len(country_tree))]
            year_gdp_lst = [float(item.text.replace('$', '')) for item in gdp_tree]

        #     for i in range(len(year_gdp_lst)):
        #         comp.append(country_lst[i], year_gdp_lst[i])

            result = pd.DataFrame({'Rank': range(1, len(country_tree)+1)[0:50], 'Name': range(1, len(country_tree)+1)[0:50], 'Initial': country_lst[0:50], 'Year GDP': year_gdp_lst[0:50]})
            result.to_csv(f'./data/gdpByYear/fetchGdpByYearToList-{year}.csv', index=False)
            print('############################## Fetch GdpByYear finish.')
        except:
            result = pd.DataFrame({'Rank': [], 'Name': [], 'Initial': [], 'Year GDP': []})
            print('############################## Fetch GdpByYear failed, no data found')
        
        return result
    elif (source == "local"):
        try:
            result = pd.read_csv(f'/data/gdpByYear/fetchGdpByYearToList-{year}.csv')
            print('############################## Local GdpByYear has been loaded.')
            return result
        except:
            print(
                '############################## No local GdpByYear found, fetch again...')
            return fetchGdpByYearToList("remote", year)


def mainFunc(source, start, end):
    # args = parse_args()
    if (source != "remote" and source != "local" and source != "test"):
        print("Invalid Source, try -source <MODE>")
        # return

    intialMap = fetchCountry(source)
    # print(intialMap)

    for year in range(start, end):
        print(year)
        gdpDataFrame = fetchGdpByYearToList(source, year)
        nameTemp = []
        twoInitialTemp = []
        holidayTemp = []
        dayCountTemp = []

        for index, row in gdpDataFrame.iterrows():
            nameTemp.append(intialMap[row['Initial']][0])

            countryCode = intialMap[row['Initial']][1]
            twoInitialTemp.append(countryCode)

            holiday, dayCount = fetchHoildyDaysCounts(source, year, countryCode)
            holidayTemp.append(holiday)
            dayCountTemp.append(dayCount)

        gdpDataFrame['Name'] = nameTemp
        gdpDataFrame['Initial'] = twoInitialTemp
        gdpDataFrame['Holiday Count'] = holidayTemp
        gdpDataFrame['Long Week days'] = dayCountTemp
        gdpDataFrame.to_csv(f'./data/gdpDataFrame/gdpDataFrame-{year}.csv',index=False)
    
    print(f'Sample - {end} GDP Table')
    print(gdpDataFrame)

if __name__ == "__main__":
    args = parse_args()
    if (args.source == "test"):
        print("In Test Mode, will only show 2 years")
        mainFunc("local", 2014, 2016)
    else:
        mainFunc(args.source, 2014, 2019)


for year in range(2014,2019):
    tempdf = pd.read_csv(f'./data/gdpDataFrame/gdpDataFrame-{year}.csv')
    fig,ax=plt.subplots()
    ax.bar(tempdf["Name"],tempdf["Holiday Count"])
    ax.set_xlabel("Name")  #设置x轴标签
    ax.set_ylabel("Holiday Count")  #设置y轴标签
    # ax.set_title("Top 50 GDP Country Ranking in str(year)")  #设置标题
    plt.title(f'Top 50 GDP Country Ranking in {year}')
    plt.xticks(rotation=90,fontsize=5)
    # ax.set_xlim(2014,2019)  #设置x轴数据限值
    plt.show()  #显示图像

    fig,ax=plt.subplots()
    ax.bar(tempdf["Name"],tempdf["Long Week days"])
    ax.set_xlabel("Name")  #设置x轴标签
    ax.set_ylabel("Long Week days")  #设置y轴标签
    # ax.set_title("Top 50 GDP Country Ranking in {year}") 
    plt.title(f'Top 50 GDP Country Ranking in {year}') #设置标题
    plt.xticks(rotation=90,fontsize=5)
    # ax.set_xlim(2014,2019)  #设置x轴数据限值
    plt.show()  #显示图像

def trimZero(df):
    return df[df['Holiday Count'] != 0]

    for year in range(2014,2019):
        tempdf = pd.read_csv(f'./data/gdpDataFrame/gdpDataFrame-{year}.csv')
        tempdf = trimZero(tempdf)
        plt.figure(figsize=(15,5))
        plt.plot(tempdf['Name'],tempdf['Long Week days'],'blue', marker='.',label='Long Week days',linewidth=1)
        plt.xticks(rotation=90,fontsize=5)
        plt.xlabel("Name")
        plt.ylabel("Long Week days")
        plt.title(f'Top 50 GDP Country Ranking in {year}')
    plt.show()

def trimZero(df):
    return df[df['Holiday Count'] != 0]

for year in range(2014,2019):
    tempdf = pd.read_csv(f'./data/gdpDataFrame/gdpDataFrame-{year}.csv')
    tempdf = trimZero(tempdf)
    plt.figure(figsize=(15,5))
    plt.plot(tempdf['Name'],tempdf['Holiday Count'],'red', marker='.',label='Holiday Count',linewidth=1)
    plt.xticks(rotation=90,fontsize=5)
    plt.xlabel("Name")
    plt.ylabel("Holiday Count")
    plt.title(f'Top 50 GDP Country Ranking in {year}')
plt.show()

def trimZero(df):
    return df[df['Holiday Count'] != 0]

# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.ticker import MultipleLocator, FormatStrFormatter
for year in range(2014,2019):
    tempdf = pd.read_csv(f'./data/gdpDataFrame/gdpDataFrame-{year}.csv')
    tempdf = trimZero(tempdf)
# plt.scatter(tempdf['Name'],tempdf['Long Week days'],color='blue',label='Long Week days',alpha=0.8)
# plt.plot(tempdf['Name'],tempdf['Long Week days'],'red', marker='*',label='Top 50 GDP Country Ranking in 2014-2018')

# plt.xticks(rotation=90)
# plt.xlabel("Name")
# plt.ylabel("Long Week days")
# plt.title("Top 50 GDP Country Ranking in 2018")
    plt.figure(figsize=(15,6))
    sns.regplot(data=tempdf, x=tempdf['Long Week days'],y=tempdf['Year GDP'],line_kws={'color':'green'})
#     plt.yticks(range(0, 200000, 7000),rotation=0)
#     ymajorLocator = MultipleLocator(1000) 
#     x = range(0,80,10)
#     y = range(0,50000,2000)
#     plt.plot(x,y)
    plt.title(f'Top 50 GDP Country Ranking in {year}')
plt.show()

