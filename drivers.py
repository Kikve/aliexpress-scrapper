
from typing import Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
import undetected_chromedriver as uc
from utils import get_IP


def get_driver(
    user_agent,
    window_size: Tuple[int, int] = (1200, 800),
    headless: bool = False,
    chrome_driver_path="./chromedriver",
    timeout=30,
) -> ChromeDriver:
    """
    Create and configure a Chrome WebDriver instance.

    Args:
        user_agent: The User-Agent string to send with each request.
        headless: Whether to run Chrome in headless mode (no GUI). Defaults to False.
        window_size: Initial window size as (width, height). Defaults to (1200, 800).
        page_load_timeout: Maximum seconds to wait for page loads. Defaults to 30.
        chrome_driver_path: Filesystem path to the chromedriver executable.

    Returns:
        A configured instance of selenium.webdriver.chrome.webdriver.WebDriver.

    Raises:
        RuntimeError if the driver binary is missing or fails to start.
    """

    options = Options()
    if headless:
        options.add_argument("headless=new")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument(f"window-size={window_size[0]},{window_size[1]}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    service = Service(executable_path=chrome_driver_path)

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        raise RuntimeError(
            f"[get_driver] failed to start ChromeDriver at '{chrome_driver_path=}'"
        ) from e

    driver.set_page_load_timeout(30)

    return driver


def get_driver_uc(
    user_agent: str,
    window_size: Tuple[int, int] = (1200, 800),
    headless: bool = False,
    timeout: int = 30,
) -> ChromeDriver:
    """
    Create an undetected-chromedriver Chrome WebDriver instance
    (auto-manages the driver binary) with stealth patches.

    Args:
        user_agent: UA string to send.
        window_size: (width, height)
        headless: run in headless mode if True.
        timeout: seconds to wait for page loads.

    Returns:
        Configured Chrome WebDriver.
    """
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    try:
        driver = uc.Chrome(options=options)

    except Exception as e:
        raise RuntimeError(f"[get_driver_uc] failed to start ChromeDriver") from e
    driver.set_page_load_timeout(timeout)

    return driver


def driver_info(driver: WebDriver) -> dict:
    # User Agent
    ua = driver.execute_script("return navigator.userAgent")
    _, ip = get_IP(driver)

    # if these are missing can be interpretated as a bot
    platform = driver.execute_script("return navigator.platform")
    vendor = driver.execute_script("return navigator.vendor")
    languages = driver.execute_script("return navigator.languages")
    webdriver = driver.execute_script("return navigator.webdriver")  # should be false

    # real users has variaty of sizes on these variables
    width = driver.execute_script("return screen.width")
    height = driver.execute_script("return screen.height")
    dpr = driver.execute_script("return window.devicePixelRatio")
    tz = driver.execute_script(
        "return Intl.DateTimeFormat().resolvedOptions().timeZone"
    )

    # bots often have empty plugins
    plugins = driver.execute_script(
        "return Array.from(navigator.plugins).map(p=>p.name)"
    )
    mimeTypes = driver.execute_script(
        "return Array.from(navigator.mimeTypes).map(m=>m.type)"
    )

    # bots not persist or send real cookies
    cookies = driver.get_cookies()
    ls = driver.execute_script("return window.localStorage")
    ss = driver.execute_script("return window.sessionStorage")

    keys = [
        "ua",
        "ip",
        "platform",
        "vendor",
        "languages",
        "webdriver",
        "width",
        "height",
        "dpr",
        "tz",
        "plugins",
        "mimeTypes",
        "cookies",
        "ls",
        "ss",
    ]
    ns = locals().copy()
    return {name: ns[name] for name in keys}




