import os
import httpx
import numpy as np
from dotenv import load_dotenv

load_dotenv()

btc = 'bitcoin'
ltc = 'litecoin'
api_key = os.environ["API_KEY"]

async def monitor_api():
    active_workers_ltc = None
    active_workers_btc = None
    async with httpx.AsyncClient() as client:
        response_ltc = await client.get(f"https://www.mining-dutch.nl/pools/{ltc}.php?page=api&action=getuserworkers&api_key={api_key}")
        response_btc = await client.get(f"https://www.mining-dutch.nl/pools/{btc}.php?page=api&action=getuserworkers&api_key={api_key}")
        data_ltc = response_ltc.json()
        data_btc = response_btc.json()

    if data_ltc or data_btc:
            try:
                workers_ltc = data_ltc['getuserworkers']['data']['count']
                active_workers_ltc = workers_ltc['active']
            except Exception as e:
                return {"response": {"ltc_workers": np.nan, "btc_workers": np.nan}}
            try:
                workers_btc = data_btc['getuserworkers']['data']['count']
                active_workers_btc = workers_btc['active']
            except Exception as e:
                return {"response": {"ltc_workers": np.nan, "btc_workers": np.nan}}

            response = {
                "response": {
                    "ltc_workers": active_workers_ltc,
                    "btc_workers": active_workers_btc
                }
            }
            return response
            
# asyncio.run(monitor_api()) 