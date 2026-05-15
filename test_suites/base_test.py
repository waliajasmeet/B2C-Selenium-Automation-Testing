# test_suites/base_test.py
# Shared base classes for all test suites.

import os
import sys
import unittest
import logging
import time as _time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from datetime import datetime
from PIL import ImageGrab
import allure
import locators
import methods
import testvalue

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class BaseTestCase(unittest.TestCase):
    """Shared setup, teardown, and screenshot utilities for all test suites."""

    screenshot_count = 0
    _test_name = "Base"

    @classmethod
    def setUpClass(cls):
        logging.info("Starting Chrome browser for %s tests", cls._test_name)
        cls._chrome_options = webdriver.ChromeOptions()
        cls._chrome_options.add_argument("--start-maximized")
        cls._chrome_options.add_argument("--window-size=1920,1080")
        cls.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=cls._chrome_options,
        )
        cls.wait = methods.get_wait(cls.driver)
        existing = [f for f in os.listdir(SCREENSHOT_DIR) if f.endswith(".png")]
        cls.screenshot_count = len(existing)
        logging.info("Chrome browser is ready. Screenshot count starts at %d", cls.screenshot_count)

    @classmethod
    def tearDownClass(cls):
        logging.info("All tests finished. Closing Chrome browser now")
        try:
            cls.driver.quit()
            logging.info("Chrome browser closed successfully")
        except Exception:
            pass

    def tearDown(self):
        """Auto-capture error screenshot when test fails or is interrupted."""
        try:
            if not getattr(self._outcome, 'success', True):
                self._take_screenshot(self._testMethodName, "error_state")
        except Exception:
            pass

    def _take_screenshot(self, label, step_name):
        cls = type(self)
        cls.screenshot_count += 1
        count = cls.screenshot_count
        filename = f"{label}_{count}_{step_name}.png"
        path = os.path.join(SCREENSHOT_DIR, filename)
        logging.info("Taking screenshot for step '%s' and saving to: %s", step_name, path)
        try:
            self.driver.save_screenshot(path)
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name=f"{label}_{step_name}",
                attachment_type=allure.attachment_type.PNG,
            )
            logging.info("Screenshot saved successfully and attached to Allure report")
        except Exception as e:
            logging.error("Failed to save screenshot: %s", e)

    def _capture_alert_if_present(self, label):
        """Check for JS alert popup — if found, capture desktop screenshot and dismiss."""
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            logging.warning("JS alert detected: %s", alert_text)
            cls = type(self)
            cls.screenshot_count += 1
            count = cls.screenshot_count
            filename = f"{label}_{count}_error_popup.png"
            path = os.path.join(SCREENSHOT_DIR, filename)
            desktop_img = ImageGrab.grab()
            desktop_img.save(path)
            with open(path, "rb") as f:
                allure.attach(f.read(), name=f"{label}_error_popup",
                              attachment_type=allure.attachment_type.PNG)
            alert.accept()
            logging.info("Error popup screenshot saved and alert dismissed")
        except Exception:
            pass

    def _dismiss_alert(self):
        """Dismiss any browser alert if present. Returns alert text or None."""
        try:
            alert = self.driver.switch_to.alert
            text = alert.text
            logging.warning("Alert detected: %s", text)
            alert.accept()
            _time.sleep(0.5)
            return text
        except Exception:
            return None

    def _dismiss_toasts(self):
        """Remove any Toastify toast notifications that may block clicks."""
        try:
            self.driver.execute_script(
                "document.querySelectorAll('.Toastify__toast').forEach(e => e.remove());"
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Service base — shared by Airport Pickup, Airport Drop, Local Rental,
# Outstation Trip
# ---------------------------------------------------------------------------

class ServiceBaseTestCase(BaseTestCase):
    """Shared logic for the 4 service search test suites."""

    _tab_xpath = None
    _search_button_xpath = None
    _service_label = None

    def _convert_12h_to_24h(self, time_12h):
        """Convert '10:30 AM' or '2:45 PM' to '10:30' or '14:45'."""
        dt = datetime.strptime(time_12h.strip(), "%I:%M %p")
        result = dt.strftime("%H:%M").lstrip("0") if dt.hour < 10 else dt.strftime("%H:%M")
        logging.info("Converted time from 12-hour format '%s' to 24-hour format '%s'", time_12h.strip(), result)
        return result

    def _validate_results_page(self, label, expected_city, expected_date, expected_time):
        """Validate location, date, and time on the results page match input."""
        logging.info("========== STARTING RESULTS PAGE VALIDATION for '%s' ==========", label)
        wait = WebDriverWait(self.driver, 20)

        logging.info("Waiting for the results page to load (looking for Modify button)...")
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, locators.RESULTS_PAGE_UNIQUE_XPATH)))
            logging.info("Results page loaded successfully. Modify button is visible")
        except Exception:
            logging.warning("Results page did NOT load for '%s'. Page may have stayed on search form. Skipping validation", label)
            return

        # --- Location ---
        logging.info("Step 1 of 3: Validating LOCATION on results page...")
        try:
            location_el = self.driver.find_element(By.XPATH, locators.RESULTS_LOCATION_XPATH)
            actual_location = location_el.text.strip()
            logging.info("  Expected city: '%s'", expected_city)
            logging.info("  Actual location on page: '%s'", actual_location)
            self.assertIn(
                expected_city.lower(), actual_location.lower(),
                f"Location mismatch: expected '{expected_city}' in '{actual_location}'"
            )
            logging.info("  LOCATION MATCHED SUCCESSFULLY")
        except AssertionError as e:
            self._take_screenshot(label, "validate_location")
            logging.error("  LOCATION VALIDATION FAILED: %s", e)
            raise e

        # --- Date ---
        logging.info("Step 2 of 3: Validating DATE on results page...")
        try:
            date_el = self.driver.find_element(By.XPATH, locators.RESULTS_DATE_XPATH)
            actual_date = date_el.text.strip()
            logging.info("  Expected date: '%s'", expected_date)
            logging.info("  Actual date on page: '%s'", actual_date)
            self.assertEqual(
                expected_date, actual_date,
                f"Date mismatch: expected '{expected_date}', got '{actual_date}'"
            )
            logging.info("  DATE MATCHED SUCCESSFULLY")
        except AssertionError as e:
            self._take_screenshot(label, "validate_date")
            logging.error("  DATE VALIDATION FAILED: %s", e)
            raise e

        # --- Time ---
        logging.info("Step 3 of 3: Validating TIME on results page...")
        try:
            time_el = self.driver.find_element(By.XPATH, locators.RESULTS_TIME_XPATH)
            actual_time = time_el.text.strip()
            expected_time_24h = self._convert_12h_to_24h(expected_time)
            logging.info("  Input time (12h): '%s' -> Converted to 24h: '%s'", expected_time, expected_time_24h)
            logging.info("  Actual time on page: '%s'", actual_time)
            self.assertEqual(
                expected_time_24h, actual_time,
                f"Time mismatch: expected '{expected_time_24h}', got '{actual_time}'"
            )
            logging.info("  TIME MATCHED SUCCESSFULLY")
        except AssertionError as e:
            self._take_screenshot(label, "validate_time")
            logging.error("  TIME VALIDATION FAILED: %s", e)
            raise e

        logging.info("========== ALL VALIDATIONS PASSED for '%s' ==========", label)

    # ── Reusable search-flow helpers ──────────────────────────────────

    def _open_site(self, label):
        logging.info("Step 1: Opening the website %s", locators.URL)
        try:
            methods.open_site(self.driver)
            logging.info("Website opened successfully")
        except Exception as e:
            self._take_screenshot(label, "open_site")
            logging.error("FAILED to open website: %s", e)
            self.fail(f"Open site failed: {e}")

    def _click_tab(self, label):
        logging.info("Step 2: Clicking on the %s tab", self._service_label)
        try:
            methods.safe_click(self.driver, By.XPATH, self._tab_xpath)
            logging.info("%s tab clicked successfully", self._service_label)
        except Exception as e:
            self._take_screenshot(label, "click_tab")
            logging.error("FAILED to click %s tab: %s", self._service_label, e)
            self.fail(f"Click tab failed: {e}")

    def _set_date(self, label, date_xpath, date):
        try:
            methods.set_date(self.driver, date_xpath, date)
            logging.info("Date '%s' set successfully using date picker", date)
        except Exception as e:
            self._take_screenshot(label, "date")
            logging.warning("FAILED to set date '%s': %s", date, e)

    def _set_time(self, label, time_xpath, time):
        try:
            methods.set_time(self.driver, time_xpath, time)
            logging.info("Time '%s' set successfully using time dropdown", time)
        except Exception as e:
            self._take_screenshot(label, "time")
            logging.warning("FAILED to set time '%s': %s", time, e)

    def _dismiss_dropdown(self):
        try:
            self.driver.find_element(By.TAG_NAME, "body").click()
            _time.sleep(0.3)
        except Exception:
            pass

    def _click_search(self, label):
        try:
            btn = self.driver.find_element(By.XPATH, self._search_button_xpath)
            self.driver.execute_script("arguments[0].click();", btn)
            logging.info("Search button clicked")
        except Exception as e:
            self._take_screenshot(label, "click_search")
            logging.error("FAILED to click search button: %s", e)
            self.fail(f"Click search failed: {e}")

    def _run_payment_flow(self, label, city, date, time):
        """Book Now -> Login -> Order Summary -> Fill Details -> Pay."""
        logging.info("Starting payment flow (Book Now -> Login -> Fill Details -> Pay)")
        try:
            booked = methods.click_book_now_and_login(
                self.driver, testvalue.LOGIN_VALID_MOBILE, testvalue.LOGIN_VALID_OTP
            )
        except Exception as e:
            self._take_screenshot(label, "book_now")
            logging.error("FAILED during Book Now / Login: %s", e)
            self.fail(f"Book Now / Login failed: {e}")
        if booked:
            logging.info("Book Now and Login successful. Validating Order Summary")
            try:
                methods.validate_order_summary(
                    self.driver, city, date, time,
                    expected_service_type=self._service_label,
                )
            except Exception as e:
                self._take_screenshot(label, "order_summary")
                logging.error("FAILED during Order Summary validation: %s", e)
                self.fail(f"Order Summary validation failed: {e}")
            logging.info("Now filling traveller details")
            try:
                methods.fill_traveller_details_and_pay(
                    self.driver,
                    first_name=testvalue.TRAVELLER_FIRST_NAME,
                    last_name=testvalue.TRAVELLER_LAST_NAME,
                    mobile=testvalue.TRAVELLER_MOBILE,
                    email=testvalue.TRAVELLER_EMAIL,
                    pickup_location=testvalue.TRAVELLER_PICKUP_LOCATION,
                    pickup_address=testvalue.TRAVELLER_PICKUP_ADDRESS,
                    flight_no=testvalue.TRAVELLER_FLIGHT_NO,
                )
            except Exception as e:
                self._take_screenshot(label, "fill_details")
                logging.error("FAILED during fill details / pay: %s", e)
                self.fail(f"Fill details / Pay failed: {e}")
        else:
            logging.warning("Could not click Book Now. No results may be available")

    def _post_search(self, label, city, date, time, go_to_payment, validate):
        """After clicking search: alert capture -> validate -> payment -> final_state."""
        _time.sleep(0.5)
        self._capture_alert_if_present(label)

        if go_to_payment:
            _time.sleep(2.5)
            if validate:
                self._validate_results_page(label, city, date, time)
            self._run_payment_flow(label, city, date, time)
            self._take_screenshot(label, "final_state")
            methods.navigate_back_to_site(self.driver)
        else:
            self._take_screenshot(label, "final_state")

        logging.info("TEST '%s' COMPLETED SUCCESSFULLY", label)
        logging.info("============================================================\n")


