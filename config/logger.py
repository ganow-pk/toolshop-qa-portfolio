"""One logger for the whole suite.

Page objects and the API client write a short line for every step they take.
pytest captures those lines and the HTML report shows them in each test's Log box.
Rule: never log a password, token, or other secret.
"""
import logging

log = logging.getLogger("toolshop")
