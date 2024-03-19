from bs4 import BeautifulSoup
import requests

# Kod EAN produktu
ean = "113304112"

# Pobranie strony produktu
url = f"https://www.ceneo.pl/{ean}"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Znalezienie opinii
opinia = soup.find("div", class_="js_product-reviews js_reviews-hook js_product-reviews-container")

# Pobranie danych opinii
autor = opinia.find("span", class_="user-post__author-name").text
rekomendacja = opinia.find("span", class_="user-post__author-recomendation").text
gwiazdki = opinia.find("span", class_="user-post__score-count").text
data = opinia.find("span", class_="user-post__published").text
tresc = opinia.find("div", class_="user-post__text").text

# Wyświetlenie danych
print(f"Autor: {autor}")
print(f"Rekomendacja: {rekomendacja}")
print(f"Liczba gwiazdek: {gwiazdki}")
print(f"Data: {data}")
print(f"Treść: {tresc}")
