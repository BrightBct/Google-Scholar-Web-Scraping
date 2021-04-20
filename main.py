import time
import numpy as np
import pandas as pd
import urllib.request
import requests
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials

url = "https://scholar.google.com/citations?view_op=view_org&hl=en&org=10241031385301082500"

user_ID = []
name = []
affiliation = []

titles = []
authors = []
publication_date = []
description = []
cite_by = []

links = []
paperLinks = []
newPage = url

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

for i in range(30):
    page = requests.get(newPage)
    soup = BeautifulSoup(page.content, 'lxml')
    for find in soup.find_all('a', href=True):
        if find.text:
            link = "https://scholar.google.com/" + find['href']
            if "/citations?hl=en&user=" in link:
                links.append(link)
                user_ID.append(find['href'][22:])
                name.append(find.text)

    for word in soup.find_all("div", {"class": "gs_ai_aff"}):
        affiliation.append(word.text)

    btn_onlclick_list = [a.get('onclick') for a in soup.find_all('button')]
    for click in btn_onlclick_list:
        if click is not None:
            click = click.replace("window.location=", "")
            click = click.replace("'", "")
            click = click.replace("\\","")
            click = click.replace("x26", "&")
            click = click.replace("x3d", "=")
            click = click.replace('&oe=ASCII;', "")
            newPage = "https://scholar.google.com"+click

for link in links:
    driver.get(link)
    time.sleep(1)

    for j in range(10):
        try:
            driver.find_element_by_xpath("//button[@id='gsc_bpf_more']").click()
            time.sleep(0.5)
        except:
            continue
    time.sleep(1)

    page = driver.page_source
    soup = BeautifulSoup(page, 'lxml')
    for find in soup.find_all('a'):
        find = str(find)
        if "data-href" in find:
            split = find.split("href=\"")
            paper = split[1]
            paper = paper.replace('oe=ASCII&amp;','')
            paper = paper.replace('?', '%3F')
            paper = paper.replace('=', '%3D')
            paper = paper.replace('&amp;', '%26')
            paper = paper.replace(':', '%3A')
            paper = paper.replace("/", "#d=gs_md_cita-d&u=%2F")
            paper = paper.replace('"', "")
            paperLinks.append(link+paper)

            title = split[2]
            title = title.replace("javascript:void(0)\">", "")
            title = title.replace("</a>", "")
            titles.append(title)

countLink = 0
for link in paperLinks:
    countLink += 1
    print(link)
    driver.get(link)
    time.sleep(1)

    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "gsc_vcd_table")))
        time.sleep(1)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        field = []
        value = []
        cite = '-'
        for find in soup.find_all("div", {"class": "gsc_vcd_field"}):
            field.append(find.text)
        for find in soup.find_all("div", {"class": "gsc_vcd_value", "style": None}):
            value.append(find.text)
        for find in soup.find_all('a', href=True):
            if find.text:
                if "Cited by" in find.text:
                    cite = find.text[9:]
                    break

        count = 0
        for count in range(len(field)):
            if field[count] == "Authors":
                print(value[count])
                authors.append(value[count])
            elif field[count] == "Publication date":
                print(value[count])
                publication_date.append(value[count])
            elif field[count] == "Description":
                print(value[count])
                description.append(value[count])
            elif field[count] == "Total citations":
                print(cite)
                cite_by.append(cite)
            count += 1

        if len(authors) < countLink:
            authors.append("-")
        if len(publication_date) < countLink:
            publication_date.append("-")
        if len(description) < countLink:
            description.append("-")
        if len(cite_by) < countLink:
            cite_by.append("-")

        print(len(authors))
        print(len(publication_date))
        print(len(description))
        print(len(cite_by))

    except:
        continue

driver.quit()

user_ID = np.array(user_ID)
name = np.array(name)
affiliation = np.array(affiliation)
authorTable = pd.DataFrame(data=[user_ID, name, affiliation])
authorTable = authorTable.T
authorTable.columns = ['user_ID', 'name', 'affiliation']
authorTable.to_csv("Author Table.csv", index=False)

titles = np.array(titles)
authors = np.array(authors)
publication_date = np.array(publication_date)
description = np.array(description)
cite_by = np.array(cite_by)
paperTable = pd.DataFrame(data=[titles, authors, publication_date, description, cite_by])
paperTable = paperTable.T
paperTable.columns = ['title', 'authors', 'publication_date', 'description', 'cite_by']
paperTable.to_csv('Paper Table.csv', index=False)

time.sleep(5)

driver.quit()

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(credentials)

spreadsheet = client.open('Author Table')

with open('DSI200/Author Table.csv', 'r', encoding='iso-8859-1') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet.id, data=content)

spreadsheet = client.open('Paper Table')

with open('DSI200/Paper Table.csv', 'r', encoding='iso-8859-1') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet.id, data=content)
