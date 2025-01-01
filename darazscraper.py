import requests
import json
import pandas as pd
from time import sleep

def scrape_daraz_api(pages=1):
    base_url = "https://www.daraz.com.np/catalog/?ajax=true&isFirstRequest=true&q=mobile%20phones"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    all_products = []
    
    for page in range(1, pages + 1):
        url = f"{base_url}&page={page}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Extract products from JSON
            products = data.get('mods', {}).get('listItems', [])
            
            for product in products:
                product_info = {
                    'name': product.get('name'),
                    'price': product.get('price'),
                    'originalPrice': product.get('originalPrice'),
                    'discount': product.get('discount'),
                    'rating': product.get('ratingScore'),
                    'location': product.get('location'),
                    'itemId': product.get('itemId'),
                    'itemSold': product.get('itemSoldCntShow'),
                    'brandName': product.get('brandName'),
                }
                all_products.append(product_info)
            
            print(f"Scraped page {page}")
            sleep(1)  # Respect rate limiting
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            continue
    
    # Save raw JSON
    with open('daraz_raw2.json', 'w') as f:
        json.dump(all_products, f, indent=2)
    
    # Save as CSV
    df = pd.DataFrame(all_products)
    df.to_csv('daraz_products2.csv', index=False)
    print(f"Scraped {len(all_products)} products")
    
    return df

if __name__ == "__main__":
    scrape_daraz_api(pages=3)  # Scrape first 3 pages