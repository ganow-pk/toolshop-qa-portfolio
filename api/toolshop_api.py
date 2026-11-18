"""Thin client for the Toolshop REST API.

The API version of a page object: tests call readable methods, and the
endpoint paths live here only.
"""
import time

from playwright.sync_api import APIRequestContext, APIResponse

from config.logger import log


class ToolshopApi:
    def __init__(self, request: APIRequestContext) -> None:
        self.request = request

    def _send(self, method: str, path: str, note: str = "", **kwargs) -> APIResponse:
        start = time.perf_counter()
        response = self.request.fetch(path, method=method, **kwargs)
        ms = (time.perf_counter() - start) * 1000
        log.info("%s %s %s-> %s %s (%.0f ms)", method, path, note, response.status, response.status_text, ms)
        return response

    def login(self, email: str, password: str) -> APIResponse:
        # Body holds a password, so only the email is written to the log.
        return self._send("POST", "/users/login", note=f"as {email!r} ",
                          data={"email": email, "password": password})

    def list_products(self, **params) -> APIResponse:
        return self._send("GET", "/products", params=params or None)

    def search_products(self, query: str) -> APIResponse:
        return self._send("GET", "/products/search", note=f"q={query!r} ", params={"q": query})

    def products_in_price_range(self, low: float, high: float) -> APIResponse:
        return self._send("GET", "/products", note=f"price {low}-{high} ",
                          params={"between": f"price,{low},{high}"})
