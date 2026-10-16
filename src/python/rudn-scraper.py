# САМЫЙ РАННИЙ ПРОТОТИП
# ВСЯ РАБОТА БУДЕТ БАЗИРОВАНА С НЕГО
# https://i.pinimg.com/474x/f7/20/20/f72020244e330f7415319513208af87d.jpg <- это я

import os
import time
import requests

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By


download_dir = os.path.abspath("./downloads") # папка downloads для файлов
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

edge_options = Options()
edge_prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}
edge_options.add_experimental_option("prefs", edge_prefs)

driver = webdriver.Edge(options=edge_options) # да я использую edge, я злой
# ---------- весь этот блок работает как шаблон, с которого надо работать ------
driver.get("https://www.rudn.ru/")

name_input = driver.find_element(By.LINK_TEXT, "Карьера")
name_input.click()
elements = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
pdf_urls = [elem.get_attribute("href") for elem in elements]
for i in pdf_urls:
    response = requests.get(i)
    filename = os.path.basename(i.split("?")[0])
    print(f"Downloading file from page {i} to: {download_dir}")
    time.sleep(0.2)

    with open(os.path.join(download_dir, filename), "wb") as f:
        f.write(response.content)


print("Все .pdf файлы на странице скачены.")
driver.quit()