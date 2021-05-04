import pandas as pd
import time
import gspread

from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

PATH = './chromedriver'
driver = webdriver.Chrome(PATH)

driver.get("https://scholar.google.com/citations?view_op=view_org&hl=en&org=10241031385301082500")
df = pd.DataFrame({'user_id': [], 'name': [], 'affiliation': []})
df2 = pd.DataFrame({'title': [], 'author': [], 'publication_date': [], 'description': [], 'cite_by': []})
links = []

author = driver.find_element_by_css_selector("#gsc_sa_ccl > div:nth-child(3) > div > div > h3 > a")
while True:
    for i in driver.find_elements(By.CSS_SELECTOR, "div.gs_ai_t"):
        a = i.find_element_by_css_selector('a')
        user_id = a.get_attribute('href').split('=')[-1]
        author = a.text
        affiliation = i.find_element_by_css_selector('div.gs_ai_aff').text
        df = df.append({'user_id': user_id, 'author': author, 'affiliation': affiliation}, ignore_index=True)
        links.append(a.get_attribute('href'))
    try:
        element = WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, '//button[@aria-label="Next"]')))
        element.click()
    except:
        break
    time.sleep(1)

for link in links:
    driver.get(link)
    while True:
        try:
            element = WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.ID, 'gsc_bpf_more')))
            element.click()
        except:
            break
    for i in driver.find_elements(By.CSS_SELECTOR, "tr.gsc_a_tr"):
        a = i.find_element_by_css_selector('a')
        a.click()
        try:
            element = WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, 'gsc_ocd_view')))
        except:
            continue
        title = driver.find_element_by_id('gsc_vcd_title').text
        author = '-'
        publication_date = '-'
        description = '-'
        cited = '-'
        for j in driver.find_elements(By.ID, 'gsc_vcd_table'):
            field = j.find_element_by_class_name('gsc_vcd_field').text
            if field == 'Authors':
                author = j.find_element_by_class_name('gsc_vcd_value').text
            if field == 'Publication date':
                publication_date = j.find_element_by_class_name('gsc_vcd_value').text
            if field == 'Description':
                description = j.find_element_by_class_name('gsc_vcd_value').text
            if field == 'Total citations':
                cited = j.find_element_by_class_name('gsc_vcd_value').text
        df2 = df2.append({'title': title, 'authors': author, 'publication_date': publication_date,
                          'description': description, 'cite_by': cited}, ignore_index=True)
        driver.find_element_by_id('gs_md_cita-d-x').click()
        time.sleep(1)

driver.quit()
df.to_csv("Author Table.csv", index=False)
df2.to_csv("Paper Table.csv", index=False)

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name('../client_secret.json', scope)
client = gspread.authorize(credentials)

spreadsheet = client.open('Author Table')

with open('Author Table.csv', 'r', encoding='iso-8859-1') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet.id, data=content)

spreadsheet = client.open('Paper Table')

with open('Paper Table.csv', 'r', encoding='iso-8859-1') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet.id, data=content)
