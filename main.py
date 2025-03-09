from flask import Flask, request, jsonify
import scripts.send_invoice_email as send_invoice_email
import requests
import os

app = Flask(__name__)

NTFY_URL = os.getenv('NTFY_URL')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON data"}), 400

    # Process the webhook data (for example, print it)
    print("Received webhook data:", data)
    
    # You can add further processing logic here

    return jsonify({"status": "success", "received": data}), 200

@app.route('/send-mail', methods=['POST'])
def send_invoice():
    data = request.get_json(silent=True)
    try:
        send_invoice_email.handler(data)
        requests.post(NTFY_URL,data="Invoice email sent".encode(encoding='utf-8'))
        return jsonify({"status": "success", "message": "Invoice email sent"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Listen on all interfaces so that Docker can expose the port externally.
    app.run(host='0.0.0.0', port=5000, debug=True)