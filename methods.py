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


# Helper utilities
def get_wait(driver, timeout=15):
    """Return a WebDriverWait instance for the driver."""
    return WebDriverWait(driver, timeout)


def scroll_into_view(driver, element):
    """Scroll element into view (best-effort)."""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    except Exception:
        # not critical; swallow to keep robustness
        pass


def safe_click(driver, by, locator, timeout=15, attempts=2):
    """
    Wait for element to be clickable, scroll into view, and click.
    Retries once on StaleElementReferenceException.
    """
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
    """
    Wait for element to be present/clickable, optionally clear, then send keys.
    """
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
    """Click element if present and clickable within timeout; otherwise no-op."""
    try:
        safe_click(driver, by, locator, timeout=timeout)
        return True
    except Exception:
        return False


def type_and_select_first_option(driver, input_xpath, value, first_option_xpath=None, timeout=15):
    """
    Type into an autocomplete input and select the first suggestion.
    If first_option_xpath is provided, click it when visible.
    Otherwise, fallback to ARROWDOWN + ENTER.
    """
    wait = get_wait(driver, timeout)
    # focus and type
    input_el = wait.until(EC.element_to_be_clickable((By.XPATH, input_xpath)))
    scroll_into_view(driver, input_el)
    try:
        input_el.clear()
    except Exception:
        pass
    input_el.click()
    input_el.send_keys(value)

    # if a specific first option locator is provided, try clicking it
    if first_option_xpath and first_option_xpath != "PASTE_XPATH_HERE":
        try:
            first = wait.until(EC.visibility_of_element_located((By.XPATH, first_option_xpath)))
            scroll_into_view(driver, first)
            first.click()
            return
        except TimeoutException:
            logging.info("First-option xpath provided but not visible; falling back to keyboard selection")

    # fallback keyboard selection
    # Wait briefly for suggestions to appear (explicit wait for any suggestion)
    try:
        # try to wait for a common suggestion element near input (not provided), short sleep avoided
        input_el.send_keys(Keys.ARROW_DOWN)
        input_el.send_keys(Keys.ENTER)
    except Exception as e:
        logging.error("Failed to select first suggestion via keyboard: %s", e)
        raise


def set_date(driver, date_xpath, date_value, timeout=15):
    """
    Set a date in xdsoft DateTimePicker.
    date_value format: DD-MM-YYYY (e.g. "28-02-2026")
    Clicks the input to open the calendar, navigates to correct month/year,
    then clicks the target day cell.
    """
    import time as _time

    # Parse date_value (DD-MM-YYYY)
    parts = date_value.split("-")
    day = int(parts[0])
    month = int(parts[1]) - 1  # xdsoft uses 0-indexed months
    year = int(parts[2])

    wait = get_wait(driver, timeout)
    elem = wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath)))
    scroll_into_view(driver, elem)

    # Click date input and wait for picker to open (retry if needed)
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

    # Navigate to correct month/year using prev/next buttons
    max_clicks = 24  # safety limit
    for _ in range(max_clicks):
        # Read current displayed month and year from the picker
        current_month_text = picker.find_element(
            By.CSS_SELECTOR, ".xdsoft_label.xdsoft_month span"
        ).text
        current_year_text = picker.find_element(
            By.CSS_SELECTOR, ".xdsoft_label.xdsoft_year span"
        ).text

        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        current_month_idx = month_names.index(current_month_text)
        current_year = int(current_year_text)

        # Compare: target is (year, month) vs (current_year, current_month_idx)
        if current_year == year and current_month_idx == month:
            break  # correct month/year displayed
        elif (current_year, current_month_idx) < (year, month):
            picker.find_element(By.CSS_SELECTOR, "button.xdsoft_next").click()
            _time.sleep(0.3)
        else:
            picker.find_element(By.CSS_SELECTOR, "button.xdsoft_prev").click()
            _time.sleep(0.3)
    else:
        raise Exception(f"Could not navigate to {date_value} in datepicker after {max_clicks} clicks")

    # Click the target day cell
    day_cell = picker.find_element(
        By.CSS_SELECTOR,
        f"td.xdsoft_date[data-date='{day}'][data-month='{month}'][data-year='{year}']"
    )
    scroll_into_view(driver, day_cell)
    day_cell.click()
    logging.info("Date selected in xdsoft picker: %s", date_value)


