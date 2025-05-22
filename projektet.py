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
            "namn": person._namn,
            "email": person.get_email(),
            "lösenord": person.get_lösenord(),
            "saldo": 0,
            "kundvagn": [],
            "historik": []
        })
        with open("slutprojektet/konto.json", "w", encoding="utf-8") as file:
            json.dump(konton, file, indent = 4) 
    
class Person(Konto):       
    def __init__(self, namn, saldo, email, lösenord):
        super().__init__(namn, email, lösenord) 
        self.__saldo = saldo
        self.produkt_kundvagn  = []
        
    def set_saldo(self, saldo):
        self.__saldo = saldo
    
    def get_saldo(self):
        return self.__saldo  
    
    def uppdatera_kundvagn(namn, ny_kundvagn):
        konton = Konto.hämta_konton()
        for konto in konton:
            if konto["namn"] == namn:
                konto["kundvagn"] = ny_kundvagn
                break
        with open("slutprojektet/konto.json", "w", encoding="utf-8") as file:
            json.dump(konton, file, indent=4)
    
    def lägg_till(self, produkt_id):
        temp_api = ProduktAPI()
        produkter_data = temp_api.hämta_produktdata()
        for produkt in produkter_data:
            if produkt["id"] == produkt_id:
                self.produkt_kundvagn.append(produkt)
                Person.uppdatera_kundvagn(self._namn, self.produkt_kundvagn)
                break
    
    @staticmethod
    def uppdatera_saldo(namn, nytt_saldo):
        konton = Konto.hämta_konton()

        for konto in konton:
            if konto["namn"] == namn:
                konto["saldo"] = nytt_saldo
                break 

        with open("slutprojektet/konto.json", "w", encoding="utf-8") as file:
            json.dump(konton, file, indent = 4)

    def sätt_in_saldo(self, belopp):
        if belopp >= 0:
            self.__saldo += belopp
            Person.uppdatera_saldo(self._namn, self.__saldo)
            
    def checkout(self, total_summa):
        self.set_saldo(self.get_saldo() - total_summa)
        self.uppdatera_saldo(self._namn, self.get_saldo())

        konton = Konto.hämta_konton()
        for konto in konton:
            if konto["namn"] == self._namn:
                konto["historik"].extend(self.produkt_kundvagn)
                konto["kundvagn"] = []  
                break

        with open("slutprojektet/konto.json", "w", encoding="utf-8") as file:
            json.dump(konton, file, indent=4, ensure_ascii=False)

        self.produkt_kundvagn = []     
        
    @classmethod
    def hämta_person(cls, namn, konton):
        for k in konton:
            if k["namn"] == namn:
                person = cls(
                    namn = k["namn"],
                    email = k["email"],
                    lösenord = k["lösenord"],
                    saldo = float(k["saldo"])
                )
                person.produkt_kundvagn = k.get("kundvagn", [])
                return person
        return None       
        
class ProduktAPI():
    def __init__(self):
        self.api_url = "https://dummyjson.com/products?limit=194"
        
    def hämta_produktdata(self, antal = 194): 
        try:
            response = requests.get(self.api_url, timeout=5) 
            response.raise_for_status() 
            data = response.json()
            return data.get("products", [])[:antal]
        except requests.exceptions.RequestException as e:
            print(f"Något gick fel vid hämtning av produkter: {e}")
            return [] 
                
