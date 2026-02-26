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
import testdata

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
        _time.sleep(1)
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

    clean = time_value.strip().upper().replace(" AM", "").replace(" PM", "")
    h, m = clean.split(":")
    hour_str = h.strip().zfill(2)
    minute_str = m.strip().zfill(2)

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
    _time.sleep(1)

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


def _get_service_type():
    """Return normalised service type string."""
    return testdata.SERVICE_TYPE.strip().lower()


def click_service_tab(driver):
    """Click the correct tab based on SERVICE_TYPE."""
    stype = _get_service_type()
    logging.info("Service type selected: %s", testdata.SERVICE_TYPE)

    if "airport" in stype:
        safe_click(driver, By.XPATH, locators.AIRPORT_TRANSFER_TAB_XPATH)
    elif "local" in stype:
        safe_click(driver, By.XPATH, locators.LOCAL_RENTAL_TAB_XPATH)
    elif "outstation" in stype:
        safe_click(driver, By.XPATH, locators.OUTSTATION_TRIP_TAB_XPATH)
    elif "self" in stype:
        safe_click(driver, By.XPATH, locators.SELF_DRIVE_TAB_XPATH)
    else:
        raise ValueError(f"Unknown SERVICE_TYPE: '{testdata.SERVICE_TYPE}'. "
                         "Use: Airport Transfer | Local Rental | Outstation Trip | Self Drive")


# ════════════════════════════════════════════════════════════════
# STEP 2 — Fill the search form (per service type)
# ════════════════════════════════════════════════════════════════

def fill_search_form(driver):
    """Auto-dispatch to the correct form filler based on SERVICE_TYPE."""
    stype = _get_service_type()
    if "airport" in stype:
        _fill_airport_transfer_form(driver)
    elif "local" in stype:
        _fill_local_rental_form(driver)
    elif "outstation" in stype:
        _fill_outstation_trip_form(driver)
    elif "self" in stype:
        _fill_self_drive_form(driver)


def _fill_airport_transfer_form(driver):
    """Fill Airport Transfer: direction, city, date, time."""
    logging.info("Selecting direction -> %s", testdata.AIRPORT_DIRECTION)
    safe_click(driver, By.XPATH, locators.DIRECTION_SELECT_XPATH)

    direction_lower = testdata.AIRPORT_DIRECTION.strip().lower()
    option_xpath = locators.DIRECTION_OPTION_XPATH_TEMPLATE.format(direction_lower)
    safe_click(driver, By.XPATH, option_xpath)

    logging.info("Typing City -> %s", testdata.AIRPORT_CITY)
    type_and_select_first_option(
        driver,
        locators.AIRPORT_CITY_XPATH,
        testdata.AIRPORT_CITY,
        first_option_xpath=locators.AIRPORT_CITY_FIRST_OPTION_XPATH,
    )

    logging.info("Setting date -> %s", testdata.AIRPORT_DATE)
    set_date(driver, locators.AIRPORT_DATE_XPATH, testdata.AIRPORT_DATE)

    logging.info("Setting time -> %s", testdata.AIRPORT_TIME)
    set_time(driver, locators.AIRPORT_TIME_XPATH, testdata.AIRPORT_TIME)


def _fill_local_rental_form(driver):
    """Fill Local Rental: city, package, date, time."""
    logging.info("Typing City -> %s", testdata.LOCAL_RENTAL_CITY)
    type_and_select_first_option(
        driver,
        locators.LOCAL_RENTAL_CITY_XPATH,
        testdata.LOCAL_RENTAL_CITY,
        first_option_xpath=locators.LOCAL_RENTAL_CITY_FIRST_OPTION_XPATH,
    )

    logging.info("Selecting Package -> %s", testdata.LOCAL_RENTAL_PACKAGE)
    safe_click(driver, By.XPATH, locators.LOCAL_RENTAL_PACKAGE_XPATH)
    package_lower = testdata.LOCAL_RENTAL_PACKAGE.strip().lower()
    option_xpath = locators.LOCAL_RENTAL_PACKAGE_OPTION_XPATH_TEMPLATE.format(package_lower)
    safe_click(driver, By.XPATH, option_xpath)

    logging.info("Setting date -> %s", testdata.LOCAL_RENTAL_DATE)
    set_date(driver, locators.LOCAL_RENTAL_DATE_XPATH, testdata.LOCAL_RENTAL_DATE)

    logging.info("Setting time -> %s", testdata.LOCAL_RENTAL_TIME)
    set_time(driver, locators.LOCAL_RENTAL_TIME_XPATH, testdata.LOCAL_RENTAL_TIME)


