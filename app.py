import os
import time
import json
import requests
import asyncio
import numpy as np
from fastapi import FastAPI, Request, HTTPException, Response, BackgroundTasks
from api.get_miners import monitor_api
from meta.send_message import send_message

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()


WEBHOOK_TOKEN=os.environ["WEBHOOK_TOKEN"]
SEND_TO=os.environ["PHONE_NUMBER"]

TOTAL_LTC_WORKERS = 30
TOTAL_BTC_WORKERS = 2


async def check_active_miners():
    # Variable para almacenar la última notificación de alerta enviada
    last_alert_time = None
    # Bandera para saber si estamos en estado de alerta
    in_alert = False
    # Intervalo de notificación en alerta: 5 minutos (300 segundos)
    alert_interval = 5 * 60

    while True:
        workers = await monitor_api()
        ltc_workers = workers["response"].get("ltc_workers", np.nan)
        btc_workers = workers["response"].get("btc_workers", np.nan)
        now = time.time()
        
        # Construir el mensaje de alerta si alguno de los tokens tiene menos workers de los esperados
        alert_message = None
        if ltc_workers < TOTAL_LTC_WORKERS or btc_workers < TOTAL_BTC_WORKERS:
            if ltc_workers < TOTAL_LTC_WORKERS and btc_workers < TOTAL_BTC_WORKERS:
                alert_message = (
                    f"Falla en los workers:\n"
                    f"LTC WORKERS: {ltc_workers}\n"
                    f"BTC WORKERS: {btc_workers}"
                )
            elif ltc_workers < TOTAL_LTC_WORKERS:
                alert_message = f"Falla en los workers:\nLTC WORKERS: {ltc_workers}"
            elif btc_workers < TOTAL_BTC_WORKERS:
                alert_message = f"Falla en los workers:\nBTC WORKERS: {btc_workers}"

        if alert_message:
            # Se ha detectado una alerta
            # Si no estábamos ya en alerta o han pasado 5 minutos desde la última notificación, enviamos el mensaje
            if (not in_alert) or (last_alert_time is None) or (now - last_alert_time >= alert_interval):
                send_message(SEND_TO, alert_message)
                last_alert_time = now
                in_alert = True
        else:
            # Si no hay alerta y previamente se había detectado, informamos que todo está bien
            if in_alert:
                send_message(SEND_TO, message="Alarma todo está bien: Workers reestablecidos")
                in_alert = False
            # Reiniciamos la variable de notificación
            last_alert_time = None

        # Esperar 30 segundos antes de la siguiente verificación
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
