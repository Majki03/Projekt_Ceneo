from bs4 import BeautifulSoup
import requests

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
    return soup.find_all("div", class_="user-post user-post__card js_product-review")

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
            autor = "Brak informacji"

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
            gwiazdki = "Brak informacji"

        # Zabezpieczenie przed brakiem daty
        data_element = opinia.find("span", class_="user-post__published")
        if data_element:
            data = data_element.text
        else:
            data = "Brak informacji"

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
                autor = "Brak informacji"

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
                gwiazdki = "Brak informacji"

            # Zabezpieczenie przed brakiem daty
            data_element = opinia.find("span", class_="user-post__published")
            if data_element:
                data = data_element.text
            else:
                data = "Brak informacji"

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

if __name__ == "__main__":
    main()