def _fill_outstation_trip_form(driver):
    """Fill Outstation Trip: trip type, from city, to city, date, time."""
    # Trip Type (case-insensitive)
    logging.info("Selecting Trip Type -> %s", testdata.OUTSTATION_TRIP_TYPE)
    safe_click(driver, By.XPATH, locators.OUTSTATION_TRIP_TYPE_XPATH)
    trip_type_lower = testdata.OUTSTATION_TRIP_TYPE.strip().lower()
    option_xpath = locators.OUTSTATION_TRIP_TYPE_OPTION_XPATH_TEMPLATE.format(trip_type_lower)
    safe_click(driver, By.XPATH, option_xpath)

    # From City
    logging.info("Typing From City -> %s", testdata.OUTSTATION_FROM_CITY)
    type_and_select_first_option(
        driver,
        locators.OUTSTATION_FROM_CITY_XPATH,
        testdata.OUTSTATION_FROM_CITY,
        first_option_xpath=locators.OUTSTATION_FROM_CITY_FIRST_OPTION_XPATH,
    )

    # To City
    logging.info("Typing To City -> %s", testdata.OUTSTATION_TO_CITY)
    type_and_select_first_option(
        driver,
        locators.OUTSTATION_TO_CITY_XPATH,
        testdata.OUTSTATION_TO_CITY,
        first_option_xpath=locators.OUTSTATION_TO_CITY_FIRST_OPTION_XPATH,
    )

    # Date
    logging.info("Setting date -> %s", testdata.OUTSTATION_DATE)
    set_date(driver, locators.OUTSTATION_DATE_XPATH, testdata.OUTSTATION_DATE)

    # Time
    logging.info("Setting time -> %s", testdata.OUTSTATION_TIME)
    set_time(driver, locators.OUTSTATION_TIME_XPATH, testdata.OUTSTATION_TIME)


def _fill_self_drive_form(driver):
    """Fill Self Drive query form: name, mobile, email, city, vehicle type, date, days."""
    import time as _time

    logging.info("Filling Self Drive query form")

    # Name
    safe_type(driver, By.XPATH, locators.SELF_DRIVE_NAME_XPATH, testdata.SELF_DRIVE_NAME)

    # Mobile
    safe_type(driver, By.XPATH, locators.SELF_DRIVE_MOBILE_XPATH, testdata.SELF_DRIVE_MOBILE)

    # Email
    safe_type(driver, By.XPATH, locators.SELF_DRIVE_EMAIL_XPATH, testdata.SELF_DRIVE_EMAIL)

    # City
    safe_type(driver, By.XPATH, locators.SELF_DRIVE_CITY_XPATH, testdata.SELF_DRIVE_CITY)

    # Vehicle Type
    safe_type(driver, By.XPATH, locators.SELF_DRIVE_VEHICLE_TYPE_XPATH, testdata.SELF_DRIVE_VEHICLE_TYPE)

    # Travel Date
    set_date(driver, locators.SELF_DRIVE_TRAVEL_DATE_XPATH, testdata.SELF_DRIVE_TRAVEL_DATE)

    # No. of days
    safe_type(driver, By.XPATH, locators.SELF_DRIVE_NO_OF_DAYS_XPATH, testdata.SELF_DRIVE_NO_OF_DAYS)
    _time.sleep(0.5)


