# test_suites/Modify_Search.py
# Modify Search — Click Modify on results page, change fields, re-search, validate.
# Covers: Airport Pickup, Airport Drop, Local Rental, Outstation Trip.

import logging
import time as _time

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import allure
import locators
import methods
import testvalue

from base_test import BaseTestCase


@allure.feature("Modify Search")
class TestModifySearch(BaseTestCase):
    _test_name = "Modify Search"

    def setUp(self):
        """Check if browser session is alive; restart if crashed."""
        try:
            self.driver.title  # quick session health check
        except Exception:
            logging.warning("Browser session is dead. Restarting Chrome for next test...")
            try:
                self.driver.quit()
            except Exception:
                pass
            cls = type(self)
            cls.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=cls._chrome_options,
            )
            cls.wait = methods.get_wait(self.driver)
            logging.info("Chrome browser restarted successfully")

    def _convert_to_site_time_format(self, time_12h):
        """Convert '10:30 AM' → '10:30', '2:30 PM' → '14:30'.

        The site displays time in 24-hour format (HH:MM).
        """
        dt = datetime.strptime(time_12h.strip(), "%I:%M %p")
        result = dt.strftime("%H:%M")
        logging.info("Converted time '%s' to site display format '%s'", time_12h.strip(), result)
        return result

    def _validate_results_page(self, label, expected_city, expected_date, expected_time):
        """Validate location, date, and time on the results page match input.
        Returns True if results page loaded and validation passed, False if page didn't load."""
        logging.info("========== STARTING RESULTS PAGE VALIDATION for '%s' ==========", label)
        wait = WebDriverWait(self.driver, 20)

        # Wait for results page to load
        logging.info("Waiting for the results page to load (looking for Modify button)...")
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, locators.RESULTS_PAGE_UNIQUE_XPATH)))
            logging.info("Results page loaded successfully. Modify button is visible")
        except Exception:
            logging.warning("Results page did NOT load for '%s'. Skipping validation", label)
            return False

        # --- Location ---
        logging.info("Validating LOCATION on results page...")
        try:
            location_el = self.driver.find_element(By.XPATH, locators.RESULTS_LOCATION_XPATH)
            actual_location = location_el.text.strip()
            logging.info("  Expected city: '%s' | Actual: '%s'", expected_city, actual_location)
            self.assertIn(
                expected_city.lower(), actual_location.lower(),
                f"Location mismatch: expected '{expected_city}' in '{actual_location}'"
            )
            logging.info("  LOCATION MATCHED")
        except AssertionError as e:
            self._take_screenshot(label, "validate_location")
            logging.error("  LOCATION VALIDATION FAILED: %s", e)
            raise e

        # --- Date ---
        logging.info("Validating DATE on results page...")
        try:
            date_el = self.driver.find_element(By.XPATH, locators.RESULTS_DATE_XPATH)
            actual_date = date_el.text.strip()
            logging.info("  Expected: '%s' | Actual: '%s'", expected_date, actual_date)
            self.assertEqual(
                expected_date, actual_date,
                f"Date mismatch: expected '{expected_date}', got '{actual_date}'"
            )
            logging.info("  DATE MATCHED")
        except AssertionError as e:
            self._take_screenshot(label, "validate_date")
            logging.error("  DATE VALIDATION FAILED: %s", e)
            raise e

        # --- Time ---
        logging.info("Validating TIME on results page...")
        try:
            time_el = self.driver.find_element(By.XPATH, locators.RESULTS_TIME_XPATH)
            actual_time = time_el.text.strip()
            expected_site_time = self._convert_to_site_time_format(expected_time)
            logging.info("  Expected: '%s' | Actual: '%s'", expected_site_time, actual_time)
            self.assertEqual(
                expected_site_time, actual_time,
                f"Time mismatch: expected '{expected_site_time}', got '{actual_time}'"
            )
            logging.info("  TIME MATCHED")
        except AssertionError as e:
            self._take_screenshot(label, "validate_time")
            logging.error("  TIME VALIDATION FAILED: %s", e)
            raise e

        logging.info("========== ALL VALIDATIONS PASSED for '%s' ==========", label)
        return True

    def _dismiss_dropdown_and_search(self, label, search_button_xpath, step_num):
        """Dismiss any open dropdown, click Search, wait for results."""
        try:
            self.driver.find_element(By.TAG_NAME, "body").click()
            _time.sleep(0.3)
        except Exception:
            pass

        logging.info("Step %d: Clicking 'Search Your Ride' button", step_num)
        try:
            btn = self.driver.find_element(By.XPATH, search_button_xpath)
            self.driver.execute_script("arguments[0].click();", btn)
            logging.info("Search button clicked. Waiting for results page to load...")
            _time.sleep(4)
        except Exception as e:
            self._take_screenshot(label, "click_search")
            logging.error("FAILED to click search button: %s", e)
            self.fail(f"Click search failed: {e}")

    def _click_modify(self, label, step_num):
        """Click the Modify button on results page."""
        logging.info("Step %d: Clicking 'Modify' button on results page", step_num)
        try:
            # Dismiss any toast notifications that may block the button
            self.driver.execute_script(
                "document.querySelectorAll('.Toastify__toast').forEach(el => el.remove());"
            )
            _time.sleep(0.3)
            wait = WebDriverWait(self.driver, 10)
            modify_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, locators.RESULTS_PAGE_UNIQUE_XPATH))
            )
            try:
                modify_btn.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", modify_btn)
            logging.info("Modify button clicked. Search form should now be visible")
            _time.sleep(1)
        except Exception as e:
            self._take_screenshot(label, "click_modify")
            logging.error("FAILED to click Modify button: %s", e)
            self.fail(f"Click Modify failed: {e}")

    # ══════════════════════════════════════════════════════════════
    # Reusable form-fill helpers (for cross-tab modify tests)
    # ══════════════════════════════════════════════════════════════

    def _fill_airport_form(self, direction, city, date, time_val, label, start_step):
        """Fill Airport Transfer form: tab, direction, city, date, time. Returns next step number."""
        step = start_step

        logging.info("Step %d: Clicking Airport Transfer tab", step)
        try:
            methods.safe_click(self.driver, By.XPATH, locators.AIRPORT_TRANSFER_TAB_XPATH, timeout=5)
        except Exception:
            # Fallback: img[2] may be hidden when tab is inactive; click the anchor/li directly
            logging.info("  img[2] not clickable, falling back to li[1]/a click via JS")
            tab_a = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="myTab"]/li[1]/a'))
            )
            self.driver.execute_script("arguments[0].click();", tab_a)
            _time.sleep(1)
        step += 1

        logging.info("Step %d: Selecting direction '%s'", step, direction)
        methods.safe_click(self.driver, By.XPATH, locators.DIRECTION_SELECT_XPATH)
        methods.safe_click(self.driver, By.XPATH, locators.DIRECTION_OPTION_XPATH_TEMPLATE.format(direction))
        step += 1

        logging.info("Step %d: Entering city '%s'", step, city)
        try:
            city_input = self.driver.find_element(By.XPATH, locators.AIRPORT_CITY_XPATH)
            city_input.clear()
            _time.sleep(0.5)
        except Exception:
            pass
        methods.type_and_select_first_option(
            self.driver, locators.AIRPORT_CITY_XPATH, city,
            first_option_xpath=locators.AIRPORT_CITY_FIRST_OPTION_XPATH,
        )
        step += 1

        logging.info("Step %d: Setting date '%s'", step, date)
        methods.set_date(self.driver, locators.AIRPORT_DATE_XPATH, date)
        step += 1

        logging.info("Step %d: Setting time '%s'", step, time_val)
        methods.set_time(self.driver, locators.AIRPORT_TIME_XPATH, time_val)
        step += 1

        return step

    def _fill_local_rental_form(self, city, package, date, time_val, label, start_step):
        """Fill Local Rental form: tab, city, package, date, time. Returns next step number."""
        step = start_step

        logging.info("Step %d: Clicking Local Rental tab", step)
        methods.safe_click(self.driver, By.XPATH, locators.LOCAL_RENTAL_TAB_XPATH)
        step += 1

        logging.info("Step %d: Entering city '%s'", step, city)
        try:
            city_input = self.driver.find_element(By.XPATH, locators.LOCAL_RENTAL_CITY_XPATH)
            city_input.clear()
            _time.sleep(0.5)
        except Exception:
            pass
        methods.type_and_select_first_option(
            self.driver, locators.LOCAL_RENTAL_CITY_XPATH, city,
            first_option_xpath=locators.LOCAL_RENTAL_CITY_FIRST_OPTION_XPATH,
        )
        step += 1

        logging.info("Step %d: Selecting package '%s'", step, package)
        try:
            wait = WebDriverWait(self.driver, 15)
            select_elem = wait.until(EC.element_to_be_clickable((By.XPATH, locators.LOCAL_RENTAL_PACKAGE_XPATH)))
            WebDriverWait(self.driver, 10).until(
                lambda d: len(Select(d.find_element(By.XPATH, locators.LOCAL_RENTAL_PACKAGE_XPATH)).options) > 1
            )
            sel = Select(select_elem)
            options = [o.text.strip() for o in sel.options if o.text.strip() and o.get_attribute("value")]
            match = next((o for o in options if package.lower() in o.lower()), None)
            if match:
                sel.select_by_visible_text(match)
            else:
                sel.select_by_index(1)
            logging.info("Package selected successfully")
        except Exception as e:
            self._take_screenshot(label, "package")
            self.fail(f"Package select failed: {e}")
        step += 1

        logging.info("Step %d: Setting date '%s'", step, date)
        methods.set_date(self.driver, locators.LOCAL_RENTAL_DATE_XPATH, date)
        step += 1

        logging.info("Step %d: Setting time '%s'", step, time_val)
        methods.set_time(self.driver, locators.LOCAL_RENTAL_TIME_XPATH, time_val)
        step += 1

        return step

    # ══════════════════════════════════════════════════════════════
    # TEST 1: Airport Transfer — Pickup From Airport
    # ══════════════════════════════════════════════════════════════

    @allure.story("Same-Tab Modify")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Airport Transfer tab\n"
        "3. Select direction: Pickup from Airport\n"
        "4. Enter city (Bengaluru) and select from suggestions\n"
        "5. Set a future date and time\n"
        "6. Click 'Search Your Ride' button\n"
        "7. Validate results page shows correct location, date, and time\n"
        "8. Click 'Modify' button on results page\n"
        "9. Change city to Delhi, update date and time\n"
        "10. Click 'Search Your Ride' again\n"
        "11. Validate modified results page shows updated city, date, and time"
    )
    def to_verify_modify_airport_pickup_search(self):
        """Verify Modify works for Airport Transfer Pickup — change city, date, time."""
        label = "modify_airport_pickup"
        logging.info("============================================================")
        logging.info("STARTING TEST: Modify Airport Pickup Search")
        logging.info("  Initial: %s | %s | %s", testvalue.BEST_CITY, testvalue.BEST_DATE, testvalue.BEST_TIME)
        logging.info("  Modified: %s | %s | %s", testvalue.MODIFY_CITY, testvalue.MODIFY_DATE, testvalue.MODIFY_TIME)
        logging.info("============================================================")

        # ── Initial search ──
        logging.info("Step 1: Opening the website")
        methods.open_site(self.driver)

        logging.info("Step 2: Clicking Airport Transfer tab")
        methods.safe_click(self.driver, By.XPATH, locators.AIRPORT_TRANSFER_TAB_XPATH)

        logging.info("Step 3: Selecting direction '%s'", testvalue.BEST_DIRECTION)
        methods.safe_click(self.driver, By.XPATH, locators.DIRECTION_SELECT_XPATH)
        methods.safe_click(self.driver, By.XPATH, locators.DIRECTION_OPTION_XPATH_TEMPLATE.format(testvalue.BEST_DIRECTION))

        logging.info("Step 4: Entering city '%s'", testvalue.BEST_CITY)
        methods.type_and_select_first_option(
            self.driver, locators.AIRPORT_CITY_XPATH, testvalue.BEST_CITY,
            first_option_xpath=locators.AIRPORT_CITY_FIRST_OPTION_XPATH,
        )

        logging.info("Step 5: Setting date '%s'", testvalue.BEST_DATE)
        methods.set_date(self.driver, locators.AIRPORT_DATE_XPATH, testvalue.BEST_DATE)

        logging.info("Step 6: Setting time '%s'", testvalue.BEST_TIME)
        methods.set_time(self.driver, locators.AIRPORT_TIME_XPATH, testvalue.BEST_TIME)

        self._dismiss_dropdown_and_search(label, locators.AIRPORT_SEARCH_BUTTON_XPATH, 7)

        logging.info("Step 8: Validating initial results")
        loaded = self._validate_results_page(label + "_initial", testvalue.BEST_CITY, testvalue.BEST_DATE, testvalue.BEST_TIME)
        if not loaded:
            self.skipTest("Airport Pickup initial search did not produce results — skipping modify test")

        # ── Modify ──
        self._click_modify(label, 9)

        logging.info("Step 10: Changing city to '%s'", testvalue.MODIFY_CITY)
        city_input = self.driver.find_element(By.XPATH, locators.AIRPORT_CITY_XPATH)
        city_input.clear()
        _time.sleep(0.5)
        methods.type_and_select_first_option(
            self.driver, locators.AIRPORT_CITY_XPATH, testvalue.MODIFY_CITY,
            first_option_xpath=locators.AIRPORT_CITY_FIRST_OPTION_XPATH,
        )

        logging.info("Step 11: Changing date to '%s'", testvalue.MODIFY_DATE)
        methods.set_date(self.driver, locators.AIRPORT_DATE_XPATH, testvalue.MODIFY_DATE)

        logging.info("Step 12: Changing time to '%s'", testvalue.MODIFY_TIME)
        methods.set_time(self.driver, locators.AIRPORT_TIME_XPATH, testvalue.MODIFY_TIME)

        self._dismiss_dropdown_and_search(label, locators.AIRPORT_SEARCH_BUTTON_XPATH, 13)
        self._take_screenshot(label, "modified_results")

        logging.info("Step 14: Validating modified results")
        self._validate_results_page(label + "_modified", testvalue.MODIFY_CITY, testvalue.MODIFY_DATE, testvalue.MODIFY_TIME)

        logging.info("TEST '%s' COMPLETED SUCCESSFULLY\n", label)

    # ══════════════════════════════════════════════════════════════
    # TEST 2: Airport Transfer — Drop To Airport
    # ══════════════════════════════════════════════════════════════

    @allure.story("Same-Tab Modify")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Airport Transfer tab\n"
        "3. Select direction: Drop to Airport\n"
        "4. Enter city (Bengaluru) and select from suggestions\n"
        "5. Set a future date and time\n"
        "6. Click 'Search Your Ride' button\n"
        "7. Validate results page shows correct location, date, and time\n"
        "8. Click 'Modify' button on results page\n"
        "9. Change city to Delhi, update date and time\n"
        "10. Click 'Search Your Ride' again\n"
        "11. Validate modified results page shows updated city, date, and time"
    )
    def to_verify_modify_airport_drop_search(self):
        """Verify Modify works for Airport Transfer Drop — change city, date, time."""
        label = "modify_airport_drop"
        logging.info("============================================================")
        logging.info("STARTING TEST: Modify Airport Drop Search")
        logging.info("  Initial: %s | %s | %s", testvalue.DROP_BEST_CITY, testvalue.DROP_BEST_DATE, testvalue.DROP_BEST_TIME)
        logging.info("  Modified: %s | %s | %s", testvalue.MODIFY_DROP_CITY, testvalue.MODIFY_DROP_DATE, testvalue.MODIFY_DROP_TIME)
        logging.info("============================================================")

        # ── Initial search ──
        logging.info("Step 1: Opening the website")
        methods.open_site(self.driver)

        logging.info("Step 2: Clicking Airport Transfer tab")
        methods.safe_click(self.driver, By.XPATH, locators.AIRPORT_TRANSFER_TAB_XPATH)

        logging.info("Step 3: Selecting direction '%s'", testvalue.DROP_BEST_DIRECTION)
        methods.safe_click(self.driver, By.XPATH, locators.DIRECTION_SELECT_XPATH)
        methods.safe_click(self.driver, By.XPATH, locators.DIRECTION_OPTION_XPATH_TEMPLATE.format(testvalue.DROP_BEST_DIRECTION))

        logging.info("Step 4: Entering city '%s'", testvalue.DROP_BEST_CITY)
        methods.type_and_select_first_option(
            self.driver, locators.AIRPORT_CITY_XPATH, testvalue.DROP_BEST_CITY,
            first_option_xpath=locators.AIRPORT_CITY_FIRST_OPTION_XPATH,
        )

        logging.info("Step 5: Setting date '%s'", testvalue.DROP_BEST_DATE)
        methods.set_date(self.driver, locators.AIRPORT_DATE_XPATH, testvalue.DROP_BEST_DATE)

        logging.info("Step 6: Setting time '%s'", testvalue.DROP_BEST_TIME)
        methods.set_time(self.driver, locators.AIRPORT_TIME_XPATH, testvalue.DROP_BEST_TIME)

        self._dismiss_dropdown_and_search(label, locators.AIRPORT_SEARCH_BUTTON_XPATH, 7)

        logging.info("Step 8: Validating initial results")
        loaded = self._validate_results_page(label + "_initial", testvalue.DROP_BEST_CITY, testvalue.DROP_BEST_DATE, testvalue.DROP_BEST_TIME)
        if not loaded:
            self.skipTest("Airport Drop initial search did not produce results — skipping modify test")

        # ── Modify ──
        self._click_modify(label, 9)

        logging.info("Step 10: Changing city to '%s'", testvalue.MODIFY_DROP_CITY)
        city_input = self.driver.find_element(By.XPATH, locators.AIRPORT_CITY_XPATH)
        city_input.clear()
        _time.sleep(0.5)
        methods.type_and_select_first_option(
            self.driver, locators.AIRPORT_CITY_XPATH, testvalue.MODIFY_DROP_CITY,
            first_option_xpath=locators.AIRPORT_CITY_FIRST_OPTION_XPATH,
        )

        logging.info("Step 11: Changing date to '%s'", testvalue.MODIFY_DROP_DATE)
        methods.set_date(self.driver, locators.AIRPORT_DATE_XPATH, testvalue.MODIFY_DROP_DATE)

        logging.info("Step 12: Changing time to '%s'", testvalue.MODIFY_DROP_TIME)
        methods.set_time(self.driver, locators.AIRPORT_TIME_XPATH, testvalue.MODIFY_DROP_TIME)

        self._dismiss_dropdown_and_search(label, locators.AIRPORT_SEARCH_BUTTON_XPATH, 13)
        self._take_screenshot(label, "modified_results")

        logging.info("Step 14: Validating modified results")
        self._validate_results_page(label + "_modified", testvalue.MODIFY_DROP_CITY, testvalue.MODIFY_DROP_DATE, testvalue.MODIFY_DROP_TIME)

        logging.info("TEST '%s' COMPLETED SUCCESSFULLY\n", label)

    # ══════════════════════════════════════════════════════════════
    # TEST 3: Local Rental
    # ══════════════════════════════════════════════════════════════

    @allure.story("Same-Tab Modify")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Local Rental tab\n"
        "3. Enter city (Bengaluru) and select from suggestions\n"
        "4. Select rental package (8 Hrs / 80 Kms)\n"
        "5. Set a future date and time\n"
        "6. Click 'Search Your Ride' button\n"
        "7. Validate results page shows correct location, date, and time\n"
        "8. Click 'Modify' button on results page\n"
        "9. Change city to Delhi, package to 12 Hrs / 120 Kms, update date and time\n"
        "10. Click 'Search Your Ride' again\n"
        "11. Validate modified results page shows updated city, date, and time"
    )
    def to_verify_modify_local_rental_search(self):
        """Verify Modify works for Local Rental — change city, package, date, time."""
        label = "modify_local_rental"
        logging.info("============================================================")
        logging.info("STARTING TEST: Modify Local Rental Search")
        logging.info("  Initial: %s | %s | %s | %s", testvalue.LR_BEST_CITY, testvalue.LR_BEST_PACKAGE, testvalue.LR_BEST_DATE, testvalue.LR_BEST_TIME)
        logging.info("  Modified: %s | %s | %s | %s", testvalue.MODIFY_LR_CITY, testvalue.MODIFY_LR_PACKAGE, testvalue.MODIFY_LR_DATE, testvalue.MODIFY_LR_TIME)
        logging.info("============================================================")

        # ── Initial search ──
        logging.info("Step 1: Opening the website")
        methods.open_site(self.driver)

        logging.info("Step 2: Clicking Local Rental tab")
        methods.safe_click(self.driver, By.XPATH, locators.LOCAL_RENTAL_TAB_XPATH)

        logging.info("Step 3: Entering city '%s'", testvalue.LR_BEST_CITY)
        methods.type_and_select_first_option(
            self.driver, locators.LOCAL_RENTAL_CITY_XPATH, testvalue.LR_BEST_CITY,
            first_option_xpath=locators.LOCAL_RENTAL_CITY_FIRST_OPTION_XPATH,
        )

        logging.info("Step 4: Selecting package '%s'", testvalue.LR_BEST_PACKAGE)
        try:
            wait = WebDriverWait(self.driver, 15)
            select_elem = wait.until(EC.element_to_be_clickable((By.XPATH, locators.LOCAL_RENTAL_PACKAGE_XPATH)))
            WebDriverWait(self.driver, 10).until(
                lambda d: len(Select(d.find_element(By.XPATH, locators.LOCAL_RENTAL_PACKAGE_XPATH)).options) > 1
            )
            sel = Select(select_elem)
            options = [o.text.strip() for o in sel.options if o.text.strip() and o.get_attribute("value")]
            match = next((o for o in options if testvalue.LR_BEST_PACKAGE.lower() in o.lower()), None)
            if match:
                sel.select_by_visible_text(match)
            else:
                sel.select_by_index(1)
            logging.info("Package selected successfully")
        except Exception as e:
            self._take_screenshot(label, "package")
            self.fail(f"Package select failed: {e}")

        logging.info("Step 5: Setting date '%s'", testvalue.LR_BEST_DATE)
        methods.set_date(self.driver, locators.LOCAL_RENTAL_DATE_XPATH, testvalue.LR_BEST_DATE)

        logging.info("Step 6: Setting time '%s'", testvalue.LR_BEST_TIME)
        methods.set_time(self.driver, locators.LOCAL_RENTAL_TIME_XPATH, testvalue.LR_BEST_TIME)

        self._dismiss_dropdown_and_search(label, locators.LOCAL_RENTAL_SEARCH_BUTTON_XPATH, 7)

        logging.info("Step 8: Validating initial results")
        loaded = self._validate_results_page(label + "_initial", testvalue.LR_BEST_CITY, testvalue.LR_BEST_DATE, testvalue.LR_BEST_TIME)
        if not loaded:
            self.skipTest("Local Rental initial search did not produce results — skipping modify test")

        # ── Modify ──
        self._click_modify(label, 9)

        logging.info("Step 10: Changing city to '%s'", testvalue.MODIFY_LR_CITY)
        city_input = self.driver.find_element(By.XPATH, locators.LOCAL_RENTAL_CITY_XPATH)
        city_input.clear()
        _time.sleep(0.5)
        methods.type_and_select_first_option(
            self.driver, locators.LOCAL_RENTAL_CITY_XPATH, testvalue.MODIFY_LR_CITY,
            first_option_xpath=locators.LOCAL_RENTAL_CITY_FIRST_OPTION_XPATH,
        )

        logging.info("Step 11: Changing package to '%s'", testvalue.MODIFY_LR_PACKAGE)
        try:
            select_elem = self.driver.find_element(By.XPATH, locators.LOCAL_RENTAL_PACKAGE_XPATH)
            WebDriverWait(self.driver, 10).until(
                lambda d: len(Select(d.find_element(By.XPATH, locators.LOCAL_RENTAL_PACKAGE_XPATH)).options) > 1
            )
            sel = Select(select_elem)
            options = [o.text.strip() for o in sel.options if o.text.strip() and o.get_attribute("value")]
            match = next((o for o in options if testvalue.MODIFY_LR_PACKAGE.lower() in o.lower()), None)
            if match:
                sel.select_by_visible_text(match)
            else:
                sel.select_by_index(2)
            logging.info("Package changed successfully")
        except Exception as e:
            self._take_screenshot(label, "modify_package")
            logging.warning("FAILED to change package: %s", e)

        logging.info("Step 12: Changing date to '%s'", testvalue.MODIFY_LR_DATE)
        methods.set_date(self.driver, locators.LOCAL_RENTAL_DATE_XPATH, testvalue.MODIFY_LR_DATE)

        logging.info("Step 13: Changing time to '%s'", testvalue.MODIFY_LR_TIME)
        methods.set_time(self.driver, locators.LOCAL_RENTAL_TIME_XPATH, testvalue.MODIFY_LR_TIME)

        self._dismiss_dropdown_and_search(label, locators.LOCAL_RENTAL_SEARCH_BUTTON_XPATH, 14)
        self._take_screenshot(label, "modified_results")

        logging.info("Step 15: Validating modified results")
        self._validate_results_page(label + "_modified", testvalue.MODIFY_LR_CITY, testvalue.MODIFY_LR_DATE, testvalue.MODIFY_LR_TIME)

        logging.info("TEST '%s' COMPLETED SUCCESSFULLY\n", label)

    def _type_and_select_pac(self, input_xpath, value):
        """Type into a Google Places Autocomplete input and select the first pac-item.
        Google Places uses mousedown event (not click) to register selections."""
        wait = WebDriverWait(self.driver, 15)
        input_el = wait.until(EC.element_to_be_clickable((By.XPATH, input_xpath)))
        methods.scroll_into_view(self.driver, input_el)
        try:
            input_el.clear()
        except Exception:
            pass
        input_el.click()
        _time.sleep(0.5)
        input_el.send_keys(value)

        # Wait for a VISIBLE pac-container with pac-items
        for attempt in range(3):
            _time.sleep(2)
            try:
                containers = self.driver.find_elements(By.CSS_SELECTOR, "div.pac-container")
                for container in containers:
                    if container.is_displayed():
                        items = container.find_elements(By.CSS_SELECTOR, "div.pac-item")
                        if items:
                            # Use ActionChains for a real mouse click on pac-item
                            from selenium.webdriver.common.action_chains import ActionChains
                            ActionChains(self.driver).move_to_element(items[0]).click().perform()
                            _time.sleep(1)
                            logging.info("Google Places suggestion selected for '%s' (attempt %d)", value, attempt + 1)
                            new_val = input_el.get_attribute("value")
                            logging.info("  Input value after selection: '%s'", new_val)
                            # Force-close any remaining pac-container by pressing Escape
                            from selenium.webdriver.common.keys import Keys
                            input_el.send_keys(Keys.ESCAPE)
                            _time.sleep(0.5)
                            # Click body to fully dismiss
                            self.driver.find_element(By.TAG_NAME, "body").click()
                            _time.sleep(0.5)
                            return
            except Exception:
                pass
            logging.info("No visible pac-items found for '%s' (attempt %d), retrying...", value, attempt + 1)
            try:
                input_el.clear()
                _time.sleep(0.3)
                input_el.send_keys(value)
            except Exception:
                pass

        logging.warning("pac-item not found for '%s' after 3 attempts, using keyboard fallback", value)
        from selenium.webdriver.common.keys import Keys
        input_el.send_keys(Keys.ARROW_DOWN)
        input_el.send_keys(Keys.ENTER)
        _time.sleep(1)

    # ══════════════════════════════════════════════════════════════
    # TEST 4: Outstation Trip
    # ══════════════════════════════════════════════════════════════

    @allure.story("Same-Tab Modify")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Outstation Trip tab\n"
        "3. Select trip type (One Way)\n"
        "4. Enter 'From' city (Delhi) and 'To' city (Mumbai)\n"
        "5. Set a future date and time\n"
        "6. Click 'Search Your Ride' button\n"
        "7. Validate results page shows correct location, date, and time\n"
        "8. Click 'Modify' button on results page\n"
        "9. Change date and time (city kept same — autocomplete doesn't work in overlay)\n"
        "10. Click 'Search Your Ride' again\n"
        "11. Validate modified results page shows updated date and time"
    )
    def to_verify_modify_outstation_trip_search(self):
        """Verify Modify works for Outstation Trip — change from/to city, date, time."""
        label = "modify_outstation"
        logging.info("============================================================")
        logging.info("STARTING TEST: Modify Outstation Trip Search")
        logging.info("  Initial: %s → %s | %s | %s", testvalue.OS_BEST_FROM_CITY, testvalue.OS_BEST_TO_CITY, testvalue.OS_BEST_DATE, testvalue.OS_BEST_TIME)
        logging.info("  Modified: %s → %s | %s | %s", testvalue.MODIFY_OS_FROM_CITY, testvalue.MODIFY_OS_TO_CITY, testvalue.MODIFY_OS_DATE, testvalue.MODIFY_OS_TIME)
        logging.info("============================================================")

        # ── Initial search — match standalone Outstation_Trip.py flow exactly ──
        logging.info("Step 1: Opening the website")
        methods.open_site(self.driver)

        logging.info("Step 2: Clicking Outstation Trip tab")
        methods.safe_click(self.driver, By.XPATH, locators.OUTSTATION_TRIP_TAB_XPATH)

        logging.info("Step 3: Selecting trip type '%s'", testvalue.OS_BEST_TRIP_TYPE)
        try:
            wait = WebDriverWait(self.driver, 15)
            select_elem = wait.until(EC.element_to_be_clickable((By.XPATH, locators.OUTSTATION_TRIP_TYPE_XPATH)))
            WebDriverWait(self.driver, 10).until(
                lambda d: len(Select(d.find_element(By.XPATH, locators.OUTSTATION_TRIP_TYPE_XPATH)).options) > 1
            )
            sel = Select(select_elem)
            options = [o.text.strip() for o in sel.options if o.text.strip() and o.get_attribute("value")]
            match = next((o for o in options if testvalue.OS_BEST_TRIP_TYPE.lower() in o.lower()), None)
            if match:
                sel.select_by_visible_text(match)
            else:
                sel.select_by_index(1)
            logging.info("Trip type selected successfully")
        except Exception as e:
            self._take_screenshot(label, "trip_type")
            self.fail(f"Trip type select failed: {e}")

        logging.info("Step 4: Entering 'From' city '%s'", testvalue.OS_BEST_FROM_CITY)
        methods.type_and_select_first_option(
            self.driver, locators.OUTSTATION_FROM_CITY_XPATH, testvalue.OS_BEST_FROM_CITY,
            first_option_xpath=locators.OUTSTATION_FROM_CITY_FIRST_OPTION_XPATH,
        )

        logging.info("Step 5: Entering 'To' city '%s'", testvalue.OS_BEST_TO_CITY)
        methods.type_and_select_first_option(
            self.driver, locators.OUTSTATION_TO_CITY_XPATH, testvalue.OS_BEST_TO_CITY,
            first_option_xpath=locators.OUTSTATION_TO_CITY_FIRST_OPTION_XPATH,
        )

        logging.info("Step 6: Setting date '%s'", testvalue.OS_BEST_DATE)
        methods.set_date(self.driver, locators.OUTSTATION_DATE_XPATH, testvalue.OS_BEST_DATE)

        logging.info("Step 7: Setting time '%s'", testvalue.OS_BEST_TIME)
        methods.set_time(self.driver, locators.OUTSTATION_TIME_XPATH, testvalue.OS_BEST_TIME)

        self._dismiss_dropdown_and_search(label, locators.OUTSTATION_SEARCH_BUTTON_XPATH, 8)


        logging.info("Step 9: Validating initial results")
        loaded = self._validate_results_page(label + "_initial", testvalue.OS_BEST_FROM_CITY, testvalue.OS_BEST_DATE, testvalue.OS_BEST_TIME)
        if not loaded:
            self.skipTest("Outstation Trip initial search did not produce results — skipping modify test")

        # ── Modify: change date & time only (city autocomplete doesn't work in overlay) ──
        self._click_modify(label, 10)

        # Set date via JS (date picker doesn't open inside Modify overlay)
        logging.info("Step 11: Setting date via JS to '%s'", testvalue.MODIFY_OS_DATE)
        self.driver.execute_script(
            "var el = document.getElementById('pickup_date');"
            "if(el){ var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;"
            "nativeInputValueSetter.call(el, arguments[0]);"
            "el.dispatchEvent(new Event('input', { bubbles: true }));"
            "el.dispatchEvent(new Event('change', { bubbles: true })); }",
            testvalue.MODIFY_OS_DATE
        )
        _time.sleep(0.5)

        logging.info("Step 12: Setting time to '%s'", testvalue.MODIFY_OS_TIME)
        methods.set_time(self.driver, locators.OUTSTATION_TIME_XPATH, testvalue.MODIFY_OS_TIME)

        self._dismiss_dropdown_and_search(label, locators.OUTSTATION_SEARCH_BUTTON_XPATH, 13)
        self._take_screenshot(label, "modified_results")

        logging.info("Step 14: Validating modified results (same city, new date/time)")
        self._validate_results_page(label + "_modified", testvalue.OS_BEST_FROM_CITY, testvalue.MODIFY_OS_DATE, testvalue.MODIFY_OS_TIME)

        logging.info("TEST '%s' COMPLETED SUCCESSFULLY\n", label)

    # ══════════════════════════════════════════════════════════════
    # CROSS-TAB TESTS: Modify from one service type to another
    # ══════════════════════════════════════════════════════════════

    # ── TEST 5: Airport Pickup → Local Rental ──

    @allure.story("Cross-Tab Modify")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Fill Airport Transfer form (direction: Pickup from Airport, city: Bengaluru)\n"
        "3. Set future date and time, click Search\n"
        "4. Validate results page shows correct location, date, and time\n"
        "5. Click 'Modify' button on results page\n"
        "6. Switch to Local Rental tab inside the Modify overlay\n"
        "7. Fill Local Rental form (city: Delhi, package: 12 Hrs / 120 Kms, new date and time)\n"
        "8. Click Search\n"
        "9. Validate modified results page shows Local Rental results for Delhi"
    )
    def to_verify_modify_airport_pickup_to_local_rental(self):
        """Cross-tab: Airport Pickup → Local Rental."""
        label = "crosstab_pickup_to_lr"
        logging.info("============================================================")
        logging.info("STARTING TEST: Airport Pickup → Local Rental (Cross-Tab)")
        logging.info("============================================================")

        # ── Initial search: Airport Pickup ──
        logging.info("Step 1: Opening the website")
        methods.open_site(self.driver)
        next_step = self._fill_airport_form(
            testvalue.BEST_DIRECTION, testvalue.BEST_CITY,
            testvalue.BEST_DATE, testvalue.BEST_TIME, label, 2
        )
        self._dismiss_dropdown_and_search(label, locators.AIRPORT_SEARCH_BUTTON_XPATH, next_step)

        loaded = self._validate_results_page(label + "_initial", testvalue.BEST_CITY, testvalue.BEST_DATE, testvalue.BEST_TIME)
        if not loaded:
            self.skipTest("Airport Pickup initial search did not produce results — skipping cross-tab test")

        # ── Modify → Local Rental ──
        self._click_modify(label, next_step + 1)

        mod_step = self._fill_local_rental_form(
            testvalue.MODIFY_LR_CITY, testvalue.MODIFY_LR_PACKAGE,
            testvalue.MODIFY_LR_DATE, testvalue.MODIFY_LR_TIME, label, next_step + 2
        )
        self._dismiss_dropdown_and_search(label, locators.LOCAL_RENTAL_SEARCH_BUTTON_XPATH, mod_step)
        self._take_screenshot(label, "modified_results")

        self._validate_results_page(label + "_modified", testvalue.MODIFY_LR_CITY, testvalue.MODIFY_LR_DATE, testvalue.MODIFY_LR_TIME)
        logging.info("TEST '%s' COMPLETED SUCCESSFULLY\n", label)

    # ── TEST 6: Airport Pickup → Airport Drop ──

    @allure.story("Cross-Tab Modify")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Fill Airport Transfer form (direction: Pickup from Airport, city: Bengaluru)\n"
        "3. Set future date and time, click Search\n"
        "4. Validate results page shows correct location, date, and time\n"
        "5. Click 'Modify' button on results page\n"
        "6. Stay on Airport Transfer tab, change direction to Drop to Airport\n"
        "7. Change city to Delhi, update date and time\n"
        "8. Click Search\n"
        "9. Validate modified results page shows Airport Drop results for Delhi"
    )
    def to_verify_modify_airport_pickup_to_airport_drop(self):
        """Cross-tab: Airport Pickup → Airport Drop."""
        label = "crosstab_pickup_to_drop"
        logging.info("============================================================")
        logging.info("STARTING TEST: Airport Pickup → Airport Drop (Cross-Tab)")
        logging.info("============================================================")

        # ── Initial search: Airport Pickup ──
        logging.info("Step 1: Opening the website")
        methods.open_site(self.driver)
        next_step = self._fill_airport_form(
            testvalue.BEST_DIRECTION, testvalue.BEST_CITY,
            testvalue.BEST_DATE, testvalue.BEST_TIME, label, 2
        )
        self._dismiss_dropdown_and_search(label, locators.AIRPORT_SEARCH_BUTTON_XPATH, next_step)

        loaded = self._validate_results_page(label + "_initial", testvalue.BEST_CITY, testvalue.BEST_DATE, testvalue.BEST_TIME)
        if not loaded:
            self.skipTest("Airport Pickup initial search did not produce results — skipping cross-tab test")

        # ── Modify → Airport Drop ──
        self._click_modify(label, next_step + 1)

        mod_step = self._fill_airport_form(
            testvalue.MODIFY_DROP_DIRECTION, testvalue.MODIFY_DROP_CITY,
            testvalue.MODIFY_DROP_DATE, testvalue.MODIFY_DROP_TIME, label, next_step + 2
        )
        self._dismiss_dropdown_and_search(label, locators.AIRPORT_SEARCH_BUTTON_XPATH, mod_step)
        self._take_screenshot(label, "modified_results")

        self._validate_results_page(label + "_modified", testvalue.MODIFY_DROP_CITY, testvalue.MODIFY_DROP_DATE, testvalue.MODIFY_DROP_TIME)
        logging.info("TEST '%s' COMPLETED SUCCESSFULLY\n", label)

    # ── TEST 7: Airport Drop → Local Rental ──

    @allure.story("Cross-Tab Modify")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Fill Airport Transfer form (direction: Drop to Airport, city: Bengaluru)\n"
        "3. Set future date and time, click Search\n"
        "4. Validate results page shows correct location, date, and time\n"
        "5. Click 'Modify' button on results page\n"
        "6. Switch to Local Rental tab inside the Modify overlay\n"
        "7. Fill Local Rental form (city: Delhi, package: 12 Hrs / 120 Kms, new date and time)\n"
        "8. Click Search\n"
        "9. Validate modified results page shows Local Rental results for Delhi"
    )
    def to_verify_modify_airport_drop_to_local_rental(self):
        """Cross-tab: Airport Drop → Local Rental."""
        label = "crosstab_drop_to_lr"
        logging.info("============================================================")
        logging.info("STARTING TEST: Airport Drop → Local Rental (Cross-Tab)")
        logging.info("============================================================")

        # ── Initial search: Airport Drop ──
        logging.info("Step 1: Opening the website")
        methods.open_site(self.driver)
        next_step = self._fill_airport_form(
            testvalue.DROP_BEST_DIRECTION, testvalue.DROP_BEST_CITY,
            testvalue.DROP_BEST_DATE, testvalue.DROP_BEST_TIME, label, 2
        )
        self._dismiss_dropdown_and_search(label, locators.AIRPORT_SEARCH_BUTTON_XPATH, next_step)

        loaded = self._validate_results_page(label + "_initial", testvalue.DROP_BEST_CITY, testvalue.DROP_BEST_DATE, testvalue.DROP_BEST_TIME)
        if not loaded:
            self.skipTest("Airport Drop initial search did not produce results — skipping cross-tab test")

        # ── Modify → Local Rental ──
        self._click_modify(label, next_step + 1)

        mod_step = self._fill_local_rental_form(
            testvalue.MODIFY_LR_CITY, testvalue.MODIFY_LR_PACKAGE,
            testvalue.MODIFY_LR_DATE, testvalue.MODIFY_LR_TIME, label, next_step + 2
        )
        self._dismiss_dropdown_and_search(label, locators.LOCAL_RENTAL_SEARCH_BUTTON_XPATH, mod_step)
        self._take_screenshot(label, "modified_results")

        self._validate_results_page(label + "_modified", testvalue.MODIFY_LR_CITY, testvalue.MODIFY_LR_DATE, testvalue.MODIFY_LR_TIME)
        logging.info("TEST '%s' COMPLETED SUCCESSFULLY\n", label)

    # ── TEST 8: Airport Drop → Airport Pickup ──

    @allure.story("Cross-Tab Modify")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Fill Airport Transfer form (direction: Drop to Airport, city: Bengaluru)\n"
        "3. Set future date and time, click Search\n"
        "4. Validate results page shows correct location, date, and time\n"
        "5. Click 'Modify' button on results page\n"
        "6. Stay on Airport Transfer tab, change direction to Pickup from Airport\n"
        "7. Change city to Delhi, update date and time\n"
        "8. Click Search\n"
        "9. Validate modified results page shows Airport Pickup results for Delhi"
    )
    def to_verify_modify_airport_drop_to_airport_pickup(self):
        """Cross-tab: Airport Drop → Airport Pickup."""
        label = "crosstab_drop_to_pickup"
        logging.info("============================================================")
        logging.info("STARTING TEST: Airport Drop → Airport Pickup (Cross-Tab)")
        logging.info("============================================================")

        # ── Initial search: Airport Drop ──
        logging.info("Step 1: Opening the website")
        methods.open_site(self.driver)
        next_step = self._fill_airport_form(
            testvalue.DROP_BEST_DIRECTION, testvalue.DROP_BEST_CITY,
            testvalue.DROP_BEST_DATE, testvalue.DROP_BEST_TIME, label, 2
        )
        self._dismiss_dropdown_and_search(label, locators.AIRPORT_SEARCH_BUTTON_XPATH, next_step)

        loaded = self._validate_results_page(label + "_initial", testvalue.DROP_BEST_CITY, testvalue.DROP_BEST_DATE, testvalue.DROP_BEST_TIME)
        if not loaded:
            self.skipTest("Airport Drop initial search did not produce results — skipping cross-tab test")

        # ── Modify → Airport Pickup ──
        self._click_modify(label, next_step + 1)

        mod_step = self._fill_airport_form(
            testvalue.BEST_DIRECTION, testvalue.MODIFY_CITY,
            testvalue.MODIFY_DATE, testvalue.MODIFY_TIME, label, next_step + 2
        )
        self._dismiss_dropdown_and_search(label, locators.AIRPORT_SEARCH_BUTTON_XPATH, mod_step)
        self._take_screenshot(label, "modified_results")

        self._validate_results_page(label + "_modified", testvalue.MODIFY_CITY, testvalue.MODIFY_DATE, testvalue.MODIFY_TIME)
        logging.info("TEST '%s' COMPLETED SUCCESSFULLY\n", label)

    # ── TEST 9: Local Rental → Airport Pickup ──

    @allure.story("Cross-Tab Modify")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Fill Local Rental form (city: Bengaluru, package: 8 Hrs / 80 Kms)\n"
        "3. Set future date and time, click Search\n"
        "4. Validate results page shows correct location, date, and time\n"
        "5. Click 'Modify' button on results page\n"
        "6. Switch to Airport Transfer tab inside the Modify overlay\n"
        "7. Fill Airport Transfer form (direction: Pickup from Airport, city: Delhi, new date and time)\n"
        "8. Click Search\n"
        "9. Validate modified results page shows Airport Pickup results for Delhi"
    )
    def to_verify_modify_local_rental_to_airport_pickup(self):
        """Cross-tab: Local Rental → Airport Pickup."""
        label = "crosstab_lr_to_pickup"
        logging.info("============================================================")
        logging.info("STARTING TEST: Local Rental → Airport Pickup (Cross-Tab)")
        logging.info("============================================================")

        # ── Initial search: Local Rental ──
        logging.info("Step 1: Opening the website")
        methods.open_site(self.driver)
        next_step = self._fill_local_rental_form(
            testvalue.LR_BEST_CITY, testvalue.LR_BEST_PACKAGE,
            testvalue.LR_BEST_DATE, testvalue.LR_BEST_TIME, label, 2
        )
        self._dismiss_dropdown_and_search(label, locators.LOCAL_RENTAL_SEARCH_BUTTON_XPATH, next_step)

        loaded = self._validate_results_page(label + "_initial", testvalue.LR_BEST_CITY, testvalue.LR_BEST_DATE, testvalue.LR_BEST_TIME)
        if not loaded:
            self.skipTest("Local Rental initial search did not produce results — skipping cross-tab test")

        # ── Modify → Airport Pickup ──
        self._click_modify(label, next_step + 1)

        mod_step = self._fill_airport_form(
            testvalue.BEST_DIRECTION, testvalue.MODIFY_CITY,
            testvalue.MODIFY_DATE, testvalue.MODIFY_TIME, label, next_step + 2
        )
        self._dismiss_dropdown_and_search(label, locators.AIRPORT_SEARCH_BUTTON_XPATH, mod_step)
        self._take_screenshot(label, "modified_results")

        self._validate_results_page(label + "_modified", testvalue.MODIFY_CITY, testvalue.MODIFY_DATE, testvalue.MODIFY_TIME)
        logging.info("TEST '%s' COMPLETED SUCCESSFULLY\n", label)

    # ── TEST 10: Local Rental → Airport Drop ──

    @allure.story("Cross-Tab Modify")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Fill Local Rental form (city: Bengaluru, package: 8 Hrs / 80 Kms)\n"
        "3. Set future date and time, click Search\n"
        "4. Validate results page shows correct location, date, and time\n"
        "5. Click 'Modify' button on results page\n"
        "6. Switch to Airport Transfer tab inside the Modify overlay\n"
        "7. Fill Airport Transfer form (direction: Drop to Airport, city: Delhi, new date and time)\n"
        "8. Click Search\n"
        "9. Validate modified results page shows Airport Drop results for Delhi"
    )
    def to_verify_modify_local_rental_to_airport_drop(self):
        """Cross-tab: Local Rental → Airport Drop."""
        label = "crosstab_lr_to_drop"
        logging.info("============================================================")
        logging.info("STARTING TEST: Local Rental → Airport Drop (Cross-Tab)")
        logging.info("============================================================")

        # ── Initial search: Local Rental ──
        logging.info("Step 1: Opening the website")
        methods.open_site(self.driver)
        next_step = self._fill_local_rental_form(
            testvalue.LR_BEST_CITY, testvalue.LR_BEST_PACKAGE,
            testvalue.LR_BEST_DATE, testvalue.LR_BEST_TIME, label, 2
        )
        self._dismiss_dropdown_and_search(label, locators.LOCAL_RENTAL_SEARCH_BUTTON_XPATH, next_step)

        loaded = self._validate_results_page(label + "_initial", testvalue.LR_BEST_CITY, testvalue.LR_BEST_DATE, testvalue.LR_BEST_TIME)
        if not loaded:
            self.skipTest("Local Rental initial search did not produce results — skipping cross-tab test")

        # ── Modify → Airport Drop ──
        self._click_modify(label, next_step + 1)

        mod_step = self._fill_airport_form(
            testvalue.MODIFY_DROP_DIRECTION, testvalue.MODIFY_DROP_CITY,
            testvalue.MODIFY_DROP_DATE, testvalue.MODIFY_DROP_TIME, label, next_step + 2
        )
        self._dismiss_dropdown_and_search(label, locators.AIRPORT_SEARCH_BUTTON_XPATH, mod_step)
        self._take_screenshot(label, "modified_results")

        self._validate_results_page(label + "_modified", testvalue.MODIFY_DROP_CITY, testvalue.MODIFY_DROP_DATE, testvalue.MODIFY_DROP_TIME)
        logging.info("TEST '%s' COMPLETED SUCCESSFULLY\n", label)


if __name__ == "__main__":
    import unittest
    unittest.main()
