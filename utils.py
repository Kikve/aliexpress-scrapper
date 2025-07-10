from typing import Tuple, Optional
import re
from selenium.webdriver.remote.webdriver import WebDriver

from navigation import navigate_to
import time
from selenium.webdriver.common.by import By


def extract_number(string_number: str) -> Tuple[bool, Optional[float]]:
    """
    Extracts the first number (with optional decimal point) from a string.

    Returns (True, value) on success, or (False, 0.0) on no match.
    Commas are stripped before parsing.
    """
    string_number = string_number.strip().replace(",", "")
    match = re.search(r"[\d\.]+", string_number)
    if match:
        number = match.group(0)
        return True, float(number)
    else:
        return False, None


def get_IP(driver: WebDriver) -> Tuple[bool, Optional[str]]:
    if navigate_to(driver, "https://www.whatismyip.com/"):
        time.sleep(5)
        ip = driver.find_element(By.ID, "ipv4").text
        return (True, ip)
    else:
        return (False, None)
