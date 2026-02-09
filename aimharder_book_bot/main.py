"""Automated class booking bot for AimHarder platform using Selenium."""

import os
import sys
import time
from datetime import date, timedelta

from dotenv import load_dotenv
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# --- CONFIGURATION ---
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Validate credentials
if not EMAIL or not PASSWORD:
    logger.error("EMAIL and PASSWORD must be set in your .env file.")
    sys.exit(1)

# List of classes you want to book
TARGETS = [
    {
        "name": "Hyrox",
        "id": "25375",
        "time": "17:00 - 18:00",
        "days_ahead": [1, 3],  # Book Monday and Wednesday
    },
    {
        "name": "Hyrox",
        "id": "25375",
        "time": "18:00 - 19:00",
        "days_ahead": [4],  # Book Thursday
    },
    {
        "name": "Strength & Conditioning",
        "id": "27780",
        "time": "17:00 - 18:00",
        "days_ahead": [4],  # Book Thursday
    },
]

SCHEDULE_URL = "https://crossfitgaragelasagrera.aimharder.com/schedule"


def get_driver():
    """Initializes the Chrome driver with options."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    return webdriver.Chrome(options=options)


def login(driver):
    """Handles the login process."""
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


def book_class(driver, target, days_ahead):
    """Logic to find and book a specific class."""
    target_name = target["name"]
    target_time = target["time"]

    booking_date = date.today() + timedelta(days=days_ahead)
    formatted_date = booking_date.strftime("%d/%m/%Y")

    logger.info(
        f"\n--- Checking {target_name} ({target_time}) for {formatted_date} ---"
    )

    wait = WebDriverWait(driver, 10)

    # 1. Set the Date
    try:
        date_input = wait.until(EC.element_to_be_clickable((By.ID, "selw")))
        date_input.clear()
        date_input.send_keys(formatted_date)
        date_input.send_keys(Keys.ENTER)
        time.sleep(1)
    except Exception as e:
        logger.error(f"Error setting date: {e}")
        return

    # 2. Scan and Book
    found = False
    attempts = 0

    while not found and attempts < 3:
        try:
            blocks = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div.bloqueClase")
                )
            )

            for block in blocks:
                # Use strict text matching or 'in' depending on how exact the site labels are
                name_text = block.find_element(
                    By.CSS_SELECTOR, "span.rvNombreCl"
                ).text.strip()
                time_text = block.find_element(
                    By.CSS_SELECTOR, "span.rvHora"
                ).text.strip()

                # Basic check: Name contains "CrossFit" (or whatever) AND time matches
                if (target_name.lower() in name_text.lower()) and (
                    time_text == target_time
                ):
                    logger.info(f"Found match: {name_text} at {time_text}")

                    try:
                        reservar_btn = block.find_element(
                            By.XPATH, ".//a[contains(text(), 'Reservar')]"
                        )
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});",
                            reservar_btn,
                        )
                        time.sleep(0.5)

                        driver.execute_script("arguments[0].click();", reservar_btn)

                        # Confirm modal
                        try:
                            confirm_btn = WebDriverWait(driver, 3).until(
                                EC.element_to_be_clickable(
                                    (
                                        By.XPATH,
                                        "//button[contains(text(), 'Confirmar') or contains(text(), 'Aceptar')]",
                                    )
                                )
                            )
                            confirm_btn.click()
                            logger.info(f"SUCCESS: Booked {target_name}!")
                        except TimeoutException:
                            logger.info("No confirmation needed or missed.")

                        found = True
                        break

                    except NoSuchElementException:
                        if "Cancelar" in block.text:
                            print("Status: Already Booked.")
                            found = True
                        elif "Lista de Espera" in block.text:
                            print("Status: Waitlist Only.")
                            found = True
                        else:
                            print("Status: Button not found (Full?).")
                    break

            if not found:
                logger.warning(f"Target not found. Retrying scan... ({attempts + 1}/3)")
                time.sleep(1)
                attempts += 1
            else:
                break

        except StaleElementReferenceException:
            attempts += 1
            continue
        except Exception as e:
            logger.error(f"Error scanning blocks: {e}")
            break


def run_bot():
    """Main execution function."""
    driver = get_driver()
    try:
        login(driver)
        driver.get(SCHEDULE_URL)

        # Iterate through every target configuration
        for target in TARGETS:
            # 1. Switch the dropdown filter first
            switch_filter(driver, target["id"])

            # 2. Check all requested days for this class
            for days in target["days_ahead"]:
                book_class(driver, target, days)

    finally:
        driver.quit()
