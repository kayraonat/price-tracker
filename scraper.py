import requests
from bs4 import BeautifulSoup
import json
import os

DATA_FILE = "price_history.json"

url = "http://books.toscrape.com/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_current_price():
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Fix encoding to handle the currency symbol correctly
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, "html.parser")
        first_book = soup.find("article", class_="product_pod")

        if first_book:
            book_name = first_book.find("h3").find("a")["title"]
            raw_price = first_book.find("p", class_="price_color").text
            
            # Clean the price string (remove currency symbols and convert to float)
            clear_price = float(raw_price.replace('Â£', '').replace('£', '').strip())

            return book_name, clear_price
        return None, None

    except Exception as e:
        print(f"Error while fetching data: {e}")
        return None, None

def load_previous_data():
    # If the file exists, load the data; otherwise, return an empty dictionary
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_data(data):
    # Save the updated data back to the JSON file
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# --- MAIN LOGIC ---
if __name__ == "__main__":
    book_name, new_price = get_current_price()

    if book_name and new_price:
        print(f"Tracked Product: {book_name}")
        print(f"Current Price: {new_price} GBP")
        
        # Load past data
        history_data = load_previous_data()
        
        # Check if the book is already being tracked
        if book_name in history_data:
            old_price = history_data[book_name]["price"]
            print(f"Previous Price: {old_price} GBP")
            
            # Comparison Logic
            if new_price < old_price:
                print("ALERT! Price has dropped! (Notification will be sent)")
            elif new_price > old_price:
                print("WARNING: Price has increased.")
            else:
                print("Price has not changed.")
        else:
            print("This product is being tracked for the first time.")
            
        # Update the dictionary with the new price
        history_data[book_name] = {
            "price": new_price,
            "currency": "GBP"
        }
        
        # Save to file
        save_data(history_data)
        print(f"Data successfully saved to '{DATA_FILE}'.")

    else:
        print("Failed to retrieve data. Process aborted.")\
        