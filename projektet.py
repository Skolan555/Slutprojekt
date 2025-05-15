from flask import Flask, render_template
import requests

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
    
    def get_lösenordl(self):
        return self.__lösenord
    
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
    

@app.route("/All-in-One-Shop/log", methods=["GET"])
def logg():
    
    return render_template('log.html', 
    )

if __name__ == "__main__":
    app.run(debug=True)


"""
git add .
git commit -m "First py file"
git push

194 id, 24 category
"""