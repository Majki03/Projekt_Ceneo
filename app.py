from flask import Flask, render_template, request, redirect, url_for, flash
from ceneo import ekstrakcja_opinii_po_ean, _analiza_statystyczna, pobierz_opinie, wyswietl_wykresy
import json
import csv

app = Flask(__name__, template_folder=".")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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
        if request.form.get("zapisz_wykresy") == "True":
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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ekstrakcja", methods=['GET', 'POST'])
def ekstrakcja_opinii():
    if request.method == 'POST':
        ean = request.form['ean']
        if ean.strip() == '':
            flash('Pole kodu EAN nie może być puste!', 'error')
        else:
            opinie = ekstrakcja_opinii_po_ean(ean)
            if opinie is None:
                flash('Błędny kod EAN!', 'error')
            else:
                zapisz_do_json(opinie, "opinie.json")
                return redirect(url_for('ekstrakcja_opinii'))
    return render_template("ekstrakcja.html")

@app.route("/ekstrakcja_opinii", methods=['GET', 'POST'])
def ekstrakcja():
    if request.method == 'POST':
        # Kod obsługujący filtrowanie opinii po dowolnej kolumnie
        filtr = request.form.get('filtr')
        wartosc_filtru = request.form.get('wartosc_filtru')
        opinie = filtruj_opinie(filtr, wartosc_filtru)
    else:
        # Pobranie opinii
        with open("opinie.json", "r") as f:
            opinie = json.load(f)
    return render_template("ekstrakcja_opinii.html", opinie=opinie)

def filtruj_opinie(filtr, wartosc):
    with open("opinie.json", "r") as f:
        opinie = json.load(f)
    
    if filtr == 'autor':
        return [opinia for opinia in opinie if opinia['autor'].lower() == wartosc.lower()]
    elif filtr == 'rekomendacja':
        return [opinia for opinia in opinie if opinia['rekomendacja'].lower() == wartosc.lower()]
    elif filtr == 'liczba_gwiazdek':
        return [opinia for opinia in opinie if opinia['gwiazdki'].lower() == wartosc.lower()]
    # Dodaj inne możliwe filtry według potrzeb
    else:
        return opinie

@app.route("/wykresy", methods=['POST'])
def wykresy():
    return render_template("wykresy.html")

@app.route("/zapisz_do_json", methods=['POST'])
def zapisz_do_json_view():
    opinie = json.loads(request.form['opinie'])
    zapisz_do_json(opinie, "opinie.json")
    flash('Opinie zostały zapisane do pliku JSON!', 'success')
    return redirect(url_for('ekstrakcja_opinii'))

@app.route("/zapisz_do_csv", methods=['POST'])
def zapisz_do_csv_view():
    opinie = json.loads(request.form['opinie'])
    zapisz_do_csv(opinie, "opinie.csv")
    flash('Opinie zostały zapisane do pliku CSV!', 'success')
    return redirect(url_for('ekstrakcja_opinii'))

"""
@app.route("/lista_produktow")
def lista_produktow():
    # Inicjalizacja listy produktów
    produkty = []

    # Pobranie opinii
    with open("opinie.json", "r", encoding="utf-8") as f:
        opinie = json.load(f)

    if request.method == "POST":
        akcja = request.form.get("akcja")
        if akcja == "zapisz_json":
            # Pobranie opinii
            with open("opinie.json", "r", encoding="utf-8") as f:
                opinie = json.load(f)

            # Zapisanie opinii do pliku JSON
            zapisz_do_json(opinie, "opinie.json")

        elif akcja == "zapisz_csv":
            # Pobranie opinii
            with open("opinie.json", "r", encoding="utf-8") as f:
                opinie = json.load(f)

            # Zapisanie opinii do pliku CSV
            zapisz_do_csv(opinie, "opinie.csv")

    # Tworzenie obiektów produktów
    for opinia in opinie:
        ean = opinia.get['ean'] 
        produkt = Produkt(ean)
        produkt.nazwa = 'Nazwa Produktu'  # Pobierz nazwę produktu z serwisu Ceneo lub innej platformy
        produkt.liczba_opinii = len(opinie)
        produkt.liczba_wad = sum(len(opinia['wady']) for opinia in opinie)
        produkt.liczba_zalet = sum(len(opinia['zalety']) for opinia in opinie)
        oceny = [float(opinia['gwiazdki'].replace(',', '.')) for opinia in opinie]
        produkt.srednia_ocena = sum(oceny) / len(oceny)
        produkt.url = f"https://www.ceneo.pl/{ean}"  # Ustawienie URL do produktu
        produkty.append(produkt)

    return render_template("lista_produktow.html", produkty=produkty)
"""

@app.route("/o_autorze")
def about():
    return render_template("o_autorze.html")

if __name__ == "__main__":
    app.run(debug=True)