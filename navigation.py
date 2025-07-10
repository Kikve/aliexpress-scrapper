# ====================
# navigation
# ====================

import time
from log_config import logger

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
)


def scroll_end(
    driver: WebDriver,
    scroll_step: int = 1600,
    pause_time: float = 1.0,
    bottom_threshold: int = 1000,
) -> bool:
    """
    Scrolls the page down in increments until you’ve reached (or are within)
     a certain distance of the bottom of the document.

     Args:
         driver: A Selenium WebDriver instance.
         scroll_step: Number of pixels to scroll in each iteration. Defaults to 1600.
         pause_time: Seconds to wait after each scroll. Defaults to 1.0.
         bottom_threshold: Stop when the remaining distance to the bottom is less
           than this number of pixels. Defaults to 1000.
         max_steps: Maximum number of scroll attempts before giving up. Defaults to 100.

     Returns:
         True if the bottom was reached (within bottom_threshold),
         False if the page are not scrolling.

    """

    height = driver.execute_script("return document.body.scrollHeight")
    position_height = driver.execute_script("return window.scrollY")
    while (height - position_height) > bottom_threshold:
        driver.execute_script(
            f"window.scrollTo({position_height}, {position_height + scroll_step});"
        )

        # Get the new values
        time.sleep(pause_time)
        height = driver.execute_script("return document.body.scrollHeight")
        position_height = driver.execute_script("return window.scrollY")

    logger.info(f"[scroll end] url = {driver.current_url}, end scroll")
    return True


def navigate_to(driver: WebDriver, url: str) -> bool:
    """
    Navigate the Selenium WebDriver to the given URL, returning success status.

       Args:
           driver (WebDriver): An instance of Selenium’s WebDriver.
           url (str): The destination URL to load.

       Returns:
           bool:
               - True if the page was loaded without exception.
               - False if an exception occurred while loading, with the error logged
    """
    try:
        driver.get(url)
    except Exception as e:
        logger.error(f"[navigate_to] page not loaded -> {e}")
        return False
    time.sleep(1)
    current_url = driver.current_url
    if current_url != url:
        logger.error(f"[navigate to] the page returned is not the same {current_url}")
        input("Press Return to continue")
        navigate_to(driver, url)
    logger.info(f"[navigate to] page loaded {url}")
    return True


def select_and_hover(driver: WebDriver, selector: str, retry: int = 2) -> bool:
    """
    Find and element in current driver page ans hover it

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        retry (int): Number of times to attempt selection

    Returns:
        bool:
            True if the page was successfully loaded (via driver.get),
            False if all attempts failed and the page was skipped.
    """

    for attempt in range(0, retry):
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            ActionChains(driver).move_to_element(element).perform()
            logger.info(f"[selector_and_hover] => {selector=},{attempt=} hovered")

            return True

        except (TimeoutException, NoSuchElementException):
            logger.error(f"[selector_and_hover] => {selector=},{attempt=} not found")

        except WebDriverException:
            logger.error(f"Navigation Error {attempt=}")

        if attempt < retry:
            input("Press return to continue")
        else:
            logger.error(f"[selector_and_hover] => {selector=},{attempt=} skipping")
            return False
