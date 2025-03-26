import requests

def api_products():
    url = "https://dummyjson.com/products"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        products = data.get("products", [])
        
        for product in products[:]:  # visa antal produkter
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

