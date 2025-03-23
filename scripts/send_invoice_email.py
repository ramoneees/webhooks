import smtplib
# import json  # Removed as it is not accessed
from email.mime.text import MIMEText
import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')
EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT', 'Geração de factura')

INVOICENINJA_API_URL = os.getenv('INVOICENINJA_API_URL')
INVOICENINJA_TOKEN = os.getenv('INVOICENINJA_TOKEN')

headers = {
    "X-API-TOKEN": INVOICENINJA_TOKEN,
    "X-Requested-With": "XMLHttpRequest"
}

required_env_vars = ['SMTP_SERVER', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'EMAIL_FROM', 'EMAIL_TO', 'INVOICE_NINJA_API_URL', 'INVOICE_NINJA_TOKEN']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

response = requests.get(INVOICENINJA_API_URL, headers=headers)
if response.status_code != 200:
    logger.error(f"Failed to fetch data from Invoice Ninja API: {response.status_code} {response.text}")
    raise ValueError("Failed to fetch data from Invoice Ninja API.")

countries  = response.json().get('countries')
currencies  = response.json().get('currencies')


def get_item_by_id(items, item_id):
    for item in items:
        if item['id'] == item_id:
            return item
    return None

def email_body(data):
    currency = get_item_by_id(currencies, data['currency_id'])
    country = get_item_by_id(countries, data['client']['country_id'])
    invoice_amount = f"{data['amount']} {currency['symbol']}"
    company_name = data['client']['name']
    vat_number = data['client']['vat_number']
    address = f"{data['client']['address1']}{data['client']['address2']}\n{data['client']['city']}, {data['client']['state']}\n{data['client']['postal_code']}\n{country['name']}"
    description = data['invoices'][0]['line_items'][0]['product_key']


    # Email body
    email_body = f"""
    Prezado(a),

    Solicito a gentileza de emitir uma factura no valor de:
    {invoice_amount}

    Para a empresa:

    {company_name}
    NIF/VAT: {vat_number}
    {address}

    Descrição do serviço:
    "{description}"

    Agradeço desde já pela atenção e colaboração.

    Atenciosamente,
    Ramon Rios
    """

    print(f"email body: {email_body}")

    # Create the email message
    msg = MIMEText(email_body)
    msg.set_charset('utf-8')
    
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    return msg


# Send the email

def handler(invoice_information):
    msg = email_body(invoice_information)
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        
        if SMTP_SERVER != 'localhost':
            server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
