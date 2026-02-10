#
# AimHarder Booking Bot
# Author: Helena Ribera <heleribera@gmail.com>
# Website: https://hriberaponsa.com
#
"""Utility functions for the aimharder_book_bot."""

import os
import time

import yaml
from dotenv import load_dotenv
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

config = yaml.safe_load(open("aimharder_book_bot/config.yml"))

load_dotenv()
SCHEDULE_URL = os.getenv("SCHEDULE_URL")


def get_classes_to_book(user: str):
    """Reads the config file and returns a list of classes to book for a given user."""
    TARGETS = []
    for activity_name, activity in config["users"][user]["classes"].items():
        for session in activity["sessions"]:
            TARGETS.append(
                {
                    "name": activity_name.replace("_", " ").title(),
                    "id": str(activity["id"]),
                    "time": session["time"],
                    "days_ahead": session["days_ahead"],
                }
            )
    return TARGETS


def get_driver():
    """Initializes the Chrome driver with options."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    return webdriver.Chrome(options=options)


def login(driver, user: str):
    """Handles the login process."""
    EMAIL = os.getenv(config["users"][user]["credentials"]["email"])
    PASSWORD = os.getenv(config["users"][user]["credentials"]["password"])

    logger.info("Logging in...")
    driver.get("https://aimharder.com/login")

    # Handle GDPR manually if needed
    driver.add_cookie(
        {
            "name": "ahgdprcookie_v2",
            "value": "1",
            "path": "/",
            "domain": "aimharder.com",
        }
    )
    driver.refresh()

    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.element_to_be_clickable((By.ID, "mail"))).send_keys(EMAIL)
        wait.until(EC.element_to_be_clickable((By.ID, "pw"))).send_keys(PASSWORD)
        wait.until(EC.element_to_be_clickable((By.ID, "loginSubmit"))).click()
        wait.until(EC.url_changes("https://aimharder.com/login"))
        logger.info("Login successful.")
    except TimeoutException:
        logger.error("Login failed or timed out.")
        raise


def switch_filter(driver, class_id):
    """Switches the schedule view to the specific class ID."""
    try:
        wait = WebDriverWait(driver, 10)
        select_elem = wait.until(
            EC.presence_of_element_located((By.ID, "filtroClases"))
        )
        select = Select(select_elem)
        select.select_by_value(class_id)

        # Wait a moment for the table to reload after filtering
        time.sleep(1.5)
    except Exception as e:
        logger.error(f"Error switching filter to ID {class_id}: {e}")
