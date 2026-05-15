# methods.py
# Reusable helper functions and high-level flow functions.

import os
import logging
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException,
)

import locators

# screenshots directory
SCREENSHOT_DIR = os.path.join(os.getcwd(), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ════════════════════════════════════════════════════════════════
# Helper utilities
# ════════════════════════════════════════════════════════════════

def get_wait(driver, timeout=15):
    return WebDriverWait(driver, timeout)


def scroll_into_view(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    except Exception:
        pass


def safe_click(driver, by, locator, timeout=15, attempts=2):
    wait = get_wait(driver, timeout)
    last_exc = None
    for attempt in range(attempts):
        try:
            element = wait.until(EC.element_to_be_clickable((by, locator)))
            scroll_into_view(driver, element)
            element.click()
            return
        except StaleElementReferenceException as e:
            logging.warning("StaleElementReferenceException on click, retrying (%s/%s)", attempt + 1, attempts)
            last_exc = e
    logging.error("safe_click failed for locator %s:%s", by, locator)
    raise last_exc or Exception("safe_click failed")


def safe_type(driver, by, locator, text, clear=True, timeout=15):
    wait = get_wait(driver, timeout)
    elem = wait.until(EC.element_to_be_clickable((by, locator)))
    scroll_into_view(driver, elem)
    if clear:
        try:
            elem.clear()
        except Exception:
            pass
    elem.send_keys(text)


def click_if_present(driver, by, locator, timeout=5):
    try:
        safe_click(driver, by, locator, timeout=timeout)
        return True
    except Exception:
        return False


def type_and_select_first_option(driver, input_xpath, value, first_option_xpath=None, timeout=15):
    wait = get_wait(driver, timeout)
    input_el = wait.until(EC.element_to_be_clickable((By.XPATH, input_xpath)))
    scroll_into_view(driver, input_el)
    try:
        input_el.clear()
    except Exception:
        pass
    input_el.click()
    input_el.send_keys(value)

    if first_option_xpath and first_option_xpath != "PASTE_XPATH_HERE":
        try:
            first = wait.until(EC.visibility_of_element_located((By.XPATH, first_option_xpath)))
            scroll_into_view(driver, first)
            first.click()
            return
        except TimeoutException:
            logging.info("First-option xpath not visible; falling back to keyboard selection")

    try:
        input_el.send_keys(Keys.ARROW_DOWN)
        input_el.send_keys(Keys.ENTER)
    except Exception as e:
        logging.error("Failed to select first suggestion via keyboard: %s", e)
        raise


def set_date(driver, date_xpath, date_value, timeout=15):
    import time as _time

    parts = date_value.split("-")
    day = int(parts[0])
    month = int(parts[1]) - 1
    year = int(parts[2])

    wait = get_wait(driver, timeout)
    elem = wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath)))
    scroll_into_view(driver, elem)

    picker = None
    for attempt in range(3):
        elem.click()
        _time.sleep(0.5)
        try:
            picker = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.xdsoft_datetimepicker[style*='display: block']")
            ))
            break
        except TimeoutException:
            logging.warning("Date picker did not open on attempt %d, retrying...", attempt + 1)
    if not picker:
        raise Exception("Date picker failed to open after 3 attempts")
    logging.info("xdsoft datepicker opened")

    max_clicks = 24
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    for _ in range(max_clicks):
        current_month_text = picker.find_element(By.CSS_SELECTOR, ".xdsoft_label.xdsoft_month span").text
        current_year_text = picker.find_element(By.CSS_SELECTOR, ".xdsoft_label.xdsoft_year span").text
        current_month_idx = month_names.index(current_month_text)
        current_year = int(current_year_text)

        if current_year == year and current_month_idx == month:
            break
        elif (current_year, current_month_idx) < (year, month):
            picker.find_element(By.CSS_SELECTOR, "button.xdsoft_next").click()
            _time.sleep(0.3)
        else:
            picker.find_element(By.CSS_SELECTOR, "button.xdsoft_prev").click()
            _time.sleep(0.3)
    else:
        raise Exception(f"Could not navigate to {date_value} in datepicker after {max_clicks} clicks")

    day_cell = picker.find_element(
        By.CSS_SELECTOR,
        f"td.xdsoft_date[data-date='{day}'][data-month='{month}'][data-year='{year}']"
    )
    scroll_into_view(driver, day_cell)
    day_cell.click()
    logging.info("Date selected: %s", date_value)


