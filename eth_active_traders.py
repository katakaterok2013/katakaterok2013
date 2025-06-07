import requests
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import os

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
BASE_URL = "https://api.etherscan.io/api"

def get_contract_interactions(start_block, end_block):
    unique_addresses = set()
    page = 1
    while True:
        params = {
            "module": "account",
            "action": "txlistinternal",
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
            "page": page,
            "offset": 1000,
            "apikey": ETHERSCAN_API_KEY
        }
        r = requests.get(BASE_URL, params=params)
        data = r.json()
        if not data.get("result") or len(data["result"]) == 0:
            break
        for tx in data["result"]:
            if tx["isError"] == "0" and tx["from"]:
                unique_addresses.add(tx["from"])
        page += 1
    return unique_addresses

def get_block_number_by_timestamp(timestamp):
    params = {
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": timestamp,
        "closest": "before",
        "apikey": ETHERSCAN_API_KEY
    }
    r = requests.get(BASE_URL, params=params)
    return int(r.json()["result"])

def analyze_trader_activity(days=5):
    stats = {}
    for i in range(days):
        date = datetime.datetime.utcnow().date() - datetime.timedelta(days=i)
        start_time = int(datetime.datetime.combine(date, datetime.time.min).timestamp())
        end_time = int(datetime.datetime.combine(date, datetime.time.max).timestamp())
        start_block = get_block_number_by_timestamp(start_time)
        end_block = get_block_number_by_timestamp(end_time)
        print(f"🔍 [{date}] Getting addresses between blocks {start_block} and {end_block}")
        traders = get_contract_interactions(start_block, end_block)
        stats[str(date)] = len(traders)
    return stats

def plot(stats):
    dates = list(stats.keys())[::-1]
    values = [stats[d] for d in dates]
    plt.figure(figsize=(10, 5))
    plt.plot(dates, values, marker="o")
    plt.title("📈 Daily Active Ethereum Traders (Contract Interactions)")
    plt.xlabel("Date")
    plt.ylabel("Unique Wallets")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("eth_active_traders.png")
    plt.show()

if __name__ == "__main__":
    print("📊 Tracking Ethereum trader activity...")
    stats = analyze_trader_activity(5)
    print("\n💡 Results:")
    for day, count in stats.items():
        print(f"{day}: {count} unique active traders")
    plot(stats)
