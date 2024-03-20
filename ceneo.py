from bs4 import BeautifulSoup
import requests

# Kod EAN produktu
ean = "113304112"

# Pobranie strony produktu
url = f"https://www.ceneo.pl/{ean}"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Znalezienie wszystkich opinii na pierwszej stronie
opinie = soup.find_all("div", class_="user-post user-post__card js_product-review")

# Iteracja po opiniach z pierwszej strony i wyświetlanie danych
for opinia in opinie:
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
    print()

# Pobieranie i wyświetlanie opinii z kolejnych stron
for i in range(2, 10):  # Pobieranie opinii z 2 do 10 strony
    url = f"https://www.ceneo.pl/{ean}/opinie-{i}"
    # Pobieranie i parsowanie strony
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Znajdowanie i wyświetlanie opinii
    opinie = soup.find_all("div", class_="user-post user-post__card js_product-review")
    for opinia in opinie:
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
        print()