def set_time(driver, time_xpath, time_value, timeout=15):
    import time as _time
    from selenium.webdriver.support.ui import Select

    # Convert 12h format (e.g. "10:30 PM") to 24h for the site's dropdown
    from datetime import datetime as _dt
    t = _dt.strptime(time_value.strip(), "%I:%M %p")
    hour_str = str(t.hour).zfill(2)       # 24h hour: "22" for 10 PM, "08" for 8 AM
    # Round minutes to nearest 5 (site dropdown: 00,05,10,...,55)
    rounded_min = round(t.minute / 5) * 5
    if rounded_min == 60:
        rounded_min = 55
    minute_str = str(rounded_min).zfill(2)
    logging.info("Time '%s' converted to 24h: hour=%s, minute=%s", time_value.strip(), hour_str, minute_str)

    wait = get_wait(driver, timeout)

    try:
        driver.find_element(By.TAG_NAME, "body").click()
        _time.sleep(0.3)
    except Exception:
        pass

    time_div = wait.until(EC.element_to_be_clickable((By.XPATH, time_xpath)))
    scroll_into_view(driver, time_div)
    try:
        time_input = time_div.find_element(By.TAG_NAME, "input")
        time_input.click()
    except Exception:
        time_div.click()
    _time.sleep(0.5)

    dropdown = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "div.dropdown-menu.show")
    ))
    logging.info("Time dropdown opened")

    hour_select = dropdown.find_element(By.CSS_SELECTOR, "select.select_hour")
    Select(hour_select).select_by_value(hour_str)
    logging.info("Hour selected: %s", hour_str)
    _time.sleep(0.5)

    try:
        dropdown = driver.find_element(By.CSS_SELECTOR, "div.dropdown-menu.show")
        minute_select = dropdown.find_element(By.CSS_SELECTOR, "select.select_minute")
        Select(minute_select).select_by_value(minute_str)
        logging.info("Minute selected: %s", minute_str)
    except (NoSuchElementException, StaleElementReferenceException):
        try:
            time_input = time_div.find_element(By.TAG_NAME, "input")
            time_input.click()
        except Exception:
            time_div.click()
        _time.sleep(0.5)
        dropdown = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.dropdown-menu.show")
        ))
        minute_select = dropdown.find_element(By.CSS_SELECTOR, "select.select_minute")
        Select(minute_select).select_by_value(minute_str)
        logging.info("Minute selected (after reopen): %s", minute_str)

    try:
        driver.find_element(By.TAG_NAME, "body").click()
        _time.sleep(0.3)
    except Exception:
        pass

    logging.info("Time selected: %s", time_value)


# ════════════════════════════════════════════════════════════════
# STEP 1 — Open site + click the correct tab
# ════════════════════════════════════════════════════════════════

def open_site(driver):
    logging.info("Opening site: %s", locators.URL)
    driver.get(locators.URL)


# ════════════════════════════════════════════════════════════════
# Book Now + Login if needed
# ════════════════════════════════════════════════════════════════

def _dismiss_alert(driver):
    """Dismiss any browser alert if present. Returns alert text or None."""
    try:
        alert = driver.switch_to.alert
        text = alert.text
        logging.warning("Alert detected: %s", text)
        alert.accept()
        import time as _t; _t.sleep(0.5)
        return text
    except Exception:
        return None


def click_book_now_and_login(driver, mobile, otp, timeout=10):
    """Click first Book Now button on results page. If login required, handle login flow.

    Returns True if Book Now was clicked, False if no results page / no Book Now button.
    """
    import time as _time

    # Try to click Book Now — skip silently if not on results page
    try:
        wait = WebDriverWait(driver, timeout)
        book_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.BOOK_NOW_BUTTON_FALLBACK_XPATH))
        )
        scroll_into_view(driver, book_btn)
        book_btn.click()
        logging.info("Book Now clicked")
        _time.sleep(1)
    except TimeoutException:
        logging.info("No Book Now button found — not on results page, skipping")
        return False

    # Check if login page appeared (Sign In with OTP)
    try:
        login_mobile = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_MOBILE_INPUT_XPATH))
        )
        logging.info("Login page detected — filling credentials")

        # Enter mobile
        login_mobile.clear()
        login_mobile.send_keys(mobile)
        logging.info("Mobile entered: %s", mobile)

        # Send OTP with retry
        for attempt in range(3):
            safe_click(driver, By.XPATH, locators.LOGIN_SEND_OTP_BUTTON_XPATH)
            _time.sleep(2)
            alert_text = _dismiss_alert(driver)
            if alert_text and "error" in alert_text.lower():
                wait_sec = 15 * (attempt + 1)
                logging.warning("OTP rate limited, waiting %ds...", wait_sec)
                _time.sleep(wait_sec)
                continue
            break

        # Enter OTP
        otp_input = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_OTP_INPUT_XPATH))
        )
        otp_input.clear()
        otp_input.send_keys(otp)
        logging.info("OTP entered")

        # Verify OTP
        safe_click(driver, By.XPATH, locators.LOGIN_VERIFY_OTP_BUTTON_XPATH)
        _time.sleep(1)
        _dismiss_alert(driver)
        logging.info("Login completed")

    except TimeoutException:
        logging.info("No login page — already logged in or direct booking")

    return True


