#
# AimHarder Booking Bot
# Author: Helena Ribera <heleribera@gmail.com>
# Website: www.hriberaponsa.com
#
"""Main execution file for the AimHarder Booking Bot."""

import os
from datetime import datetime

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
TARGET_HOUR = 9


def run_bot(user: str):
    """Main execution function."""
    TARGETS = get_classes_to_book(user=user)
    driver = get_driver()
    try:
        login(driver=driver, user=user)
        driver.get(SCHEDULE_URL)

        while datetime.now().hour < TARGET_HOUR:
            continue

        for target in TARGETS:
            switch_filter(driver=driver, class_id=target["id"])

            for days in target["days_ahead"]:
                book_class(driver=driver, target=target, days_ahead=days)

    finally:
        driver.quit()