class Produkt(ProduktAPI):
    def __init__(self, produkt_namn, produkt_pris, produkt_beskrivning, produkt_bild, produkt_kategori, produkt_id):
        super().__init__()
        self.produkt_namn = produkt_namn
        self.produkt_pris = produkt_pris
        self.produkt_beskrivning = produkt_beskrivning
        self.produkt_bild = produkt_bild
        self.produkt_kategori = produkt_kategori  
        self.produkt_id = produkt_id
        
    def visa_info(self):
        print(f"Namn: {self.produkt_namn}")
        print(f"Pris: {self.produkt_pris} USD")
        print(f"Beskrivning: {self.produkt_beskrivning}")
        print(f"Bild: {self.produkt_bild}")
        print(f"Kategori: {self.produkt_kategori}")
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
                produkt_bild = p["thumbnail"],
                produkt_kategori = p["category"],
                produkt_id = p["id"]
            )
            produkt_lista.append(produkt)
            

        return produkt_lista    

    def visa_kategorier():
        temp_api = ProduktAPI()
        produkter_data = temp_api.hämta_produktdata(antal = 194)
        kategorier = sorted({p["category"] for p in produkter_data})
        return kategorier

  
@app.route("/", methods=["GET"])
def home():
    produkter = Produkt.skapa_produkter_från_api()
    
    return render_template('main.html', 
        produkter = produkter,
        view_type = "not_loggin"
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
                    return redirect(url_for("main", name = k["namn"]))
            return render_template("log.html", fel = "Fel e-post eller lösenord.")

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
    
@app.route("/All-in-One-Shop/log/välkomna-<name>", methods=["GET", "POST"])
def main(name):
    
    konton = Konto.hämta_konton()
    
    for k in konton:
        if k["namn"] == name:
            person = Person.hämta_person(name, konton)
            
            if request.method == "POST":
                form_type = request.form.get("form-type")
                if form_type == "saldo":
                    try:
                        belopp = float(request.form.get("deposit"))
                        if belopp >= 0:
                            person.sätt_in_saldo(belopp)
                    except (ValueError, TypeError):
                        pass
                elif form_type == "köp":
                    try:
                        produkt_id = int(request.form.get("produkt_id"))
                        person.lägg_till(produkt_id)

                    except (ValueError, TypeError):
                        return render_template("log.html",
                            fel = "Felaktigt produkt-ID"
                        )   
                elif form_type == "checkout":
                    total_summa = sum(p["price"] for p in person.produkt_kundvagn)

                    if person.get_saldo() >= total_summa:
                        person.checkout(total_summa)
                        
                    else:
                        return render_template("main.html",
                            fel = "Inte tillräckligt med saldo.",
                            namn = name,
                            saldo = person.get_saldo(),
                            kundvagn = person.produkt_kundvagn,
                        )
         
            produkter = Produkt.skapa_produkter_från_api()
            return render_template("main.html", 
                produkter = produkter, 
                namn = name, 
                saldo = person.get_saldo(),
                kundvagn = person.produkt_kundvagn,
                view_type = "produkter"
            )

    return "Konto hittades inte"


@app.route("/All-in-One-Shop/log/<namn>/kategorier", methods=["GET", "POST"])
def kategorier(namn):
    
    konton = Konto.hämta_konton()
    for k in konton:
         if k["namn"] == namn:
            person = Person.hämta_person(namn, konton)
            
            if request.method == "POST":
                form_type = request.form.get("form-type")
                if form_type == "saldo":
                    try:
                        belopp = float(request.form.get("deposit"))
                        if belopp >= 0:
                            person.sätt_in_saldo(belopp)
                    except (ValueError, TypeError):
                        pass
                elif form_type == "checkout":
                    total_summa = sum(p["price"] for p in person.produkt_kundvagn)

                    if person.get_saldo() >= total_summa:
                        person.checkout(total_summa)
                    else:
                        return render_template("main.html",
                            fel = "Inte tillräckligt med saldo.",
                            kategorier = alla_kategorier,
                            namn = namn,
                            saldo = person.get_saldo(),
                            kundvagn = person.produkt_kundvagn,
                        )               
        
    alla_kategorier = Produkt.visa_kategorier()
    return render_template("main.html", 
        kategorier = alla_kategorier,
        namn = namn,
        saldo = person.get_saldo(),
        kundvagn = person.produkt_kundvagn,
        view_type = "kategorier"
    )
    
@app.route("/All-in-One-Shop/log/<namn>/kategorier/<kategorier_namn>", methods=["GET", "POST"])
def kategorier_namn(kategorier_namn, namn):    
    
    produkter = Produkt.skapa_produkter_från_api()
    produkter_i_kategori = [p for p in produkter if p.produkt_kategori == kategorier_namn]

    konton = Konto.hämta_konton()
    for k in konton:
        if k["namn"] == namn:
            person = Person.hämta_person(namn, konton)
            
            if request.method == "POST":
                form_type = request.form.get("form-type")
                if form_type == "saldo":
                    try:
                        belopp = float(request.form.get("deposit"))
                        if belopp >= 0:
                            person.sätt_in_saldo(belopp)
                    except (ValueError, TypeError):
                        pass
                elif form_type == "köp":
                    try:
                        produkt_id = int(request.form.get("produkt_id"))
                        person.lägg_till(produkt_id)

                    except (ValueError, TypeError):
                        return render_template("log.html",
                            fel = "Felaktigt produkt-ID"
                        )
                elif form_type == "checkout":
                    total_summa = sum(p["price"] for p in person.produkt_kundvagn)

                    if person.get_saldo() >= total_summa:
                        person.checkout(total_summa)
                    else:
                        return render_template("main.html",
                            fel = "Inte tillräckligt med saldo.",
                            namn = namn,
                            saldo = person.get_saldo(),
                            kundvagn = person.produkt_kundvagn,
                        )                       
    
    return render_template("main.html",  
        produkters = produkter_i_kategori,
        namn = namn,
        saldo = person.get_saldo(),
        kundvagn = person.produkt_kundvagn,
        view_type = "kategorier_produkter"
    )   
    
@app.route("/All-in-One-Shop/log/<name>/produkt-historik", methods=["GET", "POST"])
def historik(name):
    konton = Konto.hämta_konton()

    for k in konton:
        if k["namn"] == name:
            person = Person.hämta_person(name, konton)
            historik = k.get("historik", [])

            if request.method == "POST":
                form_type = request.form.get("form-type")
                if form_type == "rensa":
                    for konto in konton:
                        if konto["namn"] == name:
                            konto["historik"] = []
                            break

                    with open("slutprojektet/konto.json", "w", encoding="utf-8") as f:
                        json.dump(konton, f, indent=4, ensure_ascii=False)

                    historik = []
                elif form_type == "saldo":
                    try:
                        belopp = float(request.form.get("deposit"))
                        if belopp >= 0:
                            person.sätt_in_saldo(belopp)
                    except (ValueError, TypeError):
                        pass
                elif form_type == "checkout":
                    total_summa = sum(p["price"] for p in person.produkt_kundvagn)

                    if person.get_saldo() >= total_summa:
                        person.checkout(total_summa)
                        
                    else:
                        return render_template("main.html",
                            fel = "Inte tillräckligt med saldo.",
                            namn = name,
                            saldo = person.get_saldo(),
                            kundvagn = person.produkt_kundvagn,
                        )        

            return render_template("main.html", 
                namn = name, 
                historik = historik,
                kundvagn = person.produkt_kundvagn,
                saldo = person.get_saldo(), 
                view_type = "historik"
            )

    return "Konto hittades inte" 
    
@app.route('/ta_bort/<namn>/<int:produkt_id>')
def ta_bort_produkt(namn, produkt_id):
    with open("slutprojektet/konto.json", "r", encoding="utf-8") as f:
        konton = json.load(f)

    for konto in konton:
        if konto["namn"] == namn:
            konto["kundvagn"] = [p for p in konto["kundvagn"] if p.get("id") != produkt_id]
            break  

    with open("slutprojektet/konto.json", "w", encoding="utf-8") as f:
        json.dump(konton, f, indent=4, ensure_ascii=False)

    return redirect(url_for('main', name = namn))


if __name__ == "__main__":
    app.run(debug=True)