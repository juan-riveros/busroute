import logging
from datetime import datetime as dt, timedelta

from .config import Config
from .utils import convert_to_seconds

import httpx
from rush import quota, throttle
from rush.limiters import gcra
from rush.stores import dictionary as dict_store

class MBTAClient:
    def __init__(self, log: logging.Logger, config: Config):
        self.log = log
        self.rate_limiter = throttle.Throttle(
            rate=quota.Quota(period=timedelta(seconds=convert_to_seconds(config.Period)),
            count=config.Count,
            maximum_burst=1
            ),
            limiter=gcra.GenericCellRatelimiter(store=dict_store.DictionaryStore(store=dict()))
        )
        self.client : httpx.Client = httpx.Client(
            headers={},
            base_url="https://api-v3.mbta.com"
        )
    
    def get_routes(self):
        if not self.rate_limiter.check("key",1).limited:
            resp = self.client.get('/routes')            
            if resp.status_code == 400:
                self.log.debug(f"Bad Request - {resp.json().get('detail', 'Unknown error')}")
                return None
            if resp.status_code == 403:
                self.log.debug(f"Forbidden")
                return None
            if resp.status_code == 429:
                self.log.debug(f"Too Many Requests")
                return None
            route_data: dict = resp.json()
            records: list[dict] = route_data['data']
            return records