import time
import gspread
import numpy as np
import pandas as pd

from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

paperLinks = pd.read_csv("All Paper Link.csv")
paperLinks = paperLinks.to_numpy()
paperLinks = paperLinks.tolist()
paperLinks = [j for sub in paperLinks for j in sub]

titles = []
authors = []
publication_date = []
description = []
cite_by = []

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

countLink = 0
for link in paperLinks:
    countLink += 1
    print(link)
    driver.get(link)
    time.sleep(1)

    try:
        WebDriverWait(driver, 2).until(ec.presence_of_element_located((By.ID, "gsc_vcd_form")))
        time.sleep(1)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')

        for find in soup.find_all("div", {"id": "gsc_vcd_title"}):
            titles.append(find.text)
            print(find.text)

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

    time.sleep(1)

driver.quit()

titles = np.array(titles)
authors = np.array(authors)
publication_date = np.array(publication_date)
description = np.array(description)
cite_by = np.array(cite_by)
paperTable = pd.DataFrame(data=[titles, authors, publication_date, description, cite_by])
paperTable = paperTable.T
paperTable.columns = ['title', 'authors', 'publication_date', 'description', 'cite_by']
paperTable.to_csv('Paper Table.csv', index=False)

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name('../client_secret.json', scope)
client = gspread.authorize(credentials)

spreadsheet = client.open('Paper Table')

with open('Paper Table.csv', 'r', encoding='iso-8859-1') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet.id, data=content)
