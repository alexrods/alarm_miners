import os
import time
import json
import requests
from fastapi import FastAPI

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Configuración de la API de WhatsApp Business
WHATSAPP_API_URL=os.environ["WHATSAPP_API_URL"]
WHATSAPP_ACCESS_TOKEN=os.environ["WHATSAPP_ACCESS_TOKEN"]

def send_message(to, ltc_workers, btc_workers, in_alert):
    if in_alert:
        template = "workers_alert"
    else:
        template = "everything_ok_workers_"
    try:
        payload = json.dumps(
            {
                "messaging_product": "whatsapp",
                "to": to,  
                "type": "template",
                "template": {
                    "name": template,  
                    "language": {
                        "code": "en"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": ltc_workers
                                },
                                {
                                    "type": "text",
                                    "text": btc_workers
                                }
                            ]
                        }
                    ]
                }
            }
        )

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
            'message': f'An error occurred while processing the request. {error}'
        }
    