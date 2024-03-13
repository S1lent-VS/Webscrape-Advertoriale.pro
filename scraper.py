from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
import json

# Calea către Edge Driver
service = Service('C:\\edgedrivers\\msedgedriver.exe')
driver = webdriver.Edge(service=service)

# Maximizarea ferestrei browserului la modul fullscreen
driver.maximize_window()

wait = WebDriverWait(driver, 10)

# Deschiderea paginii de login
driver.get("https://app.advertoriale.pro/?show=login")

# Identificarea elementelor pentru completarea formularului
email_input = driver.find_element(By.NAME, "username")
password_input = driver.find_element(By.NAME, "password")
login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

# Completarea câmpurilor de email și parolă
email_input.send_keys("my_mail@yahoo.com")
password_input.send_keys("my_password")

# Apăsarea butonului de login pentru trimiterea formularului
login_button.click()

# Așteptarea pentru încărcarea paginii după logare (puteți ajusta timpul aici)
driver.implicitly_wait(10)
time.sleep(5)  # Sau o așteptare explicită mai robustă

# Obține codul HTML al paginii de după logare
html_after_login = driver.page_source

# Scrie codul HTML într-un fișier nou
with open('page_after_login.html', 'w', encoding='utf-8') as file:
    file.write(html_after_login)
    
# After logging in, find the 'Marketplace' link and click it
marketplace_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Marketplace')))
marketplace_link.click()

marketplace_html = driver.page_source
with open('marketplace_page.html', 'w', encoding='utf-8') as file:
    file.write(marketplace_html)


# Load the HTML content of the first marketplace page to parse the total number of pages
with open('marketplace_page.html', 'r', encoding='utf-8') as file:
    marketplace_html = file.read()

# Use BeautifulSoup to parse the HTML content and find the pagination links
soup = BeautifulSoup(marketplace_html, 'html.parser')
pagination_links = soup.select('nav.paginationBox a.page-link')

# Find the maximum page number
max_page_num = max([int(link.text) for link in pagination_links if link.text.isdigit()], default=1)


wait = WebDriverWait(driver, 10)

# Inițializează lista pentru a stoca detaliile produselor
products_details = []

# Inițializează numărul paginii
page_number = 1

while True:
    # Accesează pagina de marketplace cu numărul curent
    driver.get(f"https://app.advertoriale.pro/account/marketplace.php?page={page_number}")
    # Așteaptă ca lista de produse să fie încărcată
    wait.until(EC.presence_of_element_located((By.ID, "mpList")))

    # Procesează conținutul HTML al paginii pentru a extrage detalii despre produse
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_divs = soup.find_all('div', {'class': 'domain fs18 txt500 text-primary'})
    price_strongs = soup.find_all('strong', {'class': 'price fs16 txt500'})

    for div, strong in zip(product_divs, price_strongs):
        domain = div.get_text(strip=True)
        price = strong.get_text(strip=True)
        products_details.append({
            'domain': domain,
            'price': price
        })

    # Verifică dacă există un link pentru o pagină cu un număr mai mare decât pagina curentă
    pagination_links = soup.find_all('a', {'class': 'page-link'})
    if any(page_number < int(link.text) for link in pagination_links if link.text.isdigit()):
        page_number += 1
    else:
        break

# Salvează detaliile produselor într-un fișier JSON
with open('products_details.json', 'w', encoding='utf-8') as json_file:
    json.dump(products_details, json_file, ensure_ascii=False, indent=4)


# Închide browserul
driver.quit()
