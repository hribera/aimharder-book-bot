#
# AimHarder Booking Bot
# Author: Helena Ribera <heleribera@gmail.com>
# Website: www.hriberaponsa.com
#
"""Main execution file for the AimHarder Booking Bot."""

import os
import concurrent.futures
from datetime import datetime, time

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
TARGET_HOUR = 8
TARGET_MINUTE = 25
TARGET_TIME = time(TARGET_HOUR, TARGET_MINUTE)


def run_single_bot(user: str, target: dict):
    """Main execution function."""
    driver = get_driver()
    try:
        login(driver=driver, user=user)
        driver.get(SCHEDULE_URL)

        # Wait until the precise booking window opens
        while datetime.now().time() < TARGET_TIME:
            continue

        # Each bot now handles one specific class ID
        switch_filter(driver=driver, class_id=target["id"])

        for days in target["days_ahead"]:
            book_class(driver=driver, target=target, days_ahead=days)

    finally:
        driver.quit()


def run_bot(user: str):
    """Start the booking process in parallel for multiple classes."""
    targets = get_classes_to_book(user=user)

    with concurrent.futures.ProcessPoolExecutor(max_workers=len(targets)) as executor:
        futures = [executor.submit(run_single_bot, user, target) for target in targets]

        concurrent.futures.wait(futures)