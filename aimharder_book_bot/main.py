"""Main execution file for the AimHarder Book Bot."""

import os

from dotenv import load_dotenv

from aimharder_book_bot.book import book_class
from aimharder_book_bot.utils import (
    get_classes_to_book,
    get_driver,
    login,
    switch_filter,
)

load_dotenv()
SCHEDULE_URL = os.getenv("SCHEDULE_URL")


def run_bot(user: str = "helena"):
    """Main execution function."""
    TARGETS = get_classes_to_book(user=user)
    driver = get_driver()
    try:
        login(driver=driver)
        driver.get(SCHEDULE_URL)

        for target in TARGETS:
            switch_filter(driver=driver, class_id=target["id"])

            for days in target["days_ahead"]:
                book_class(driver=driver, target=target, days_ahead=days)

    finally:
        driver.quit()
