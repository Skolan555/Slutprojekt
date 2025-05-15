from flask import Flask, redirect, render_template, request, url_for
import requests
import json
import os

app = Flask(__name__)

class Konto():
    def __init__(self, namn, email, lösenord):
        self._namn = namn
        self.__email = email
        self.__lösenord = lösenord
        
    def set_email(self, email):
        self.__email = email
    
    def get_email(self):
        return self.__email
    
    def set_lösenord(self, lösenord):
        self.__lösenord = lösenord
    
    def get_lösenord(self):
        return self.__lösenord
    
    @staticmethod
    def hämta_konton():
        path = "slutprojektet/konto.json"
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @classmethod
    def spara_konto(cls, person):
        konton = cls.hämta_konton()
        konton.append({
            "namn": person.get_namn(),
            "email": person.get_email(),
            "lösenord": person.get_lösenord(),
            "saldo": person.get_saldo()
        })
        with open("slutprojektet/konto.json", "w", encoding="utf-8") as file:
            json.dump(konton, file, indent=4) 
    
class Person(Konto):       
    def __init__(self, namn, saldo, produkt_kundvagn, inloggad):
        super().__init__(namn) 
        self.__saldo = saldo
        self.produkt_kundvagn  = produkt_kundvagn 
        self.inloggad = inloggad
        
    def set_saldo(self, saldo):
        self.__saldo = saldo
    
    def get_saldo(self):
        return self.__saldo  
        
class ProduktAPI():
    def __init__(self):
        self.api_url = "https://dummyjson.com/products"
        
    def hämta_produktdata(self, antal = 4): 
        try:
            response = requests.get(self.api_url, timeout=5) #Om inget svar kommer inom 5 sekunder, då ska den visa fel. 
            response.raise_for_status()  #Den kollar om svaret från API har en felkod.
            data = response.json()
            return data.get("products", [])[:antal]
        except requests.exceptions.RequestException as e:
            print(f"Något gick fel vid hämtning av produkter: {e}")
            return [] #Den ska returnerar en tom lista för att undvika att det förstöra resten av programmet.
                
        
class Produkt(ProduktAPI):
    def __init__(self, produkt_namn, produkt_pris, produkt_beskrivning, produkt_bild):
        super().__init__() # self från ProduktAPI
        self.produkt_namn = produkt_namn
        self.produkt_pris = produkt_pris
        self.produkt_beskrivning = produkt_beskrivning
        self.produkt_bild = produkt_bild
        
    def visa_info(self):
        print(f"Namn: {self.produkt_namn}")
        print(f"Pris: {self.produkt_pris} USD")
        print(f"Beskrivning: {self.produkt_beskrivning}")
        print(f"Bild: {self.produkt_bild}")
        print("-" * 40)
        
    @classmethod
    def skapa_produkter_från_api(cls):
        temp_api = ProduktAPI()
        produkter_data = temp_api.hämta_produktdata()
        produkt_lista = []

        for p in produkter_data:
            produkt = cls(
                produkt_namn = p["title"],
                produkt_pris = p["price"],
                produkt_beskrivning = p["description"],
                produkt_bild = p["thumbnail"]
            )
            produkt_lista.append(produkt)

        return produkt_lista    
  

@app.route("/All-in-One-Shop", methods=["GET"])
def home():
    produkter = Produkt.skapa_produkter_från_api()
    
    return render_template('display.html', 
        produkter = produkter
    )

@app.route("/All-in-One-Shop/log", methods=["GET", "POST"])
def logg():
    
    if request.method == "POST":
        form_type = request.form.get("form-type")
        
        if form_type == "login":
            email = request.form["email"]
            lösenord = request.form["password"]
            konton = Konto.hämta_konton()

            for k in konton:
                if k["email"] == email and k["lösenord"] == lösenord:
                    return redirect(url_for("main", name=k["namn"]))
            return render_template("log.html", fel="Fel e-post eller lösenord.")

        elif form_type == "signup":
            namn = request.form["name"]
            email = request.form["email"]
            lösenord = request.form["password"]
            confirm = request.form["confirm-password"]

            if lösenord != confirm:
                return render_template("log.html",
                    fel = "Lösenorden matchar inte."
                )
            
            nytt_konto = Konto(namn, email, lösenord)
            Konto.spara_konto(nytt_konto)
            return redirect(url_for("main", name = namn))

    return render_template("log.html")
    
@app.route("/All-in-One-Shop/log/välkomna-<name>", methods=["GET"])
def main(name):
    
    produkter = Produkt.skapa_produkter_från_api()
    return render_template("main.html", 
        produkter = produkter, 
        namn = name
    )

if __name__ == "__main__":
    app.run(debug=True)


"""
git add .
git commit -m "First py file"
git push

194 id, 24 category
"""