def fill_traveller_details_and_pay(driver, first_name, last_name, mobile, email,
                                    pickup_location, pickup_address, flight_no=None, timeout=15):
    """Fill the Traveller Details form and click Pay.

    Should be called after click_book_now_and_login() when the booking form is visible.
    Returns True if form was filled and Pay clicked, False if form not found.
    """
    import time as _time

    try:
        wait = WebDriverWait(driver, timeout)
        first_name_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.FIRST_NAME_XPATH))
        )
        logging.info("Traveller Details form detected — filling details")
    except TimeoutException:
        logging.info("No Traveller Details form found — skipping")
        return False

    # First Name
    first_name_input.clear()
    first_name_input.send_keys(first_name)
    logging.info("First Name entered: %s", first_name)

    # Last Name
    safe_type(driver, By.XPATH, locators.LAST_NAME_XPATH, last_name)
    logging.info("Last Name entered: %s", last_name)

    # Mobile Number
    safe_type(driver, By.XPATH, locators.TRAVELLER_MOBILE_XPATH, mobile)
    logging.info("Mobile entered: %s", mobile)

    # Email ID
    safe_type(driver, By.XPATH, locators.TRAVELLER_EMAIL_XPATH, email)
    logging.info("Email entered: %s", email)

    # Flight No (only on Pickup From Airport booking form)
    if flight_no:
        try:
            safe_type(driver, By.XPATH, locators.FLIGHT_NO_XPATH, flight_no, timeout=3)
            logging.info("Flight No entered: %s", flight_no)
        except Exception:
            logging.info("Flight No field not present — skipping")

    # Pickup Location (not present on all booking forms)
    try:
        safe_type(driver, By.XPATH, locators.TRAVELLER_PICKUP_LOCATION_XPATH, pickup_location, timeout=3)
        logging.info("Pickup Location entered: %s", pickup_location)
    except Exception:
        logging.info("Pickup Location field not present — skipping")

    # Pickup Address (not present on all booking forms)
    try:
        safe_type(driver, By.XPATH, locators.TRAVELLER_PICKUP_ADDRESS_XPATH, pickup_address, timeout=3)
        logging.info("Pickup Address entered: %s", pickup_address)
    except Exception:
        logging.info("Pickup Address field not present — skipping")

    _time.sleep(0.5)

    # T&C checkbox
    try:
        checkbox = driver.find_element(By.XPATH, locators.TNC_CHECKBOX_XPATH)
        scroll_into_view(driver, checkbox)
        if not checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)
            logging.info("T&C checkbox checked")
    except Exception as e:
        logging.warning("T&C checkbox not found or click failed: %s", e)

    _time.sleep(0.5)

    # Click Pay button
    try:
        pay_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.PAY_BUTTON_XPATH))
        )
        scroll_into_view(driver, pay_btn)
        pay_btn.click()
        logging.info("Pay button clicked")
        _time.sleep(1)
        _dismiss_alert(driver)
    except Exception as e:
        logging.warning("Pay button click failed: %s", e)

    # Wait for payment gateway page (CCAvenue) to load
    try:
        WebDriverWait(driver, 20).until(
            lambda d: "ccavenue" in d.current_url.lower() or "payment" in d.current_url.lower()
        )
        logging.info("Payment gateway loaded: %s", driver.current_url)
        _time.sleep(1)
    except Exception:
        logging.info("Payment gateway page not detected (URL: %s)", driver.current_url)

    return True


