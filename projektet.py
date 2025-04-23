import requests

saldo = 0

class konto():
    def __init__(self, namn, email, lösenord, saldo):
        self._namn = namn
        self.__email = email
        self.__lösenord = lösenord
        self.__saldo = saldo
        
    def set_email(self, email):
        self.__email = email
    
    def get_email(self):
        return self.__email
    
    def set_lösenord(self, lösenord):
        self.__lösenord = lösenord
    
    def get_lösenordl(self):
        return self.__lösenord
        
    def set_saldo(self, saldo):
        self.__saldo = saldo
    
    def get_saldo(self):
        return self.__saldo        
        
class produkt():
    pass

def api_products():
    url = "https://dummyjson.com/products"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        products = data.get("products", [])
        
        for product in products[:5]:  # visa antal produkter
            print(f"Namn: {product['title']}")
            print(f"Pris: {product['price']} USD")
            print(f"Beskrivning: {product['description']}")
            print(f"Bild: {product['thumbnail']}")
            print("-" * 40) 
    else:
        print("Misslyckades att hämta produkter")



def main():
    api_products()
    
    
main()

"""
git add .
git commit -m "First py file"
git push

194 id, 24 category
"""

