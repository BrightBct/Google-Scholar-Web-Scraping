import pandas as pd
import numpy as np
import time

from selenium import webdriver
from bs4 import BeautifulSoup

links = pd.read_csv("All Link.csv")
links = links.to_numpy()
links = links.tolist()
links = [j for sub in links for j in sub]

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

paperLinks = []

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
            paper = paper.replace('oe=ASCII&amp;', '')
            paper = paper.replace('?', '%3F')
            paper = paper.replace('=', '%3D')
            paper = paper.replace('&amp;', '%26')
            paper = paper.replace(':', '%3A')
            paper = paper.replace("/", "#d=gs_md_cita-d&u=%2F")
            paper = paper.replace('"', "")
            paperLinks.append(link+paper)

driver.quit()

paperLinks = np.array(paperLinks)
paperFile = pd.DataFrame(data=paperLinks)
paperFile.to_csv("All Paper Link.csv", index=False)