def set_time(driver, time_xpath, time_value, timeout=15):
    """
    Set time using the custom dropdown with select_hour and select_minute.
    time_value format: HH:MM (e.g. "03:00")
    Clicks the time input to open the dropdown, then selects hour and minute.
    """
    import time as _time
    from selenium.webdriver.support.ui import Select

    # Parse time_value (HH:MM)
    h, m = time_value.split(":")
    hour_str = h.zfill(2)    # "03"
    minute_str = m.zfill(2)  # "00"

    wait = get_wait(driver, timeout)

    # Close any open date picker first by clicking elsewhere
    try:
        driver.find_element(By.TAG_NAME, "body").click()
        _time.sleep(0.3)
    except Exception:
        pass

    # Click the Start Time input to open the dropdown
    time_div = wait.until(EC.element_to_be_clickable((By.XPATH, time_xpath)))
    scroll_into_view(driver, time_div)
    try:
        time_input = time_div.find_element(By.TAG_NAME, "input")
        time_input.click()
    except Exception:
        time_div.click()
    _time.sleep(1)

    # Wait for the dropdown to appear
    dropdown = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "div.dropdown-menu.show")
    ))
    logging.info("Time dropdown opened")

    # Select hour from select_hour dropdown
    hour_select = dropdown.find_element(By.CSS_SELECTOR, "select.select_hour")
    Select(hour_select).select_by_value(hour_str)
    logging.info("Hour selected: %s", hour_str)
    _time.sleep(0.5)

    # Select minute (dropdown may close after hour selection, so re-open if needed)
    if minute_str != "00":
        # Need to select a non-default minute — re-open dropdown if closed
        try:
            dropdown = driver.find_element(By.CSS_SELECTOR, "div.dropdown-menu.show")
            minute_select = dropdown.find_element(By.CSS_SELECTOR, "select.select_minute")
            Select(minute_select).select_by_value(minute_str)
            logging.info("Minute selected: %s", minute_str)
        except (NoSuchElementException, StaleElementReferenceException):
            # Dropdown closed, re-open by clicking time input
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

    # Close dropdown by clicking elsewhere
    try:
        driver.find_element(By.TAG_NAME, "body").click()
        _time.sleep(0.3)
    except Exception:
        pass

    logging.info("Time selected: %s", time_value)


# High-level flows
def open_site(driver):
    """Open base URL and wait for page load (basic)."""
    logging.info("Opening site: %s", locators.URL)
    driver.get(locators.URL)


def ensure_airport_transfer_tab(driver):
    """Ensure the Airport Transfer tab is active; click if present and not active."""
    wait = get_wait(driver)
    try:
        tab = wait.until(EC.presence_of_element_located((By.XPATH, locators.AIRPORT_TRANSFER_TAB_XPATH)))
        # if class indicates active we assume active; else click
        try:
            classes = tab.get_attribute("class") or ""
            if "active" not in classes.lower():
                logging.info("Activating Airport Transfer tab")
                safe_click(driver, By.XPATH, locators.AIRPORT_TRANSFER_TAB_XPATH)
            else:
                logging.info("Airport Transfer tab already active")
        except Exception:
            logging.info("Could not determine tab state, attempting click")
            safe_click(driver, By.XPATH, locators.AIRPORT_TRANSFER_TAB_XPATH)
    except TimeoutException:
        logging.info("Airport transfer tab locator not found; assuming page defaults to airport transfer")


