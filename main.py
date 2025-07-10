# ========================================
# Main aliexpress srapper
# ========================================

from pandas import DataFrame
import time
from log_config import logger

from drivers import get_driver_uc, driver_info
from navigation import navigate_to, scroll_end
from parsing import card_to_dict, get_page_soup, get_info_seller


# Define variables
# one or multiple user agents
User_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
Query = "laptops"
Main_Url = f"https://es.aliexpress.com/w/wholesale-{Query}.html"
Card_class_component = "search-item-card-wrapper-gallery"
Selector_product_popup = ".store-detail--title--qt8UBeq"
Selector_product = "comet-v2-popover-content"

# initialize driver
driver = get_driver_uc(User_agent)
info = driver_info(driver)
# get current IP
logger.warning(f"IP: {info['ip']}")


# final lists
data: list[dict] = []  # products completed correctly
products_without_seller_info = []  # products without seller info, error or info not existent
ignored_cards_components = []  # ignored card components, different format?, or not existent

# navigate to the main page and get all urls of all products
if navigate_to(driver, Main_Url):
    if scroll_end(driver):
        main_soup = get_page_soup(driver)
        cards_components = main_soup.find_all(class_=Card_class_component)
        # match the card with the predifined format
        cards_to_dicts = map(card_to_dict, cards_components)
        # filter cards by status
        products = [
            card for status, card in cards_to_dicts if status
        ]  # dict with data of the main page
        ignored_cards_components = [card for status, card in cards_to_dicts if not status]
        logger.warning(f"all cards components loaded {len(data)}")

        # add seller details
        for index, product in enumerate(products):
            logger.warning("looking for seller details" + f" {index=}")
            status_get_seller_info, info_seller = get_info_seller(
                driver, product["url"], Selector_product_popup, Selector_product)

            if status_get_seller_info:
                product["seller_info"] = info_seller
                data.append(product)
                logger.info("[main] seller details added")
            else:
                products_without_seller_info.append(product)
                logger.error("[main] seller details not added")

            logger.debug(f"[main] =>> {product=}")
            time.sleep(2)

        df = DataFrame(data)
        df.to_csv(f'aliexpress {Query}.csv')
