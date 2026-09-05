import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# 'client.env' file se variables load karna
load_dotenv('client.env')

app = Flask(__name__)

# --- CONFIGURATION FROM ENVIRONMENT VARIABLES ---
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v25.0")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
GOOGLE_SHEET_WEB_APP_URL = os.getenv("GOOGLE_SHEET_WEB_APP_URL", "")

# --- 1. AUTOMATIC PHONE NUMBER FORMATTING (E.164 Standard) ---
def format_phone_number(raw_phone: str) -> str:
    if not raw_phone:
        return ""
    digits = "".join(filter(str.isdigit, raw_phone))
    
    if digits.startswith("0") and len(digits) == 11:
        digits = "92" + digits[1:]
    elif len(digits) == 10:
        digits = "92" + digits
        
    return digits

# --- 2. DUPLICATE CHECKER VIA GOOGLE APPS SCRIPT ---
def check_order_exists(order_id: str) -> bool:
    try:
        response = requests.get(f"{GOOGLE_SHEET_WEB_APP_URL}?order_id={order_id}", timeout=10)
        result = response.json()
        return result.get("exists", False)
    except Exception as e:
        print(f"[GOOGLE SHEET CHECK ERROR]: {e}")
    return False

# --- 3. GOOGLE SHEET MANAGER VIA WEB APP ---
def update_google_sheet(phone_number: str, order_id: str, status: str):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "order_id": order_id,
        "phone_number": phone_number,
        "status": status,
        "timestamp": current_time
    }
    
    try:
        response = requests.post(GOOGLE_SHEET_WEB_APP_URL, json=payload, timeout=10)
        print(f"[GOOGLE SHEET SUCCESS] Order {order_id} recorded as '{status}'.")
    except Exception as e:
        print(f"[GOOGLE SHEET ERROR] Failed to update Google Sheet: {e}")

# --- 4. WHATSAPP TEMPLATE SENDER FUNCTIONS ---
def send_order_confirmation_button(phone_number: str, customer_name: str, order_id: str, total_amount: str):
    print(f"[DEBUG] Sending confirmation button template to: {phone_number}")
    endpoint = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": "confirmation_message_templete",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": customer_name},
                        {"type": "text", "text": order_id},
                        {"type": "text", "text": total_amount}
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"[WHATSAPP SUCCESS] Confirmation template sent to {phone_number}")
    except Exception as e:
        print(f"[WHATSAPP ERROR] Failed to send message: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"[META ERROR DETAILS]: {e.response.text}")

def send_success_reply_template(phone_number: str, customer_name: str, order_id: str):
    endpoint = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": "corecart_success_reply",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": customer_name},
                        {"type": "text", "text": order_id}
                    ]
                }
            ]
        }
    }
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[WHATSAPP ERROR] Failed to send success reply: {e}")

def send_cancel_reply_template(phone_number: str, customer_name: str, order_id: str):
    endpoint = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": "corecart_cancel_reply",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": customer_name},
                        {"type": "text", "text": order_id}
                    ]
                }
            ]
        }
    }
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[WHATSAPP ERROR] Failed to send cancel reply: {e}")

def send_delivery_feedback_template(phone_number: str, customer_name: str, order_id: str):
    endpoint = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": "corecart_delivery_feedback",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": customer_name},
                        {"type": "text", "text": order_id}
                    ]
                }
            ]
        }
    }
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"[WHATSAPP SUCCESS] Feedback template sent to {phone_number}")
    except Exception as e:
        print(f"[WHATSAPP ERROR] Failed to send feedback message: {e}")

# --- 5. INVALID TEXT MESSAGE HANDLER ---
def send_guidance_message(phone_number: str):
    endpoint = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": "Kindly use the 'Confirm Order' or 'Cancel Order' buttons provided in the message above to process your order. 😊"
        }
    }
    try:
        requests.post(endpoint, json=payload, headers=headers, timeout=10)
        print(f"[GUIDANCE SENT] Sent helper text to {phone_number}")
    except Exception as e:
        print(f"[ERROR] Failed to send guidance text: {e}")

# --- 6. SHOPIFY WEBHOOK ROUTE ---
@app.route('/shopify-order', methods=['POST'])
def handle_shopify_order():
    order_data = request.get_json()
    try:
        customer_name = order_data.get('customer', {}).get('first_name', 'Valued Customer')
        raw_phone = order_data.get('shipping_address', {}).get('phone') or order_data.get('customer', {}).get('phone', '')
        
        phone_number = format_phone_number(raw_phone)
        order_id = str(order_data.get('name', 'Z-000000'))
        total_price = str(order_data.get('total_price', '0'))
        
        if phone_number:
            if check_order_exists(order_id):
                print(f"[DUPLICATE BLOCKED] Order {order_id} is already processed. Skipping message.")
            else:
                send_order_confirmation_button(phone_number, customer_name, order_id, total_price)
        else:
            print("[WARNING] Phone number missing in Shopify order payload.")
            
    except Exception as e:
        print(f"[SHOPIFY ERROR] {e}")
        
    return jsonify({"status": "received"}), 200

# --- 7. META WEBHOOK ROUTE ---
@app.route('/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode and token:
            if mode == "subscribe" and token == VERIFY_TOKEN:
                print("[VERIFY SUCCESS] Tokens matched!")
                return challenge, 200
            else:
                return "Verification failed: Token mismatch", 403
        return "Verification failed: Missing parameters", 400

    data = request.get_json()
    
    try:
        entries = data.get('entry', [])
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                messages = value.get('messages', [])
                
                if not messages and 'statuses' in value:
                    continue

                for msg in messages:
                    sender_phone = msg.get('from')
                    msg_type = msg.get('type')
                    customer_name = value.get('contacts', [{}])[0].get('profile', {}).get('name', 'Customer')
                    
                    if msg_type == 'interactive':
                        reply_id = msg['interactive']['button_reply']['id']
                        print(f"[BUTTON CLICKED] ID: {reply_id} from {sender_phone}")
                        
                        if reply_id.startswith("confirm_"):
                            order_id = reply_id.replace("confirm_", "")
                            if not check_order_exists(order_id):
                                update_google_sheet(sender_phone, order_id, "Confirmed")
                                send_success_reply_template(sender_phone, customer_name, order_id)
                            
                        elif reply_id.startswith("cancel_"):
                            order_id = reply_id.replace("cancel_", "")
                            if not check_order_exists(order_id):
                                update_google_sheet(sender_phone, order_id, "Cancelled")
                                send_cancel_reply_template(sender_phone, customer_name, order_id)
                                
                    elif msg_type == 'text':
                        print(f"[TEXT RECEIVED] Non-button text from {sender_phone}")
                        send_guidance_message(sender_phone)
                            
    except Exception as e:
        print(f"[META WEBHOOK ERROR] {e}")
        
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
