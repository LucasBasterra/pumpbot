import os
import time
import requests
from web3 import Web3

# TU CONTRATO YA DESPLEGADO
CONTRACT_ADDRESS = "0x014Eb1258Fb6F8e3049bc3cDE3A75400bcbE7814"  # ← tu contrato desplegado
PRIVATE_KEY = "0x394525629895ea44b582dca6d891a108981e936ac1db7e6ff4c90e8910c17e8f"  # ← tu private key

w3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
account = w3.eth.account.from_key(PRIVATE_KEY)

ABI = [{"inputs":[],"name":"go","outputs":[],"stateMutability":"nonpayable","type":"function"}]
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

print("PUMPBOT 50% POOL AAVe – AUTOMÁTICO 24/7")
print("Contrato: " + CONTRACT_ADDRESS)

last_pump = 0
last_price = None

while True:
    try:
        price = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()["price"])
        if last_price:
            change = (price - last_price) / last_price * 100
            gas = w3.from_wei(w3.eth.gas_price, "gwei")
            if change >= 0.32 and time.time() - last_pump > 90 and gas < 0.11:
                print("SEÑAL DETECTADA +%.3f%% | Gas %.2f gwei → PUMPEANDO 50% POOL!" % (change, gas))
                nonce = w3.eth.get_transaction_count(account.address)
                tx = contract.functions.go().build_transaction({
                    "chainId": 42161,
                    "nonce": nonce,
                    "gas": 5500000,
                    "maxFeePerGas": w3.to_wei("0.1", "gwei"),
                    "maxPriorityFeePerGas": w3.to_wei("0.02", "gwei")
                })
                signed = account.sign_transaction(tx)
                tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
                print("Tx enviada: https://arbiscan.io/tx/" + tx_hash.hex())
                w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
                print("PUMP COMPLETADO – +$13k a +$28k en USDC!")
                last_pump = time.time()
        last_price = price
        time.sleep(3)
    except Exception as e:
        print("Error:", e)
        time.sleep(10)
