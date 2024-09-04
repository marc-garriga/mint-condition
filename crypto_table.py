import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time

BASE_URL = "https://api.coingecko.com/api/v3"
COINS = ['bitcoin', 'ethereum', 'solana']
CURRENCY = 'usd'

def make_api_request(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    while True:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
            else:
                print(f"HTTP error occurred: {e}")
                raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

def get_coin_data(coin_id):
    data = make_api_request(f"coins/{coin_id}")
    current_price = data['market_data']['current_price'][CURRENCY]
    change_1y = data['market_data']['price_change_percentage_1y']
    return current_price, change_1y

def get_historical_price(coin_id, date):
    data = make_api_request(f"coins/{coin_id}/history", {"date": date.strftime('%d-%m-%Y')})
    return data['market_data']['current_price'][CURRENCY]

def get_fear_greed_index():
    try:
        response = requests.get("https://api.alternative.me/fng/")
        response.raise_for_status()
        data = response.json()
        return int(data['data'][0]['value'])
    except Exception as e:
        print(f"Error fetching Fear & Greed Index: {e}")
        return None

def get_global_data():
    try:
        data = make_api_request("global")
        bitcoin_dominance = data['data']['market_cap_percentage']['btc']
        total_market_cap = data['data']['total_market_cap'][CURRENCY]
        return bitcoin_dominance, total_market_cap
    except KeyError as e:
        print(f"KeyError in get_global_data: {e}")
        print(f"API response: {data}")
        return None, None
    except Exception as e:
        print(f"Error in get_global_data: {e}")
        return None, None

def create_dashboard():
    start_time = datetime.now()
    data = []
    
    print("Fetching global data...")
    bitcoin_dominance, total_market_cap = get_global_data()
    print(f"Bitcoin Dominance: {bitcoin_dominance}")
    print(f"Total Market Cap: {total_market_cap}")
    
    for coin in COINS:
        print(f"Fetching data for {coin}...")
        current_price, change_1y = get_coin_data(coin)
        week_ago = datetime.now() - timedelta(days=7)
        week_ago_price = get_historical_price(coin, week_ago)
        week_change = ((current_price - week_ago_price) / week_ago_price) * 100
        
        data.append({
            'Coin': coin.capitalize(),
            'Price': f"${current_price:,.0f}",
            'Week Change': f"{week_change:.2f}%",
            'This Year': f"{change_1y:.2f}%"
        })
        time.sleep(5)  # Add a 5-second delay between coin requests

    df = pd.DataFrame(data)
    
    fig, ax = plt.subplots(figsize=(10, 8))  # Increased figure height to accommodate new information
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    # Add Bitcoin Dominance and Total Market Cap
    if bitcoin_dominance is not None and total_market_cap is not None:
        plt.text(0.5, 0.18, f"Bitcoin Dominance: {bitcoin_dominance:.2f}%", ha='center', va='center', transform=ax.transAxes)
        plt.text(0.5, 0.14, f"Total Crypto Market Cap: ${total_market_cap:,.0f}", ha='center', va='center', transform=ax.transAxes)
    else:
        plt.text(0.5, 0.16, "Global data unavailable", ha='center', va='center', transform=ax.transAxes)
    
    fear_greed = get_fear_greed_index()
    if fear_greed is not None:
        plt.text(0.5, 0.10, f"Crypto Fear & Greed Index: {fear_greed}", ha='center', va='center', transform=ax.transAxes)
    else:
        plt.text(0.5, 0.10, "Crypto Fear & Greed Index: Unavailable", ha='center', va='center', transform=ax.transAxes)
    
    # Add timestamp
    end_time = datetime.now()
    timestamp = end_time.strftime("%Y-%m-%d %H:%M:%S")
    plt.text(0.5, 0.02, f"Data as of: {timestamp}", ha='center', va='center', transform=ax.transAxes, fontsize=8)
    
    plt.title("Mint Condition Cryptocurrency Dashboard", fontsize=16)
    plt.tight_layout()
    plt.savefig('crypto_dashboard.png')
    print(f"Dashboard created and saved as 'crypto_dashboard.png' (Data as of: {timestamp})")
    if bitcoin_dominance is not None and total_market_cap is not None:
        print(f"Bitcoin Dominance: {bitcoin_dominance:.2f}%")
        print(f"Total Crypto Market Cap: ${total_market_cap:,.0f}")
    else:
        print("Global data unavailable")

if __name__ == "__main__":
    create_dashboard()
