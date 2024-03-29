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

def ekstrakcja_opinii_po_ean(ean, zapisz_wykresy=False):
    """
    Ekstrahuje opinie na podstawie kodu EAN.

    Args:
        ean: Kod EAN produktu.

    Returns:
        Lista opinii na temat produktu.
    """
    url = f"https://www.ceneo.pl/{ean}"
    opinie = pobierz_opinie(url)

    # Iterowanie po stronach do momentu powtórzenia pierwszej strony
    liczba_stron = 1
    while opinie:
        liczba_stron += 1
        opinie.extend(pobierz_opinie(f"{url}/opinie-{liczba_stron}"))
        if opinie == pobierz_opinie(url):
            break
    
    if opinie:
        zapisz_do_json(opinie, "opinie.json")
        if zapisz_wykresy:
            wyniki_analizy = _analiza_statystyczna(opinie)
            if isinstance(wyniki_analizy, dict):
                oceny = wyniki_analizy.get("średnia_ocena")
                dystrybucja_ocen = wyniki_analizy.get("dystrybucja_ocen")
                wyswietl_wykresy(oceny, dystrybucja_ocen)
        return opinie
    else:
        return None

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
    id_opinii_element = opinia.get("data-entry-id")
    id_opinii = id_opinii_element if id_opinii_element else "Brak ID"

    autor_element = opinia.find("span", class_="user-post__author-name")
    autor = autor_element.text.strip() if autor_element else "Brak autora"

    rekomendacja_element = opinia.find("span", class_="user-post__author-recomendation")
    rekomendacja = rekomendacja_element.text.strip() if rekomendacja_element else "Brak rekomendacji"

    gwiazdki_element = opinia.find("span", class_="user-post__score-count")
    gwiazdki = gwiazdki_element.text.strip() if gwiazdki_element else "Brak gwiazdek"
    
    data_wystawienia_element = opinia.find_all("time", {"datetime": True})
    data_wystawienia = data_wystawienia_element[0].text.strip() if data_wystawienia_element else "Brak danych"

    czas_od_zakupu = "Brak danych"
    if len(data_wystawienia_element) > 1:
        czas_od_zakupu = data_wystawienia_element[1].text.strip()

    potwierdzony_zakup = "Nie zakupiono"
    if czas_od_zakupu != "Brak danych":
        potwierdzony_zakup = "Potwierdzone zakupem"

    pomocna_element = opinia.find("button", class_="vote-yes js_product-review-vote js_vote-yes")
    pomocna = pomocna_element.text.strip() if pomocna_element else "Brak danych"

    nie_pomocna_element = opinia.find("button", class_="vote-no js_product-review-vote js_vote-no")
    nie_pomocna = nie_pomocna_element.text.strip() if nie_pomocna_element else "Brak danych"

    tresc_element = opinia.find("div", class_="user-post__text")
    tresc = tresc_element.text.strip() if tresc_element else "Brak treści"

    wady_element = opinia.find("div", class_="review-feature__title--negatives")
    wady = []
    if wady_element:
        wady = [wada.text.strip() for wada in wady_element.find_next_sibling("div", class_="review-feature__item")]

    zalety_element = opinia.find("div", class_="review-feature__title--positives")
    zalety = []
    if zalety_element:
        zalety = [zaleta.text.strip() for zaleta in zalety_element.find_next_sibling("div", class_="review-feature__item")]

    return {
        "id": id_opinii,
        "autor": autor,
        "rekomendacja": rekomendacja,
        "gwiazdki": gwiazdki,
        "data_wystawienia": data_wystawienia,
        "czas_od_zakupu": czas_od_zakupu,
        "potwierdzony_zakup": potwierdzony_zakup,
        "pomocna": pomocna,
        "nie_pomocna": nie_pomocna,
        "tresc": tresc,
        "wady": wady,
        "zalety": zalety,
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
        writer.writerow(["ID", "Autor", "Rekomendacja", "Liczba gwiazdek", "Data wystawienia", "Czas od zakupu", "Potwierdzony zakup", "Pomocna", "Niepomocna", "Treść", "Wady", "Zalety"])
        
        # Pobranie danych z opinii
        for opinia in opinie:
            # Zabezpieczenie przed brakiem ID
            id_opinii = opinia.get("data-entry-id", "Brak ID")

            # Zabezpieczenie przed brakiem autora
            autor_element = opinia.find("span", class_="user-post__author-name")
            autor = autor_element.text.strip() if autor_element else "Brak autora"

            # Zabezpieczenie przed brakiem rekomendacji
            rekomendacja_element = opinia.find("span", class_="user-post__author-recomendation")
            rekomendacja = rekomendacja_element.text.strip() if rekomendacja_element else "Brak rekomendacji"

            # Zabezpieczenie przed brakiem gwiazdek
            gwiazdki_element = opinia.find("span", class_="user-post__score-count")
            gwiazdki = gwiazdki_element.text.strip() if gwiazdki_element else "Brak gwiazdek"

            # Zabezpieczenie przed brakiem daty
            data_element = opinia.find("span", class_="user-post__published")
            data = data_element.text.strip() if data_element else "Brak daty"

            # Zabezpieczenie przed brakiem daty wystawienia i czasu od zakupu
            czas_od_zakupu_element = opinia.find_all("time", {"datetime": True})
            data_wystawienia = "Brak danych"
            czas_od_zakupu = "Brak danych"
            if len(czas_od_zakupu_element) > 1:
                data_wystawienia = czas_od_zakupu_element[0].text.strip()
                czas_od_zakupu = czas_od_zakupu_element[1].text.strip()

            # Potwierdzenie zakupu
            potwierdzony_zakup = "Nie zakupiono"
            if czas_od_zakupu != "Brak danych":
                potwierdzony_zakup = "Potwierdzone zakupem"

            # Punktacja pomocna i niepomocna
            pomocna_element = opinia.find("button", class_="vote-yes js_product-review-vote js_vote-yes")
            pomocna = pomocna_element.text.strip() if pomocna_element else "Brak danych"
            nie_pomocna_element = opinia.find("button", class_="vote-no js_product-review-vote js_vote-no")
            nie_pomocna = nie_pomocna_element.text.strip() if nie_pomocna_element else "Brak danych"

            # Zabezpieczenie przed brakiem treści
            tresc_element = opinia.find("div", class_="user-post__text")
            tresc = tresc_element.text.strip() if tresc_element else "Brak treści"

            # Wady
            wady_element = opinia.find("div", class_="review-feature__title--negatives")
            wady = []
            if wady_element:
                for item in wady_element.find_all_next("div", class_="review-feature__item"):
                    wady.append(item.text.strip())
            wady_str = ", ".join(wady)

            # Zalety
            zalety_element = opinia.find("div", class_="review-feature__title--positives")
            zalety = []
            if zalety_element:
                for item in zalety_element.find_all_next("div", class_="review-feature__item"):
                    zalety.append(item.text.strip())
            zalety_str = ", ".join(zalety)

            writer.writerow([id_opinii, autor, rekomendacja, gwiazdki, data, data_wystawienia, czas_od_zakupu, potwierdzony_zakup, pomocna, nie_pomocna, tresc, wady_str, zalety_str])

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
    plt.pie([oceny], labels=["Średnia ocena"], colors=['skyblue'], autopct='%1.1f%%', startangle=140)
    plt.title("Średnia ocena")
    plt.axis('equal')  # Equal aspect ratio to ensure that pie is drawn as a circle
    plt.savefig('static/srednia_ocena.jpg')  # Zapisz wykres jako JPG
    plt.close()  # Zamknij bieżący wykres

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
    plt.savefig('static/dystrybucja_ocen.jpg')  # Zapisz wykres jako JPG
    plt.close()  # Zamknij bieżący wykres

class Produkt:
    def __init__(self, ean):
        self.ean = ean
        self.opinie = []

    def dodaj_opinie(self, opinie):
        self.opinie.extend(opinie)

class Opinia:
    def __init__(self, id_opinii, autor, rekomendacja, gwiazdki, potwierdzony_zakup, data_wystawienia, czas_od_zakupu, pomocna, nie_pomocna, tresc, wady, zalety):
        self.id_opinii = id_opinii
        self.autor = autor
        self.rekomendacja = rekomendacja
        self.gwiazdki = gwiazdki
        self.potwierdzony_zakup = potwierdzony_zakup
        self.data_wystawienia = data_wystawienia
        self.czas_od_zakupu = czas_od_zakupu
        self.pomocna = pomocna
        self.nie_pomocna = nie_pomocna
        self.tresc = tresc
        self.wady = wady
        self.zalety = zalety

def main():
    # Kod EAN produktu
    ean = input("Podaj kod EAN produktu: ")

    # Tworzenie obiektu produktu
    produkt = Produkt(ean)

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
        id_opinii = opinia.get("data-entry-id")
        autor = opinia.find("span", class_="user-post__author-name").text.strip()
        rekomendacja_element = opinia.find("span", class_="user-post__author-recomendation")
        rekomendacja = rekomendacja_element.text.strip() if rekomendacja_element is not None else "Brak rekomendacji"
        gwiazdki = opinia.find("span", class_="user-post__score-count").text.strip()
        potwierdzony_zakup = "Nie zakupiono"
        data_wystawienia = opinia.find("time", {"datetime": True})
        czasy_elementy = opinia.find_all("time", {"datetime": True})
        pomocna_element = opinia.find("button", class_="vote-yes js_product-review-vote js_vote-yes")
        pomocna = pomocna_element.text.strip() if pomocna_element is not None else "Brak danych"
        nie_pomocna_element = opinia.find("button", class_="vote-no js_product-review-vote js_vote-no")
        nie_pomocna = nie_pomocna_element.text.strip() if nie_pomocna_element is not None else "Brak danych"
        tresc = opinia.find("div", class_="user-post__text").text.strip()
        wady_element = opinia.find("div", class_="review-feature__title--negatives")
        wady = []
        zalety_element = opinia.find("div", class_="review-feature__title--positives")
        zalety = []

        # Uwzględnienie braku danych
        if not id_opinii:
            id_opinii = "Brak ID"
        if not autor:
            autor = "Brak autora"
        if not rekomendacja:
            rekomendacja = "Brak rekomendacji"
        if not gwiazdki:
            gwiazdki = "Brak gwiazdek"
        if czasy_elementy:
            potwierdzony_zakup = "Potwierdzenie zakupu"
        if not data_wystawienia:
            data_wystawienia = "Brak daty wystawienia opinii"
        if len(czasy_elementy) > 1:
            czas_od_zakupu_element = czasy_elementy[1]
            czas_od_zakupu = czas_od_zakupu_element.text.strip() if czas_od_zakupu_element else "Brak danych"
        else:
            czas_od_zakupu = "Brak danych"
        if not pomocna:
            pomocna = "Brak liczby pozytywnych reakcji"
        if not nie_pomocna:
            nie_pomocna = "Brak liczby negatywnych reakcji"
        if not tresc:
            tresc = "Brak treści"
        if wady_element:
            wady = [wada.text.strip() for wada in wady_element.find_next_sibling("div", class_="review-feature__item")]
        if not wady_element:
            wady_element = "Brak wad"
        if zalety_element:
            zalety = [zaleta.text.strip() for zaleta in zalety_element.find_next_sibling("div", class_="review-feature__item")]
        if not zalety_element:
            zalety_element = "Brak zalet"

        # Tworzenie obiektu opinii
        nowa_opinia = Opinia(id_opinii, autor, rekomendacja, gwiazdki, potwierdzony_zakup, data_wystawienia, czas_od_zakupu, pomocna, nie_pomocna, tresc, wady, zalety)
        # Dodawanie opinii do produktu
        produkt.dodaj_opinie([nowa_opinia])

        print(f"ID: {id_opinii}")
        print(f"Autor: {autor}")
        print(f"Rekomendacja: {rekomendacja}")
        print(f"Liczba gwiazdek: {gwiazdki}")
        print(f"{potwierdzony_zakup}")
        print(f"Data wystawienia opinii: {data_wystawienia}")
        print(f"Data zakupu: {czas_od_zakupu}")
        print(f"Liczba pozytywnych reakcji: {pomocna}")
        print(f"Liczba neagtywnych reakcji: {nie_pomocna}")
        print(f"Treść: {tresc}")
        print(f"Wady: {wady}")
        print(f"Zalety: {zalety}")
        print()

    for i in range(2, liczba_stron):
        opinie += pobierz_opinie(f"{url}/opinie-{i}")

        for opinia in opinie:
            id_opinii = opinia.get("data-entry-id")
            autor = opinia.find("span", class_="user-post__author-name").text.strip()
            rekomendacja_element = opinia.find("span", class_="user-post__author-recomendation")
            rekomendacja = rekomendacja_element.text.strip() if rekomendacja_element is not None else "Brak rekomendacji"
            gwiazdki = opinia.find("span", class_="user-post__score-count").text.strip()
            potwierdzony_zakup = "Nie zakupiono"
            data_wystawienia = opinia.find("time", {"datetime": True})
            czasy_elementy = opinia.find_all("time", {"datetime": True})
            pomocna_element = opinia.find("button", class_="vote-yes js_product-review-vote js_vote-yes")
            pomocna = pomocna_element.text.strip() if pomocna_element is not None else "Brak danych"
            nie_pomocna_element = opinia.find("button", class_="vote-no js_product-review-vote js_vote-no")
            nie_pomocna = nie_pomocna_element.text.strip() if nie_pomocna_element is not None else "Brak danych"
            tresc = opinia.find("div", class_="user-post__text").text.strip()
            wady_element = opinia.find("div", class_="review-feature__title--negatives")
            wady = []
            zalety_element = opinia.find("div", class_="review-feature__title--positives")
            zalety = []

            # Uwzględnienie braku danych
            if not id_opinii:
                id_opinii = "Brak ID"
            if not autor:
                autor = "Brak autora"
            if not rekomendacja:
                rekomendacja = "Brak rekomendacji"
            if not gwiazdki:
                gwiazdki = "Brak gwiazdek"
            if czasy_elementy:
                potwierdzony_zakup = "Potwierdzenie zakupu"
            if not data_wystawienia:
                data_wystawienia = "Brak daty wystawienia opinii"
            if len(czasy_elementy) > 1:
                czas_od_zakupu_element = czasy_elementy[1]
                czas_od_zakupu = czas_od_zakupu_element.text.strip() if czas_od_zakupu_element else "Brak danych"
            else:
                czas_od_zakupu = "Brak danych"
            if not pomocna:
                pomocna = "Brak liczby pozytywnych reakcji"
            if not nie_pomocna:
                nie_pomocna = "Brak liczby negatywnych reakcji"
            if not tresc:
                tresc = "Brak treści"
            if wady_element:
                wady = [wada.text.strip() for wada in wady_element.find_next_sibling("div", class_="review-feature__item")]
            if not wady_element:
                wady_element = "Brak wad"
            if zalety_element:
                zalety = [zaleta.text.strip() for zaleta in zalety_element.find_next_sibling("div", class_="review-feature__item")]
            if not zalety_element:
                zalety_element = "Brak zalet"

            # Tworzenie obiektu opinii
            nowa_opinia = Opinia(id_opinii, autor, rekomendacja, gwiazdki, potwierdzony_zakup, data_wystawienia, czas_od_zakupu, pomocna, nie_pomocna, tresc, wady, zalety)
            # Dodawanie opinii do produktu
            produkt.dodaj_opinie([nowa_opinia])

            print(f"ID: {id_opinii}")
            print(f"Autor: {autor}")
            print(f"Rekomendacja: {rekomendacja}")
            print(f"Liczba gwiazdek: {gwiazdki}")
            print(f"{potwierdzony_zakup}")
            print(f"Data wystawienia opinii: {data_wystawienia}")
            print(f"Data zakupu: {czas_od_zakupu}")
            print(f"Liczba pozytywnych reakcji: {pomocna}")
            print(f"Liczba neagtywnych reakcji: {nie_pomocna}")
            print(f"Treść: {tresc}")
            print(f"Wady: {wady}")
            print(f"Zalety: {zalety}")
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