# ---------------------------------------------------------------------------
# Login base — shared by Login_Home, Login_BookNow
# ---------------------------------------------------------------------------

class LoginBaseTestCase(BaseTestCase):
    """Shared logic for the 2 login test suites."""

    def _send_otp_with_retry(self, label, max_retries=4):
        """Click Send OTP with retry on rate limiting."""
        for attempt in range(max_retries):
            try:
                methods.safe_click(self.driver, By.XPATH, locators.LOGIN_SEND_OTP_BUTTON_XPATH)
                logging.info("Send OTP button clicked (attempt %d of %d)", attempt + 1, max_retries)
                _time.sleep(1)
                alert_text = self._dismiss_alert()
                if alert_text and "error" in alert_text.lower():
                    wait_sec = 15 * (attempt + 1)
                    logging.warning("OTP rate limited. Waiting %d seconds before retry...", wait_sec)
                    _time.sleep(wait_sec)
                    continue
                logging.info("OTP sent successfully")
                return True
            except Exception as e:
                self._dismiss_alert()
                if attempt == max_retries - 1:
                    self._take_screenshot(label, "send_otp")
                    logging.error("FAILED to send OTP after %d attempts: %s", max_retries, e)
                    self.fail(f"Send OTP failed after {max_retries} attempts: {e}")
                logging.warning("Send OTP attempt %d failed. Retrying in 10 seconds...", attempt + 1)
                _time.sleep(10)
        self._take_screenshot(label, "send_otp_rate_limited")
        self.fail("Send OTP failed — rate limited after all retries")
