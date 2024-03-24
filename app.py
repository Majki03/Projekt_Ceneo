from flask import Flask, render_template
import json

app = Flask(__name__, template_folder=".")

@app.route("/")
def index():
    # Pobranie wyników analizy
    with open("wyniki_statystyczne.json", "r") as f:
        wyniki_statystyczne = json.load(f)

    with open("opinie.json", "r") as f:
        opinie = json.load(f)
    
    # Przekazanie liczby opinii do kontekstu szablonu
    liczba_opinii = len(opinie)

    return render_template("index.html", wyniki=wyniki_statystyczne, liczba_opinii=liczba_opinii)

@app.route("/opinie")
def opinie():
    # Pobranie opinii
    with open("opinie.json", "r") as f:
        opinie = json.load(f)

    return render_template("opinie.html", opinie=opinie)

if __name__ == "__main__":
    app.run(debug=True)