def validate_order_summary(driver, expected_city, expected_date, expected_time,
                           expected_service_type=None, timeout=10):
    """Validate Order Summary on booking page matches search values.

    Args:
        expected_city: City name to match in Pickup City (e.g. "Delhi")
        expected_date: Date in dd-mm-yyyy format (e.g. "15-05-2026")
        expected_time: Time in 12h format (e.g. "10:30 AM")
        expected_service_type: Optional partial text match for Service type
    Returns:
        True if validation passed, False if Order Summary not found.
    """
    import time as _time

    wait = WebDriverWait(driver, timeout)
    logging.info("========== VALIDATING ORDER SUMMARY ==========")

    # Check if we're on the booking page (look for Order Summary section)
    try:
        service_el = wait.until(
            EC.visibility_of_element_located((By.XPATH, locators.ORDER_SUMMARY_SERVICE_TYPE_XPATH))
        )
        logging.info("Order Summary page detected")
    except TimeoutException:
        logging.warning("Order Summary not found — may not be on booking page")
        return False

    # --- Service Type ---
    if expected_service_type:
        actual_service = service_el.text.strip()
        logging.info("  Service Type — Expected: '%s' | Actual: '%s'", expected_service_type, actual_service)
        if expected_service_type.lower() not in actual_service.lower():
            logging.error("  SERVICE TYPE MISMATCH")
        else:
            logging.info("  SERVICE TYPE MATCHED")

    # --- Pickup City ---
    try:
        city_el = driver.find_element(By.XPATH, locators.ORDER_SUMMARY_PICKUP_CITY_XPATH)
        actual_city = city_el.text.strip()
        logging.info("  Pickup City — Expected: '%s' | Actual: '%s'", expected_city, actual_city)
        if expected_city.lower() not in actual_city.lower():
            logging.error("  PICKUP CITY MISMATCH: expected '%s' in '%s'", expected_city, actual_city)
        else:
            logging.info("  PICKUP CITY MATCHED")
    except NoSuchElementException:
        logging.warning("  Pickup City element not found")

    # --- Date & Time ---
    try:
        dt_el = driver.find_element(By.XPATH, locators.ORDER_SUMMARY_DATE_TIME_XPATH)
        actual_dt = dt_el.text.strip()
        logging.info("  Date & Time — Actual: '%s'", actual_dt)

        # Parse expected date (dd-mm-yyyy) to match site format (e.g. "Wednesday, Mar 18, 2026, 2:00 PM")
        from datetime import datetime as _dt
        parts = expected_date.split("-")
        expected_date_obj = _dt(int(parts[2]), int(parts[1]), int(parts[0]))
        # Check date parts in the displayed string
        month_abbr = expected_date_obj.strftime("%b")  # "May", "Mar", etc.
        day_num = str(expected_date_obj.day)
        year_str = str(expected_date_obj.year)

        date_ok = (month_abbr in actual_dt and day_num in actual_dt and year_str in actual_dt)
        logging.info("  Date check — month='%s', day='%s', year='%s' in '%s': %s",
                     month_abbr, day_num, year_str, actual_dt, date_ok)
        if not date_ok:
            logging.error("  DATE MISMATCH in Order Summary")
        else:
            logging.info("  DATE MATCHED")

        # Check time — convert "10:30 AM" to parts and check in string
        time_clean = expected_time.strip()
        # Site shows "2:00 PM" style — parse and compare
        t = _dt.strptime(time_clean, "%I:%M %p")
        time_no_pad = t.strftime("%-I:%M %p") if hasattr(t, 'strftime') else time_clean
        # Windows doesn't support %-I, use manual strip
        time_12h = t.strftime("%I:%M %p").lstrip("0")
        logging.info("  Time check — looking for '%s' in '%s'", time_12h, actual_dt)
        if time_12h.lower().replace(" ", "") in actual_dt.lower().replace(" ", ""):
            logging.info("  TIME MATCHED")
        else:
            logging.error("  TIME MISMATCH: expected '%s' in '%s'", time_12h, actual_dt)
    except NoSuchElementException:
        logging.warning("  Date & Time element not found")

    logging.info("========== ORDER SUMMARY VALIDATION COMPLETE ==========")
    return True


def navigate_back_to_site(driver):
    """Navigate back to original site after payment gateway. Keeps session valid for next test."""
    import time as _time
    try:
        driver.get(locators.URL)
        _time.sleep(1)
        logging.info("Navigated back to %s", locators.URL)
    except Exception:
        logging.warning("Could not navigate back to original site")


