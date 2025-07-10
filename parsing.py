# ====================
# parsing
# ====================

from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Tuple

from log_config import logger
from navigation import navigate_to, select_and_hover
from utils import extract_number


def get_page_soup(driver: WebDriver) -> BeautifulSoup:
    """
    Retrieve the current page’s HTML and parse it into a BeautifulSoup object.

    # Args:
    driver (WebDriver): An already-configured Selenium WebDriver
        that has navigated to the desired URL.

    # Returns:
    BeautifulSoup: The parsed HTML of the current page, using
    the built-in 'html.parser'.
    """
    source = driver.page_source
    soup = BeautifulSoup(source, "html.parser")
    return soup


def parse_product_page_to_dict(
    soup_product: BeautifulSoup, popup_class: str
) -> Tuple[bool, dict]:
    """
    Parses a product page popup table into a dictionary of key-value pairs.

    This function locates a popup by its CSS class, finds the first table inside it,
    and extracts each row into key-value entries. It builds a dictionary where the
    first column is used as the key and the second column as the value.

    # Args
    soup_product (BeautifulSoup): A BeautifulSoup object of the current HTML page.
    popup_class (str): The CSS class name of the popup container.

    # Returns
    Tuple[bool,dict]:
        Returns False if the expected popup/table format is missing, otherwise
        prints the collected data and returns True.
    """
    popup = soup_product.find(class_=popup_class)
    table = popup.table if popup else None
    data = {}

    if not table or not popup:
        logger.error(
            f"[parse_product_page_to_dict] format is not right =>{popup=},{table=}"
        )
        return (False, data)

    for tr in table.children:
        x, y = tr.children
        x = x.get_text(strip=True).replace(":", "")
        y = y.get_text(strip=True)

        data[x] = y

    logger.info("[parse_product_page_to_dict] data recolected => {popup_class=}")
    return (True, data)


def card_to_dict(card_component: BeautifulSoup) -> Tuple[bool, dict]:
    """
    Parses a card component into a dictionary with name, price and url.

    Args:
        card_component (BeautifulSoup): A BeautifulSoup tag representing a single product card.

    Returns:
        Tuple[bool, dict]:
            (True, data) if parsing succeeded with extracted info.
            (False, {}) if structure was not as expected.
    """

    link_tag = card_component.find("a")
    name_tag = card_component.find(class_="kr_j0")
    price_tag = card_component.find(class_="kr_kj")

    if not all((link_tag, name_tag, price_tag)):
        logger.error(
            f"[card_to_dict] format is not right => {link_tag=},{name_tag=},{price_tag=}"
        )
        return (False, {})

    url = link_tag.get("href", "").strip()
    product_name, price_text = [e.get_text(strip=True) for e in (name_tag, price_tag)]

    stat_price, price = extract_number(price_text)

    logger.info(
        f"[card_to_dict] soup parsed to dict product_name={product_name[:20]} ... , {price=}"
    )

    return (
        True,
        {
            "name": product_name,
            "price": price,
            "url": "https:" + url,
        },
    )


def get_info_seller(
    driver: WebDriver, url: str, selector_popup: str, selector_product: str
) -> Tuple[bool, dict]:
    """
    1) Load `url` via navigate_to().
    2) Hover element `selector_popup` via select_and_hover().
    3) Parse product details under `selector_product`.

    Returns:
        (True, product_dict) if everything succeeds.
        (False, {}) if load, hover or parse fails.
    """

    if navigate_to(driver, url) and select_and_hover(driver, selector_popup):
        soup_product = get_page_soup(driver)
        status, product_dict = parse_product_page_to_dict(
            soup_product, selector_product
        )
        return (True, product_dict) if status else (False, {})
    else:
        return (False, {})
