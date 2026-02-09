"""Core booking logic for the AimHarder booking bot."""

import time
from datetime import date, timedelta

from loguru import logger
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def book_class(driver, target, days_ahead):
    """Logic to find and book a specific class."""
    target_name = target["name"]
    target_time = target["time"]

    booking_date = date.today() + timedelta(days=days_ahead)
    formatted_date = booking_date.strftime("%d/%m/%Y")

    logger.info(f"Checking {target_name} ({target_time}) for {formatted_date}...")

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