def submit_self_drive_query(driver):
    """Click Submit your Query button for Self Drive."""
    import time as _time
    logging.info("Clicking Submit your Query")
    safe_click(driver, By.XPATH, locators.SELF_DRIVE_SUBMIT_BUTTON_XPATH)
    _time.sleep(2)
    logging.info("Self Drive query submitted")


def is_self_drive():
    """Check if the current service type is Self Drive."""
    return "self" in _get_service_type()


# ════════════════════════════════════════════════════════════════
# STEP 3 — Click Search Your Ride
# ════════════════════════════════════════════════════════════════

def click_search_ride(driver):
    """Click the Search button for the active service type."""
    import time as _time

    stype = _get_service_type()
    if "local" in stype:
        button_xpath = locators.LOCAL_RENTAL_SEARCH_BUTTON_XPATH
    elif "outstation" in stype:
        button_xpath = locators.OUTSTATION_SEARCH_BUTTON_XPATH
    else:
        button_xpath = locators.AIRPORT_SEARCH_BUTTON_XPATH

    logging.info("Clicking Search Your Ride")
    safe_click(driver, By.XPATH, button_xpath)

    _time.sleep(2)

    error_selectors = [
        "div.toast-body", "div.toast-message", "div.Toastify__toast--error",
        "div.alert-danger", "div.swal2-popup", "div.toast.show",
    ]
    for sel in error_selectors:
        try:
            error_el = driver.find_element(By.CSS_SELECTOR, sel)
            if error_el.is_displayed():
                error_text = error_el.text.strip()
                logging.error("Error toast detected: %s", error_text)
                raise Exception(f"Search Your Ride error: {error_text}")
        except NoSuchElementException:
            continue

    logging.info("Search clicked — no error toast detected")


# ════════════════════════════════════════════════════════════════
# STEP 4 — Validate results
# ════════════════════════════════════════════════════════════════

def assert_results_loaded(driver, timeout=15):
    wait = get_wait(driver, timeout)
    logging.info("Waiting for results")
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, locators.RESULTS_CONTAINER_XPATH)))
        logging.info("Results container visible")
        return True
    except TimeoutException:
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, locators.RESULTS_PAGE_UNIQUE_XPATH)))
            logging.info("Results page unique element visible")
            return True
        except TimeoutException:
            try:
                no_rides = driver.find_element(By.XPATH, locators.NO_RIDES_MESSAGE_XPATH)
                logging.info("No rides message: %s", no_rides.text)
                return False
            except Exception:
                logging.error("Results did not load and no 'no rides' message found")
                raise


# ════════════════════════════════════════════════════════════════
# STEP 5 — Click Book Now
# ════════════════════════════════════════════════════════════════

def click_book_now(driver, timeout=15):
    """Click Book Now for the car matching the active service type."""
    import time as _time

    stype = _get_service_type()
    if "local" in stype:
        car_name = testdata.LOCAL_RENTAL_CAR_NAME
    elif "outstation" in stype:
        car_name = testdata.OUTSTATION_CAR_NAME
    else:
        car_name = testdata.AIRPORT_CAR_NAME

    logging.info("Looking for car: %s", car_name)
    wait = get_wait(driver, timeout)

    car_xpath = locators.BOOK_NOW_BUTTON_XPATH_TEMPLATE.format(car_name.strip().lower())
    try:
        book_btn = wait.until(EC.element_to_be_clickable((By.XPATH, car_xpath)))
        logging.info("Found '%s' - clicking Book Now", car_name)
    except TimeoutException:
        logging.warning("Car '%s' not found, clicking first available", car_name)
        book_btn = wait.until(EC.element_to_be_clickable((By.XPATH, locators.BOOK_NOW_BUTTON_FALLBACK_XPATH)))

    scroll_into_view(driver, book_btn)
    book_btn.click()
    logging.info("Book Now clicked")
    _time.sleep(3)


# ════════════════════════════════════════════════════════════════
# STEP 6 — OTP (mobile + verify)
# ════════════════════════════════════════════════════════════════

