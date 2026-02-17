#
# AimHarder Booking Bot
# Author: Helena Ribera <heleribera@gmail.com>
# Website: www.hriberaponsa.com
#
"""Main execution file for the AimHarder Booking Bot."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
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
TARGET_HOUR = 18
TARGET_MINUTE = 0
TARGET_TIME = time(TARGET_HOUR, TARGET_MINUTE)


def run_target_day(user: str, target: dict, days_ahead: int):
    """Runs the target day of the booking bot."""
    driver = get_driver()
    try:
        login(driver=driver, user=user)
        driver.get(SCHEDULE_URL)

        while datetime.now().time() < TARGET_TIME:
            continue

        switch_filter(driver=driver, class_id=target["id"])
        book_class(driver=driver, target=target, days_ahead=days_ahead)
    finally:
        driver.quit()


def run_bot(user: str):
    """Main execution function."""
    TARGETS = get_classes_to_book(user=user)

    tasks = [
        (user, target, days) for target in TARGETS for days in target["days_ahead"]
    ]

    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = {
            executor.submit(run_target_day, user, target, days): (target, days)
            for user, target, days in tasks
        }
        for future in as_completed(futures):
            target, days = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Target {target['id']}, days_ahead={days} failed: {e}")
