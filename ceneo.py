from bs4 import BeautifulSoup
import requests
import json
import csv
from collections import Counter
from fractions import Fraction
import re
import matplotlib.pyplot as plt

def pobierz_opinie(url):
    """
    Pobiera opinie z podanego adresu URL.

    Args:
        url: Adres URL strony z opiniami.

    Returns:
        Lista elementów BeautifulSoup zawierających opinie.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    opinie = soup.find_all("div", class_="user-post user-post__card js_product-review")
    return opinie

def zapisz_do_json(opinie, nazwa_pliku):
    """
    Zapisuje opinie do pliku JSON.

    Args:
        opinie: Lista opinii w formacie BeautifulSoup.
        nazwa_pliku: Nazwa pliku JSON.
    """
    with open(nazwa_pliku, "w", encoding="utf-8") as f:
        json.dump([_konwertuj_do_json(opinia) for opinia in opinie], f, indent=4)

def _konwertuj_do_json(opinia):
    """
    Konwertuje obiekt Tag do formatu JSON.

    Args:
        opinia: Obiekt BeautifulSoup Tag.

    Returns:
        Słownik JSON z danymi z opinii.
    """
    # Zabezpieczenie przed brakiem autora
    autor = "Brak autora"
    autor_element = opinia.find("span", class_="user-post__author-name")
    if autor_element:
        autor = autor_element.text

    # Zabezpieczenie przed brakiem rekomendacji
    rekomendacja = "Brak rekomendacji"
    rekomendacja_element = opinia.find("span", class_="user-post__author-recomendation")
    if rekomendacja_element:
        rekomendacja = rekomendacja_element.text

    # Zabezpieczenie przed brakiem gwiazdek
    gwiazdki = "Brak gwiazdek"
    gwiazdki_element = opinia.find("span", class_="user-post__score-count")
    if gwiazdki_element:
        gwiazdki = gwiazdki_element.text

    # Zabezpieczenie przed brakiem daty
    data = "Brak daty"
    data_element = opinia.find("span", class_="user-post__published")
    if data_element:
        data = data_element.text

    # Zabezpieczenie przed brakiem treści
    tresc = "Brak treści"
    tresc_element = opinia.find("div", class_="user-post__text")
    if tresc_element:
        tresc = tresc_element.text

    return {
        "autor": autor,
        "rekomendacja": rekomendacja,
        "gwiazdki": gwiazdki,
        "data": data,
        "tresc": tresc,
    }

def zapisz_do_csv(opinie, nazwa_pliku):
    """
    Zapisuje opinie do pliku CSV.

    Args:
        opinie: Lista opinii w formacie BeautifulSoup.
        nazwa_pliku: Nazwa pliku CSV.
    """
    with open(nazwa_pliku, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Autor", "Rekomendacja", "Liczba gwiazdek", "Data", "Treść"])
        
        # Pobranie danych z opinii
        for opinia in opinie:
            # Zabezpieczenie przed brakiem autora
            autor_element = opinia.find("span", class_="user-post__author-name")
            if autor_element:
                autor = autor_element.text
            else:
                autor = "Brak autora"

            # Zabezpieczenie przed brakiem rekomendacji
            rekomendacja_element = opinia.find("span", class_="user-post__author-recomendation")
            if rekomendacja_element:
                rekomendacja = rekomendacja_element.text
            else:
                rekomendacja = "Brak rekomendacji"

            # Zabezpieczenie przed brakiem gwiazdek
            gwiazdki_element = opinia.find("span", class_="user-post__score-count")
            if gwiazdki_element:
                gwiazdki = gwiazdki_element.text
            else:
                gwiazdki = "Brak gwiazdek"

            # Zabezpieczenie przed brakiem daty
            data_element = opinia.find("span", class_="user-post__published")
            if data_element:
                data = data_element.text
            else:
                data = "Brak daty"

            # Zabezpieczenie przed brakiem treści
            tresc_element = opinia.find("div", class_="user-post__text")
            if tresc_element:
                tresc = tresc_element.text
            else:
                tresc = "Brak treści"

            writer.writerow([autor, rekomendacja, gwiazdki, data, tresc])

def _analiza_statystyczna(opinie):
    """
    Przeprowadza analizę statystyczną pobranych opinii.

    Args:
        opinie: Lista opinii w formacie BeautifulSoup.

    Returns:
        Słownik z wynikami analizy.
    """

    # Obliczanie średniej oceny
    oceny = [float(Fraction(re.search(r'\d+(?:[.,]\d+)?', opinia.find("span", class_="user-post__score-count").text.replace(",", ".")).group())) for opinia in opinie]
    if len(oceny) > 0:
        średnia_ocena = sum(oceny) / len(oceny)
    else:
        return "Brak ocen do analizy"

    # Dystrybucja ocen
    dystrybucja_ocen = Counter(oceny)

    return {
        "średnia_ocena": średnia_ocena,
        "dystrybucja_ocen": dystrybucja_ocen,
    }

def wyswietl_wykresy(oceny, dystrybucja_ocen):
    # Wykres średniej oceny
    plt.figure(figsize=(8, 6))
    plt.bar(["Średnia ocena"], [oceny], color='skyblue')
    plt.title("Średnia ocena")
    plt.ylabel("Ocena")
    plt.ylim(0, 5)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    # Wykres dystrybucji ocen
    plt.figure(figsize=(8, 6))
    oceny = list(dystrybucja_ocen.keys())
    ilosci = list(dystrybucja_ocen.values())
    plt.bar(oceny, ilosci, color='lightgreen')
    plt.title("Dystrybucja ocen")
    plt.xlabel("Ocena")
    plt.ylabel("Ilość opinii")
    plt.xticks(range(1, 6))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

def main():
    # Kod EAN produktu
    ean = input("Podaj kod EAN produktu: ")

    # Pobieranie i parsowanie strony produktu
    url = f"https://www.ceneo.pl/{ean}"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    # Pobieranie opinii z pierwszej strony
    opinie = pobierz_opinie(url)

    # Inicjowanie licznika stron
    liczba_stron = 1

    # Iterowanie po stronach do momentu powtórzenia pierwszej strony
    while opinie:
        liczba_stron += 1
        opinie = pobierz_opinie(f"{url}/opinie-{liczba_stron}")
        if opinie == pobierz_opinie(url):
            break

    # Iteracja po opiniach z pierwszej strony i wyświetlanie danych
    for opinia in opinie:
        # Zabezpieczenie przed brakiem autora
        autor_element = opinia.find("span", class_="user-post__author-name")
        if autor_element:
            autor = autor_element.text
        else:
            autor = "Brak autora"

        # Zabezpieczenie przed brakiem rekomendacji
        rekomendacja_element = opinia.find("span", class_="user-post__author-recomendation")
        if rekomendacja_element:
            rekomendacja = rekomendacja_element.text
        else:
            rekomendacja = "Brak rekomendacji"

        # Zabezpieczenie przed brakiem gwiazdek
        gwiazdki_element = opinia.find("span", class_="user-post__score-count")
        if gwiazdki_element:
            gwiazdki = gwiazdki_element.text
        else:
            gwiazdki = "Brak gwiazdek"

        # Zabezpieczenie przed brakiem daty
        data_element = opinia.find("span", class_="user-post__published")
        if data_element:
            data = data_element.text
        else:
            data = "Brak daty"

        # Zabezpieczenie przed brakiem treści
        tresc_element = opinia.find("div", class_="user-post__text")
        if tresc_element:
            tresc = tresc_element.text
        else:
            tresc = "Brak treści"

        # Wyświetlenie danych
        print(f"Autor: {autor}")
        print(f"Rekomendacja: {rekomendacja}")
        print(f"Liczba gwiazdek: {gwiazdki}")
        print(f"Data: {data}")
        print(f"Treść: {tresc}")
        print()

    # Pobieranie opinii z kolejnych stron
    for i in range(2, liczba_stron):
        opinie += pobierz_opinie(f"{url}/opinie-{i}")

        # Wyświetlanie opinii
        for opinia in opinie:
            # Zabezpieczenie przed brakiem autora
            autor_element = opinia.find("span", class_="user-post__author-name")
            if autor_element:
                autor = autor_element.text
            else:
                autor = "Brak autora"

            # Zabezpieczenie przed brakiem rekomendacji
            rekomendacja_element = opinia.find("span", class_="user-post__author-recomendation")
            if rekomendacja_element:
                rekomendacja = rekomendacja_element.text
            else:
                rekomendacja = "Brak rekomendacji"

            # Zabezpieczenie przed brakiem gwiazdek
            gwiazdki_element = opinia.find("span", class_="user-post__score-count")
            if gwiazdki_element:
                gwiazdki = gwiazdki_element.text
            else:
                gwiazdki = "Brak gwiazdek"

            # Zabezpieczenie przed brakiem daty
            data_element = opinia.find("span", class_="user-post__published")
            if data_element:
                data = data_element.text
            else:
                data = "Brak daty"

            # Zabezpieczenie przed brakiem treści
            tresc_element = opinia.find("div", class_="user-post__text")
            if tresc_element:
                tresc = tresc_element.text
            else:
                tresc = "Brak treści"

            # Wyświetlenie danych
            print(f"Autor: {autor}")
            print(f"Rekomendacja: {rekomendacja}")
            print(f"Liczba gwiazdek: {gwiazdki}")
            print(f"Data: {data}")
            print(f"Treść: {tresc}")
            print()

    # Zapis opinii do pliku JSON
    zapisz_do_json(opinie, "opinie.json")

    # Zapis opinii do pliku CSV
    zapisz_do_csv(opinie, "opinie.csv")

    # Wywołanie analizy statystycznej
    wyniki_statystyczne = _analiza_statystyczna(opinie)

    # Zapis wyników analizy statystycznej do pliku JSON
    with open("wyniki_statystyczne.json", "w", encoding="utf-8") as f:
        json.dump(wyniki_statystyczne, f, indent=4)

    # Wyświetlenie wykresów
    if "dystrybucja_ocen" in wyniki_statystyczne:
        wyswietl_wykresy(wyniki_statystyczne["średnia_ocena"], wyniki_statystyczne["dystrybucja_ocen"])
    else:
        print("Brak danych do wyświetlenia wykresów.")

if __name__ == "__main__":
    main()