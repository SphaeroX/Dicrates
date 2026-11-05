from typing import Protocol

import httpx

from dicrates.core.http import USER_AGENT


class UrlChecker(Protocol):
    async def is_reachable(self, url: str) -> bool: ...


class HttpxUrlChecker:
    """HEAD request (GET when HEAD is not allowed); any 2xx/3xx after redirects counts."""

    def __init__(
        self, *, timeout: float = 10.0, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self._timeout = timeout
        self._transport = transport

    async def is_reachable(self, url: str) -> bool:
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=True,
                transport=self._transport,
                headers={"User-Agent": USER_AGENT},
            ) as client:
                response = await client.head(url)
                if response.status_code in {403, 405, 501}:
                    response = await client.get(url)
                return response.status_code < 400
        except httpx.HTTPError:
            return False