def fill_mobile_and_send_otp(driver, timeout=15):
    logging.info("Filling mobile number: %s", testdata.MOBILE_NUMBER)
    wait = get_wait(driver, timeout)
    mobile_input = wait.until(EC.element_to_be_clickable((By.XPATH, locators.MOBILE_NUMBER_INPUT_XPATH)))
    scroll_into_view(driver, mobile_input)
    mobile_input.clear()
    mobile_input.send_keys(testdata.MOBILE_NUMBER)
    safe_click(driver, By.XPATH, locators.SEND_OTP_BUTTON_XPATH)
    logging.info("SEND OTP clicked")


def fill_otp_and_verify(driver, timeout=15):
    import time as _time
    wait = get_wait(driver, timeout)

    _time.sleep(2)
    otp_input = wait.until(EC.element_to_be_clickable((By.XPATH, locators.OTP_INPUT_XPATH)))
    scroll_into_view(driver, otp_input)
    otp_input.click()
    _time.sleep(0.5)

    otp_value = testdata.OTP_VALUE
    logging.info("Entering OTP: %s", otp_value)
    otp_input.send_keys(otp_value)
    _time.sleep(1)

    filled_value = otp_input.get_attribute("value") or ""
    if len(filled_value) < 6:
        logging.warning("OTP not filled properly, retrying...")
        otp_input.clear()
        _time.sleep(0.5)
        otp_input.send_keys(otp_value)
        _time.sleep(1)

    safe_click(driver, By.XPATH, locators.VERIFY_OTP_BUTTON_XPATH)
    logging.info("VERIFY OTP clicked")
    _time.sleep(3)


# ════════════════════════════════════════════════════════════════
# STEP 7 — Fill booking form (per service type)
# ════════════════════════════════════════════════════════════════

def fill_booking_form(driver, timeout=15):
    """Auto-dispatch to the correct booking form based on SERVICE_TYPE."""
    stype = _get_service_type()
    if "airport" in stype:
        direction = testdata.AIRPORT_DIRECTION.strip().lower()
        if "pickup" in direction:
            _fill_booking_pickup_from_airport(driver, timeout)
        else:
            _fill_booking_drop_to_airport(driver, timeout)
    elif "local" in stype:
        _fill_booking_local_rental(driver, timeout)
    elif "outstation" in stype:
        _fill_booking_outstation_trip(driver, timeout)
    elif "self" in stype:
        pass  # Self Drive has no booking form — query only


def _fill_booking_pickup_from_airport(driver, timeout=15):
    import time as _time
    logging.info("Filling booking form: Pickup From Airport")
    wait = get_wait(driver, timeout)

    # Last Name
    last_name = wait.until(EC.element_to_be_clickable((By.XPATH, locators.LAST_NAME_XPATH)))
    scroll_into_view(driver, last_name)
    last_name.click()
    last_name.clear()
    last_name.send_keys(testdata.AIRPORT_LAST_NAME)

    # Flight No
    flight_no = wait.until(EC.element_to_be_clickable((By.XPATH, locators.FLIGHT_NO_XPATH)))
    scroll_into_view(driver, flight_no)
    flight_no.click()
    flight_no.clear()
    flight_no.send_keys(testdata.PICKUP_FLIGHT_NO)
    _time.sleep(0.5)

    # Drop Address
    drop_addr = wait.until(EC.element_to_be_clickable((By.XPATH, locators.DROP_ADDRESS_XPATH)))
    scroll_into_view(driver, drop_addr)
    drop_addr.click()
    drop_addr.clear()
    drop_addr.send_keys(testdata.PICKUP_DROP_ADDRESS)
    _time.sleep(0.5)


