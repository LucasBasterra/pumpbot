import os, time, requests
from web3 import Web3

CONTRACT_ADDRESS = "0x014Eb1258Fb6F8e3049bc3cDE3A75400bcbE7814"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
w3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
account = w3.eth.account.from_key(PRIVATE_KEY)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=[{"inputs":[],"name":"go","outputs":[],"stateMutability":"nonpayable","type":"function"}])

print("PUMPBOT RENDER 24/7 → LISTO")
last_pump = 0
last_price = None

while True:
    try:
        price = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()["price"])
        if last_price and (price - last_price)/last_price*100 >= 0.32 and time.time() - last_pump > 120:
            print(f"PUMP DETECTADO +{((price-last_price)/last_price*100):.3f}% → DISPARANDO")
            tx = contract.functions.go().build_transaction({
                "chainId": 42161, "nonce": w3.eth.get_transaction_count(account.address),
                "gas": 5500000, "maxFeePerGas": w3.to_wei("0.11","gwei"), "maxPriorityFeePerGas": w3.to_wei("0.02","gwei")
            })
            signed = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            print(f"https://arbiscan.io/tx/{tx_hash.hex()}")
            w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
            last_pump = time.time()
        last_price = price
        time.sleep(3)
    except Exception as e:
        print("Error:", e)
        time.sleep(10)
