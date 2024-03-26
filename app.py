from flask import Flask, render_template, request
from test import main, ekstrakcja_opinii_po_ean
import json

app = Flask(__name__, template_folder=".")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ekstrakcja", methods=['GET', 'POST'])
def ekstrakcja_opinii():
    if request.method == 'POST':
        try:
            ean = request.form["ean"]
            if not ean:  # Sprawdzenie czy pole ean nie jest puste
                raise KeyError
            opinie = ekstrakcja_opinii_po_ean(ean)
            main(ean)
            return render_template("ekstrakcja.html", opinie=opinie)
        except KeyError:
            return render_template("ekstrakcja.html", error="Błędny kod EAN")
    else:
        return render_template("ekstrakcja.html")
    
def main_route():
    ean = request.args.get("ean")
    if ean:
        main(ean)

    return render_template("main.html")
    
@app.route("/ekstrakcja_opinii", methods=['POST'])
def ekstrakcja():
    # Pobranie opinii
    with open("opinie.json", "r") as f:
        opinie = json.load(f)

    return render_template("ekstrakcja_opinii.html", opinie=opinie)

@app.route("/o_autorze")
def about():
    return render_template("o_autorze.html")

if __name__ == "__main__":
    app.run(debug=True)