import os
import time
import json
import requests
from fastapi import FastAPI, Request, HTTPException, Response, BackgroundTasks

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Configuración de la API de WhatsApp Business
WHATSAPP_API_URL=os.environ["WHATSAPP_API_URL"]
WHATSAPP_ACCESS_TOKEN=os.environ["WHATSAPP_ACCESS_TOKEN"]

def send_message(to, message):
    try:
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
            "body": message
            }
        })

        headers = {
            'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", WHATSAPP_API_URL, headers=headers, data=payload)
        print(f"Response: {response.status_code} - {response.text}")
    
    except Exception as error:
        return {
            'error': True,
            'code': 305,
            'message': 'An error occurred while processing the request.'
        }