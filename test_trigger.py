import requests

# Aapka local flask webhook URL
url = "http://127.0.0.1:5000/shopify-order"

# Fake Shopify Order Data (Aap yahan apna WhatsApp number likhein)
dummy_order = {
    "name": "#1001",
    "total_price": "2500.00",
    "customer": {
        "first_name": "Bilawal Pakhtoon",
        "phone": "923276878958"  # Yahan apna real WhatsApp number likhein (with country code)
    },
    "shipping_address": {
        "phone": "923276878958"
    }
}

# Request send karein
response = requests.post(url, json=dummy_order)
print("Status Code:", response.status_code)
print("Response:", response.json())
