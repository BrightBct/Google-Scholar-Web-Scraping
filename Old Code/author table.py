import gspread
import numpy as np
import pandas as pd
import requests

from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials

url = "https://scholar.google.com/citations?view_op=view_org&hl=en&org=10241031385301082500"

user_ID = []
name = []
affiliation = []

links = []
newPage = url

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

    btn_onclick_list = [a.get('onclick') for a in soup.find_all('button')]
    for click in btn_onclick_list:
        if click is not None:
            click = click.replace("window.location=", "")
            click = click.replace("'", "")
            click = click.replace("\\", "")
            click = click.replace("x26", "&")
            click = click.replace("x3d", "=")
            click = click.replace('&oe=ASCII;', "")
            newPage = "https://scholar.google.com"+click

links = np.array(links)
linkFile = pd.DataFrame(data=links)
linkFile.to_csv("All Link.csv", index=False)

user_ID = np.array(user_ID)
name = np.array(name)
affiliation = np.array(affiliation)
authorTable = pd.DataFrame(data=[user_ID, name, affiliation])
authorTable = authorTable.T
authorTable.columns = ['user_ID', 'name', 'affiliation']
authorTable.to_csv("Author Table.csv", index=False)

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name('../../client_secret.json', scope)
client = gspread.authorize(credentials)

spreadsheet = client.open('Author Table')

with open('Author Table.csv', 'r', encoding='iso-8859-1') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet.id, data=content)