def fill_airport_transfer_form(driver):
    """Fill the Airport Transfer form using testdata + locators."""
    # Drop To Airport: click dropdown and select option by visible text
    logging.info("Selecting Drop To Airport -> %s", testdata.DROP_TO_AIRPORT_VALUE)
    safe_click(driver, By.XPATH, locators.DROP_TO_AIRPORT_XPATH)

    # attempt to use provided option template if present
    option_template = locators.DROP_TO_AIRPORT_OPTION_XPATH_TEMPLATE
    if option_template and "PASTE_XPATH_HERE" not in option_template:
        option_xpath = option_template.format(testdata.DROP_TO_AIRPORT_VALUE)
        safe_click(driver, By.XPATH, option_xpath)
    else:
        # fallback: try a generic list item match by text
        generic_option = f"//li[normalize-space()='{testdata.DROP_TO_AIRPORT_VALUE}']"
        safe_click(driver, By.XPATH, generic_option)

    # Drop Airport/City: type and select first suggestion
    logging.info("Typing Drop Airport/City -> %s", testdata.DROP_AIRPORT_CITY_VALUE)
    type_and_select_first_option(
        driver,
        locators.DROP_AIRPORT_CITY_XPATH,
        testdata.DROP_AIRPORT_CITY_VALUE,
        first_option_xpath=locators.DROP_AIRPORT_CITY_FIRST_OPTION_XPATH,
    )

    # Pickup Date
    logging.info("Setting pickup date -> %s", testdata.PICKUP_DATE_VALUE)
    set_date(driver, locators.PICKUP_DATE_XPATH, testdata.PICKUP_DATE_VALUE)

    # Start Time
    logging.info("Setting start time -> %s", testdata.START_TIME_VALUE)
    set_time(driver, locators.START_TIME_XPATH, testdata.START_TIME_VALUE)


def click_search_ride(driver):
    logging.info("Clicking Search Your Ride")
    safe_click(driver, By.XPATH, locators.SEARCH_RIDE_BUTTON_XPATH)


def click_book_now(driver, timeout=15):
    """Click 'Book Now' for the car specified in testdata.BOOK_CAR_NAME."""
    import time as _time
    car_name = testdata.BOOK_CAR_NAME
    logging.info("Looking for car: %s", car_name)
    wait = get_wait(driver, timeout)

    # Try to find Book Now button next to the chosen car
    car_xpath = locators.BOOK_NOW_BUTTON_XPATH_TEMPLATE.format(car_name)
    try:
        book_btn = wait.until(EC.element_to_be_clickable((By.XPATH, car_xpath)))
        logging.info("Found '%s' - clicking Book Now", car_name)
    except TimeoutException:
        logging.warning("Car '%s' not found in results, clicking first available car", car_name)
        book_btn = wait.until(EC.element_to_be_clickable((By.XPATH, locators.BOOK_NOW_BUTTON_FALLBACK_XPATH)))

    scroll_into_view(driver, book_btn)
    book_btn.click()
    logging.info("Book Now clicked for '%s', waiting for next page to load", car_name)
    _time.sleep(3)


def fill_mobile_and_send_otp(driver, timeout=15):
    """Fill mobile number on Sign In with OTP page and click SEND OTP."""
    logging.info("Filling mobile number: %s", testdata.MOBILE_NUMBER)
    wait = get_wait(driver, timeout)

    # Wait for the mobile number input to appear
    mobile_input = wait.until(EC.element_to_be_clickable((By.XPATH, locators.MOBILE_NUMBER_INPUT_XPATH)))
    scroll_into_view(driver, mobile_input)
    mobile_input.clear()
    mobile_input.send_keys(testdata.MOBILE_NUMBER)
    logging.info("Mobile number entered: %s", testdata.MOBILE_NUMBER)

    # Click SEND OTP
    safe_click(driver, By.XPATH, locators.SEND_OTP_BUTTON_XPATH)
    logging.info("SEND OTP clicked")