def _fill_booking_drop_to_airport(driver, timeout=15):
    import time as _time
    logging.info("Filling booking form: Drop To Airport")
    wait = get_wait(driver, timeout)

    # Last Name
    last_name = wait.until(EC.element_to_be_clickable((By.XPATH, locators.LAST_NAME_XPATH)))
    scroll_into_view(driver, last_name)
    last_name.click()
    last_name.clear()
    last_name.send_keys(testdata.AIRPORT_LAST_NAME)

    # Pickup Location (Google Places autocomplete)
    pickup_loc = wait.until(EC.element_to_be_clickable((By.XPATH, locators.PICKUP_LOCATION_XPATH)))
    scroll_into_view(driver, pickup_loc)
    pickup_loc.click()
    pickup_loc.clear()
    pickup_loc.send_keys(testdata.DROP_PICKUP_LOCATION)
    _time.sleep(2)
    try:
        first_suggestion = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.pac-container div.pac-item:first-child")
        ))
        first_suggestion.click()
    except TimeoutException:
        pickup_loc.send_keys(Keys.ARROW_DOWN)
        pickup_loc.send_keys(Keys.ENTER)
    _time.sleep(1)

    # Pickup Address
    pickup_addr = wait.until(EC.element_to_be_clickable((By.XPATH, locators.PICKUP_ADDRESS_XPATH)))
    scroll_into_view(driver, pickup_addr)
    pickup_addr.click()
    pickup_addr.clear()
    pickup_addr.send_keys(testdata.DROP_PICKUP_ADDRESS)
    _time.sleep(0.5)


def _fill_booking_outstation_trip(driver, timeout=15):
    import time as _time
    logging.info("Filling booking form: Outstation Trip")
    wait = get_wait(driver, timeout)

    # Last Name
    last_name = wait.until(EC.element_to_be_clickable((By.XPATH, locators.LAST_NAME_XPATH)))
    scroll_into_view(driver, last_name)
    last_name.click()
    last_name.clear()
    last_name.send_keys(testdata.OUTSTATION_LAST_NAME)

    # Pickup Address
    pickup_addr = wait.until(EC.element_to_be_clickable((By.XPATH, locators.PICKUP_ADDRESS_XPATH)))
    scroll_into_view(driver, pickup_addr)
    pickup_addr.click()
    pickup_addr.clear()
    pickup_addr.send_keys(testdata.OUTSTATION_PICKUP_ADDRESS)
    _time.sleep(0.5)


def _fill_booking_local_rental(driver, timeout=15):
    import time as _time
    logging.info("Filling booking form: Local Rental")
    wait = get_wait(driver, timeout)

    # Last Name
    last_name = wait.until(EC.element_to_be_clickable((By.XPATH, locators.LAST_NAME_XPATH)))
    scroll_into_view(driver, last_name)
    last_name.click()
    last_name.clear()
    last_name.send_keys(testdata.LOCAL_RENTAL_LAST_NAME)

    # Pickup Address
    pickup_addr = wait.until(EC.element_to_be_clickable((By.XPATH, locators.PICKUP_ADDRESS_XPATH)))
    scroll_into_view(driver, pickup_addr)
    pickup_addr.click()
    pickup_addr.clear()
    pickup_addr.send_keys(testdata.LOCAL_RENTAL_PICKUP_ADDRESS)
    _time.sleep(0.5)


# ════════════════════════════════════════════════════════════════
# STEP 8 — T&C + Pay
# ════════════════════════════════════════════════════════════════

def tick_tnc_and_pay(driver, timeout=15):
    import time as _time
    wait = get_wait(driver, timeout)

    logging.info("Ticking T&C checkbox")
    checkbox = wait.until(EC.presence_of_element_located((By.XPATH, locators.TNC_CHECKBOX_XPATH)))
    scroll_into_view(driver, checkbox)
    if not checkbox.is_selected():
        driver.execute_script("arguments[0].click();", checkbox)
    logging.info("T&C checkbox ticked")
    _time.sleep(1)

    logging.info("Clicking Pay button")
    safe_click(driver, By.XPATH, locators.PAY_BUTTON_XPATH)
    logging.info("Pay button clicked")
    _time.sleep(3)
