from dataclasses import dataclass

import aiohttp
from fastapi import Request
from multidict import CIMultiDictProxy


@dataclass
class HTTPClientResponse:
    status: int
    headers: CIMultiDictProxy
    json: dict


class HTTPClient:
    """Simple async HTTP client based on aiohttp with some convenient features, such as X-Request-Id headers transmission
      and authorization header generation"""
    def __init__(self):
        self.request_id_header = None

    def __call__(self, request: Request):
        if request_id := request.headers.get('X-Request-Id'):
            self.request_id_header = {'X-Request-Id': request_id}
        return self

    async def get(self, url, params=None, headers=None, token=None) -> HTTPClientResponse:
        final_headers = self._get_updated_headers(headers, token)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=final_headers, params=params) as response:
                return HTTPClientResponse(
                    status=response.status,
                    headers=response.headers,
                    json=await response.json()
                )

    def _get_updated_headers(self, initial_headers, token):
        headers = initial_headers or {}
        if self.request_id_header:
            headers.update(self.request_id_header)
        if token:
            headers.update({'Authorization': f'Bearer {token}'})

        return headers or initial_headers


http_client = HTTPClient()