def fill_otp_and_verify(driver, timeout=15):
    """Fill OTP from testdata and click VERIFY OTP."""
    import time as _time

    wait = get_wait(driver, timeout)

    # Wait for OTP input to be fully ready
    _time.sleep(2)
    otp_input = wait.until(EC.element_to_be_clickable((By.XPATH, locators.OTP_INPUT_XPATH)))
    logging.info("OTP input field visible.")

    # Click on OTP input first, then type
    scroll_into_view(driver, otp_input)
    otp_input.click()
    _time.sleep(0.5)

    # Fill OTP from testdata
    otp_value = testdata.OTP_VALUE
    logging.info("Entering OTP: %s", otp_value)
    otp_input.send_keys(otp_value)
    _time.sleep(1)

    # Verify OTP was actually typed
    filled_value = otp_input.get_attribute("value") or ""
    logging.info("OTP field value after typing: '%s'", filled_value)
    if len(filled_value) < 6:
        logging.warning("OTP not filled properly, retrying...")
        otp_input.clear()
        _time.sleep(0.5)
        otp_input.send_keys(otp_value)
        _time.sleep(1)

    # Click VERIFY OTP
    safe_click(driver, By.XPATH, locators.VERIFY_OTP_BUTTON_XPATH)
    logging.info("VERIFY OTP clicked")
    _time.sleep(3)


def fill_booking_form(driver, timeout=15):
    """Fill the booking form: last name, pickup location, pickup address."""
    import time as _time

    wait = get_wait(driver, timeout)

    # Fill Last Name
    logging.info("Filling Last Name: %s", testdata.LAST_NAME)
    last_name = wait.until(EC.element_to_be_clickable((By.XPATH, locators.LAST_NAME_XPATH)))
    scroll_into_view(driver, last_name)
    last_name.click()
    last_name.clear()
    last_name.send_keys(testdata.LAST_NAME)

    # Fill Pickup Location (Google Places autocomplete)
    logging.info("Filling Pickup Location: %s", testdata.PICKUP_LOCATION)
    pickup_loc = wait.until(EC.element_to_be_clickable((By.XPATH, locators.PICKUP_LOCATION_XPATH)))
    scroll_into_view(driver, pickup_loc)
    pickup_loc.click()
    pickup_loc.clear()
    pickup_loc.send_keys(testdata.PICKUP_LOCATION)
    _time.sleep(2)
    # Select first Google suggestion
    try:
        first_suggestion = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.pac-container div.pac-item:first-child")
        ))
        first_suggestion.click()
        logging.info("Pickup Location suggestion selected")
    except TimeoutException:
        # Fallback: press arrow down + enter
        pickup_loc.send_keys(Keys.ARROW_DOWN)
        pickup_loc.send_keys(Keys.ENTER)
        logging.info("Pickup Location selected via keyboard")
    _time.sleep(1)

    # Fill Pickup Address
    logging.info("Filling Pickup Address: %s", testdata.PICKUP_ADDRESS)
    pickup_addr = wait.until(EC.element_to_be_clickable((By.XPATH, locators.PICKUP_ADDRESS_XPATH)))
    scroll_into_view(driver, pickup_addr)
    pickup_addr.click()
    pickup_addr.clear()
    pickup_addr.send_keys(testdata.PICKUP_ADDRESS)
    _time.sleep(0.5)


def tick_tnc_and_pay(driver, timeout=15):
    """Tick the T&C checkbox and click the Pay button."""
    import time as _time

    wait = get_wait(driver, timeout)

    # Tick T&C checkbox
    logging.info("Ticking T&C checkbox")
    checkbox = wait.until(EC.presence_of_element_located((By.XPATH, locators.TNC_CHECKBOX_XPATH)))
    scroll_into_view(driver, checkbox)
    if not checkbox.is_selected():
        # Click via JS since checkbox may be hidden behind label
        driver.execute_script("arguments[0].click();", checkbox)
    logging.info("T&C checkbox ticked")
    _time.sleep(1)

    # Click Pay button
    logging.info("Clicking Pay button")
    safe_click(driver, By.XPATH, locators.PAY_BUTTON_XPATH)
    logging.info("Pay button clicked")
    _time.sleep(3)


def assert_results_loaded(driver, timeout=15):
    """Validate results loaded or gracefully handle 'no rides' message."""
    wait = get_wait(driver, timeout)
    logging.info("Waiting for results container or unique page element")
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
            # check for no rides message
            try:
                no_rides = driver.find_element(By.XPATH, locators.NO_RIDES_MESSAGE_XPATH)
                logging.info("No rides message displayed: %s", no_rides.text)
                return False
            except Exception:
                logging.error("Results did not load and no 'no rides' message found")
                raise
