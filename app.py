import os
import time
import json
import requests
import asyncio
import numpy as np
from fastapi import FastAPI, Request, HTTPException, Response, BackgroundTasks
from api.get_miners import monitor_api
from meta.send_message import send_message
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_TOKEN=os.environ["WEBHOOK_TOKEN"]

DEV=os.environ["PHONE_NUMBER"]
HECTOR_PHONE_NUMBER = os.environ["HECTOR_PHONE_NUMBER"]
TANIA_PHONE_NUMBER = os.environ["TANIA_PHONE_NUMBER"]
LUIS_PHONE_NUMBER = os.environ["LUIS_PHONE_NUMBER"]
VICTORINO_PHONE_NUMBER = os.environ["VICTORINO_PHONE_NUMBER"]

TOTAL_LTC_WORKERS = 30
TOTAL_BTC_WORKERS = 2


app = FastAPI()


async def check_active_miners():
    # Variable para almacenar la última notificación de alerta enviada
    last_alert_time = None
    # Bandera para saber si estamos en estado de alerta
    in_alert = False
    # Intervalo de notificación en alerta: 5 minutos (300 segundos)
    alert_interval = 5 * 60

    TO_NUMBERS = [DEV, HECTOR_PHONE_NUMBER, TANIA_PHONE_NUMBER, LUIS_PHONE_NUMBER, VICTORINO_PHONE_NUMBER]

    while True:
        workers = await monitor_api()
        ltc_workers = workers["response"].get("ltc_workers", np.nan)
        btc_workers = workers["response"].get("btc_workers", np.nan)
        now = time.time()
        
        # Verificar si hay una situación de alerta
        current_alert_state = ltc_workers < TOTAL_LTC_WORKERS or btc_workers < TOTAL_BTC_WORKERS
        
        # Caso 1: Entramos en estado de alerta
        if current_alert_state and not in_alert:
            send_message(TO_NUMBERS, ltc_workers, btc_workers, in_alert=True)
            last_alert_time = now
            in_alert = True
            print(f"Alerta inicial enviada: {datetime.now()}")
        
        # Caso 2: Seguimos en estado de alerta, verificar si toca reenviar
        elif current_alert_state and in_alert and (now - last_alert_time >= alert_interval):
            send_message(TO_NUMBERS, ltc_workers, btc_workers, in_alert=True)
            last_alert_time = now
            print(f"Alerta repetida enviada: {datetime.now()}")
        
        # Caso 3: Salimos del estado de alerta
        elif not current_alert_state and in_alert:
            send_message(TO_NUMBERS, ltc_workers, btc_workers, in_alert=False)
            in_alert = False
            last_alert_time = None
            print(f"Recuperación enviada: {datetime.now()}")
        
        # Esperar antes de la siguiente verificación
        await asyncio.sleep(60)


# Endpoint para verificar el webhook
@app.get("/webhook")
async def verify_token(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_challenge = request.query_params.get("hub.challenge")
    hub_verify_token = request.query_params.get("hub.verify_token")

    if hub_mode == "subscribe" and hub_verify_token == WEBHOOK_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain", status_code=200)
    else:
        raise HTTPException(status_code=403, detail="Verification token mismatch")


# Endpoint principal del webhook
@app.post("/webhook")
async def receive_whatsapp_message():
    return Response(status_code=200)


@app.on_event("startup")
async def startup_event():
    # Si check_active_miners se ejecuta de forma continua, créala como tarea en segundo plano.
    asyncio.create_task(check_active_miners())
