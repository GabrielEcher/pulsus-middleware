from fastapi import Request
from collections import defaultdict
import time
from .logger import logger
from starlette.middleware.base import BaseHTTPMiddleware


class PulsusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_records = defaultdict(float)

    async def dispatch(self, request: Request, call_next):

        body = ''
        try:
            body = await request.json()
        except:
            body = ''
        start_time = time.time()
        
        response = await call_next(request)

        # await self.send_json_to_websocket(request, response)
        # 4. Logging (após a resposta):
        
        logger.info(f'{request.method} {request.url.path} {response.status_code} {time.time() - start_time}s {body}')
        return response
