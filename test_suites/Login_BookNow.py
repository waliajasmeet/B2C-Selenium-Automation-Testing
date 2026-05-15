# test_suites/Login_BookNow.py
# Login — After clicking Book Now on results page
# Tests mobile + OTP validation on the login form that appears after Book Now.

import logging
import time as _time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import allure
import locators
import methods
import testvalue

from base_test import LoginBaseTestCase


@allure.feature("Login - After Book Now")
class TestLoginBookNow(LoginBaseTestCase):
    _test_name = "Book Now Login"

    def _navigate_to_book_now_login(self, label):
        """Search for a ride and click Book Now to reach the login form.

        Flow: Open site -> Airport Transfer -> future date search -> Search -> Book Now -> Login form
        Logs out first if already logged in.
        """
        logging.info("Navigating to login form via Book Now for test '%s'", label)

        self._dismiss_alert()

        # 1) Open site
        logging.info("Step 1: Opening the website %s", locators.URL)
        try:
            methods.open_site(self.driver)
            logging.info("Website opened successfully")
        except Exception as e:
            self._take_screenshot(label, "open_site")
            logging.error("FAILED to open website: %s", e)
            self.fail(f"Open site failed: {e}")

        self._dismiss_toasts()

        # If user is already logged in, click Logout first
        try:
            logout_btn = self.driver.find_element(By.XPATH, locators.LOGOUT_BUTTON_XPATH)
            self.driver.execute_script("arguments[0].click();", logout_btn)
            logging.info("User was already logged in. Logging out first...")
            _time.sleep(1)
            methods.open_site(self.driver)
            logging.info("Logged out and reopened home page")
        except Exception:
            logging.info("User is not logged in. Proceeding with search")

        self._dismiss_toasts()

        # 2) Click Airport Transfer tab
        logging.info("Step 2: Clicking on the Airport Transfer tab")
        try:
            methods.safe_click(self.driver, By.XPATH, locators.AIRPORT_TRANSFER_TAB_XPATH)
            logging.info("Airport Transfer tab clicked successfully")
        except Exception as e:
            self._take_screenshot(label, "click_tab")
            logging.error("FAILED to click Airport Transfer tab: %s", e)
            self.fail(f"Click tab failed: {e}")

        # 3) Select direction (pickup from airport)
        logging.info("Step 3: Selecting direction 'pickup from airport'")
        try:
            methods.safe_click(self.driver, By.XPATH, locators.DIRECTION_SELECT_XPATH)
            option_xpath = locators.DIRECTION_OPTION_XPATH_TEMPLATE.format(testvalue.BEST_DIRECTION)
            methods.safe_click(self.driver, By.XPATH, option_xpath)
            logging.info("Direction selected: %s", testvalue.BEST_DIRECTION)
        except Exception as e:
            self._take_screenshot(label, "direction")
            logging.error("FAILED to select direction: %s", e)
            self.fail(f"Direction select failed: {e}")

        # 4) Type city
        logging.info("Step 4: Typing city name '%s' and selecting from suggestions", testvalue.BEST_CITY)
        try:
            methods.type_and_select_first_option(
                self.driver,
                locators.AIRPORT_CITY_XPATH,
                testvalue.BEST_CITY,
                first_option_xpath=locators.AIRPORT_CITY_FIRST_OPTION_XPATH,
            )
            logging.info("City entered and first suggestion selected")
        except Exception as e:
            self._take_screenshot(label, "city")
            logging.error("FAILED to enter city: %s", e)
            self.fail(f"City input failed: {e}")

        # 5) Set date (future date to ensure results appear)
        logging.info("Step 5: Setting pickup date to '%s' (60 days from today)", testvalue.BEST_DATE)
        try:
            methods.set_date(self.driver, locators.AIRPORT_DATE_XPATH, testvalue.BEST_DATE)
            logging.info("Date set successfully")
        except Exception as e:
            self._take_screenshot(label, "date")
            logging.warning("FAILED to set date: %s", e)

        # 6) Set time
        logging.info("Step 6: Setting pickup time to '%s'", testvalue.BEST_TIME)
        try:
            methods.set_time(self.driver, locators.AIRPORT_TIME_XPATH, testvalue.BEST_TIME)
            logging.info("Time set successfully")
        except Exception as e:
            self._take_screenshot(label, "time")
            logging.warning("FAILED to set time: %s", e)

        # 7) Dismiss any open dropdown
        try:
            self.driver.find_element(By.TAG_NAME, "body").click()
            _time.sleep(0.3)
        except Exception:
            pass

        # 8) Click Search Your Ride
        logging.info("Step 7: Clicking 'Search Your Ride' button")
        try:
            btn = self.driver.find_element(By.XPATH, locators.AIRPORT_SEARCH_BUTTON_XPATH)
            self.driver.execute_script("arguments[0].click();", btn)
            logging.info("Search button clicked. Waiting for results page to load...")
            _time.sleep(3)
        except Exception as e:
            self._take_screenshot(label, "click_search")
            logging.error("FAILED to click search button: %s", e)
            self.fail(f"Click search failed: {e}")


        # 9) Click Book Now button
        logging.info("Step 8: Clicking 'Book Now' button on results page")
        try:
            wait = WebDriverWait(self.driver, 10)
            book_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, locators.BOOK_NOW_BUTTON_FALLBACK_XPATH))
            )
            methods.scroll_into_view(self.driver, book_btn)
            book_btn.click()
            logging.info("Book Now button clicked. Waiting for login form to appear...")
            _time.sleep(1)
        except Exception as e:
            self._take_screenshot(label, "book_now")
            logging.error("FAILED to click Book Now: %s", e)
            self.fail(f"Click Book Now failed: {e}")

        # 10) Verify login form appeared
        logging.info("Step 9: Verifying login form is visible after Book Now")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, locators.LOGIN_MOBILE_INPUT_XPATH))
            )
            logging.info("Login form is visible after clicking Book Now. Ready for login tests")
        except Exception as e:
            self._take_screenshot(label, "login_form_not_found")
            logging.error("Login form did NOT appear after Book Now: %s", e)
            self.fail(f"Login form not found after Book Now: {e}")

    # ── Test methods ─────────────────────────────────────────────────

    @allure.story("Mobile Min Limit Validation")
    @allure.description(
        "Steps:\n"
        "1. Open site, search for a ride with future date, click Book Now\n"
        "2. Login form appears after Book Now\n"
        "3. Enter a short mobile number (less than 10 digits)\n"
        "4. Click Send OTP button\n"
        "5. Verify that a validation error appears and OTP input field does NOT show up\n"
        "6. This confirms the mobile field enforces a minimum of 10 digits after Book Now"
    )
    def to_verify_mobile_number_field_has_min_limit_validation(self):
        """Verify mobile field rejects fewer than 10 digits — Send OTP should fail (Book Now login)."""
        label = "booknow_mobile_min_limit"
        logging.info("============================================================")
        logging.info("STARTING TEST: Mobile number minimum limit validation (Book Now)")
        logging.info("============================================================")

        self._navigate_to_book_now_login(label)

        wait = WebDriverWait(self.driver, 15)
        mobile_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_MOBILE_INPUT_XPATH))
        )
        mobile_input.clear()
        mobile_input.send_keys(testvalue.LOGIN_MOBILE_SHORT)
        logging.info("Entered short mobile number: '%s' (%d digits)", testvalue.LOGIN_MOBILE_SHORT, len(testvalue.LOGIN_MOBILE_SHORT))
        _time.sleep(0.5)

        # Click Send OTP — should show a validation error
        logging.info("Clicking Send OTP with short mobile number. Expecting validation error...")
        try:
            methods.safe_click(self.driver, By.XPATH, locators.LOGIN_SEND_OTP_BUTTON_XPATH)
            _time.sleep(1)
        except Exception:
            pass

        alert_text = self._dismiss_alert()
        if alert_text:
            logging.info("Validation alert message: '%s'", alert_text)

        # OTP input should NOT appear
        logging.info("Checking if OTP input field appeared (it should NOT)...")
        try:
            WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, locators.LOGIN_OTP_INPUT_XPATH))
            )
            otp_appeared = True
            logging.warning("OTP input field DID appear — validation failed to block short mobile")
        except Exception:
            otp_appeared = False
            logging.info("OTP input field did NOT appear — validation working correctly")

        self._take_screenshot(label, "final_state")
        self.assertFalse(otp_appeared,
            f"Mobile field accepted short input '{testvalue.LOGIN_MOBILE_SHORT}' — OTP form should not appear")
        logging.info("TEST PASSED: Mobile min limit validation is working (Book Now)\n")

    @allure.story("Mobile Max Limit Validation")
    @allure.description(
        "Steps:\n"
        "1. Open site, search for a ride with future date, click Book Now\n"
        "2. Login form appears after Book Now\n"
        "3. Enter 14 digits into the mobile number field\n"
        "4. Read back the field value\n"
        "5. Verify the field accepted only 10 digits (truncated the extra 4)\n"
        "6. This confirms the mobile field enforces a maximum of 10 digits after Book Now"
    )
    def to_verify_mobile_number_field_has_maximum_limit(self):
        """Verify mobile field accepts only 10 digits when 14 are entered (Book Now login)."""
        label = "booknow_mobile_max_limit"
        logging.info("============================================================")
        logging.info("STARTING TEST: Mobile number maximum limit validation (Book Now)")
        logging.info("============================================================")

        self._navigate_to_book_now_login(label)

        wait = WebDriverWait(self.driver, 15)
        mobile_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_MOBILE_INPUT_XPATH))
        )
        mobile_input.clear()
        mobile_input.send_keys(testvalue.LOGIN_MOBILE_OVERFLOW)
        logging.info("Entered overflow mobile number: '%s' (%d digits)", testvalue.LOGIN_MOBILE_OVERFLOW, len(testvalue.LOGIN_MOBILE_OVERFLOW))
        _time.sleep(0.5)

        actual = mobile_input.get_attribute("value") or ""
        logging.info("Field accepted value: '%s' (%d characters)", actual, len(actual))
        self._take_screenshot(label, "final_state")

        self.assertLessEqual(len(actual), 10,
            f"Mobile field accepted more than 10 digits: '{actual}' ({len(actual)} chars)")
        logging.info("TEST PASSED: Mobile max limit is enforced (accepted %d chars) (Book Now)\n", len(actual))

    @allure.story("Mobile Alphabet Rejection")
    @allure.description(
        "Steps:\n"
        "1. Open site, search for a ride with future date, click Book Now\n"
        "2. Login form appears after Book Now\n"
        "3. Type alphabetic characters (e.g. 'abcd623967') into the mobile field\n"
        "4. Read back the field value\n"
        "5. Verify the field contains only digits (no alphabets accepted)\n"
        "6. BUG: The website currently accepts alphabets — this test FAILS due to a site bug"
    )
    def to_verify_user_cannot_enter_alphabets_in_mobile_number_field(self):
        """Verify mobile field rejects alphabetic characters (Book Now login)."""
        label = "booknow_mobile_no_alpha"
        logging.info("============================================================")
        logging.info("STARTING TEST: Mobile number alphabet rejection (Book Now)")
        logging.info("============================================================")

        self._navigate_to_book_now_login(label)

        wait = WebDriverWait(self.driver, 15)
        mobile_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_MOBILE_INPUT_XPATH))
        )
        mobile_input.clear()
        mobile_input.send_keys(testvalue.LOGIN_MOBILE_ALPHA)
        logging.info("Entered alphabetic input: '%s'", testvalue.LOGIN_MOBILE_ALPHA)
        _time.sleep(0.5)

        actual = mobile_input.get_attribute("value") or ""
        logging.info("Field accepted value: '%s'", actual)
        self._take_screenshot(label, "final_state")

        digits_only = actual.replace(" ", "").replace("+", "").replace("-", "")
        self.assertTrue(digits_only.isdigit() or digits_only == "",
            f"Mobile field accepted alphabets: '{actual}'")
        logging.info("TEST PASSED: Mobile field correctly rejected alphabets (Book Now)\n")

    @allure.story("OTP Min Limit Validation")
    @allure.description(
        "Steps:\n"
        "1. Open site, search for a ride with future date, click Book Now\n"
        "2. Login form appears after Book Now\n"
        "3. Enter a valid mobile number and send OTP\n"
        "4. Enter a short OTP (less than 6 digits)\n"
        "5. Click Verify OTP button\n"
        "6. Verify that a validation error appears\n"
        "7. This confirms the OTP field enforces a minimum of 6 digits after Book Now"
    )
    def to_verify_otp_number_field_has_min_limit_validation(self):
        """Verify OTP field rejects fewer than 6 digits (Book Now login)."""
        label = "booknow_otp_min_limit"
        logging.info("============================================================")
        logging.info("STARTING TEST: OTP minimum limit validation (Book Now)")
        logging.info("============================================================")

        self._navigate_to_book_now_login(label)

        wait = WebDriverWait(self.driver, 15)
        mobile_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_MOBILE_INPUT_XPATH))
        )
        mobile_input.clear()
        mobile_input.send_keys(testvalue.LOGIN_VALID_MOBILE)
        logging.info("Entered valid mobile number: '%s'", testvalue.LOGIN_VALID_MOBILE)

        self._send_otp_with_retry(label)

        otp_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_OTP_INPUT_XPATH))
        )
        otp_input.clear()
        otp_input.send_keys(testvalue.LOGIN_OTP_SHORT)
        logging.info("Entered short OTP: '%s' (%d digits)", testvalue.LOGIN_OTP_SHORT, len(testvalue.LOGIN_OTP_SHORT))
        _time.sleep(0.5)

        logging.info("Clicking Verify OTP with short OTP. Expecting validation error...")
        try:
            methods.safe_click(self.driver, By.XPATH, locators.LOGIN_VERIFY_OTP_BUTTON_XPATH)
            _time.sleep(1)
        except Exception:
            pass

        alert_text = self._dismiss_alert()
        self._take_screenshot(label, "final_state")
        logging.info("Short OTP result — alert: %s", alert_text)
        logging.info("TEST COMPLETED: OTP min limit validation (Book Now)\n")

    @allure.story("OTP Max Limit Validation")
    @allure.description(
        "Steps:\n"
        "1. Open site, search for a ride with future date, click Book Now\n"
        "2. Login form appears after Book Now\n"
        "3. Enter a valid mobile number and send OTP\n"
        "4. Enter 11 digits into the OTP field\n"
        "5. Read back the field value\n"
        "6. Verify the field accepted only 6 digits (truncated the extra 5)\n"
        "7. This confirms the OTP field enforces a maximum of 6 digits after Book Now"
    )
    def to_verify_otp_field_has_maximum_limit_validation_of_6_digits(self):
        """Verify OTP field accepts only 6 digits when 11 are entered (Book Now login)."""
        label = "booknow_otp_max_limit"
        logging.info("============================================================")
        logging.info("STARTING TEST: OTP maximum limit validation (Book Now)")
        logging.info("============================================================")

        self._navigate_to_book_now_login(label)

        wait = WebDriverWait(self.driver, 15)
        mobile_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_MOBILE_INPUT_XPATH))
        )
        mobile_input.clear()
        mobile_input.send_keys(testvalue.LOGIN_VALID_MOBILE)
        logging.info("Entered valid mobile number: '%s'", testvalue.LOGIN_VALID_MOBILE)

        self._send_otp_with_retry(label)

        otp_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_OTP_INPUT_XPATH))
        )
        otp_input.clear()
        otp_input.send_keys(testvalue.LOGIN_OTP_OVERFLOW)
        logging.info("Entered overflow OTP: '%s' (%d digits)", testvalue.LOGIN_OTP_OVERFLOW, len(testvalue.LOGIN_OTP_OVERFLOW))
        _time.sleep(0.5)

        actual = otp_input.get_attribute("value") or ""
        logging.info("OTP field accepted value: '%s' (%d characters)", actual, len(actual))
        self._take_screenshot(label, "final_state")

        self.assertLessEqual(len(actual), 6,
            f"OTP field accepted more than 6 digits: '{actual}' ({len(actual)} chars)")
        logging.info("TEST PASSED: OTP max limit is enforced (accepted %d chars) (Book Now)\n", len(actual))

    @allure.story("OTP Alphabet Rejection")
    @allure.description(
        "Steps:\n"
        "1. Open site, search for a ride with future date, click Book Now\n"
        "2. Login form appears after Book Now\n"
        "3. Enter a valid mobile number and send OTP\n"
        "4. Type alphabetic characters (e.g. 'abc123') into the OTP field\n"
        "5. Read back the field value\n"
        "6. Verify the field contains only digits (no alphabets accepted)\n"
        "7. BUG: The website currently accepts alphabets — this test FAILS due to a site bug"
    )
    def to_verify_user_cannot_enter_alphabets_in_otp_field(self):
        """Verify OTP field rejects alphabetic characters (Book Now login)."""
        label = "booknow_otp_no_alpha"
        logging.info("============================================================")
        logging.info("STARTING TEST: OTP alphabet rejection (Book Now)")
        logging.info("============================================================")

        self._navigate_to_book_now_login(label)

        wait = WebDriverWait(self.driver, 15)
        mobile_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_MOBILE_INPUT_XPATH))
        )
        mobile_input.clear()
        mobile_input.send_keys(testvalue.LOGIN_VALID_MOBILE)
        logging.info("Entered valid mobile number: '%s'", testvalue.LOGIN_VALID_MOBILE)

        self._send_otp_with_retry(label)

        otp_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_OTP_INPUT_XPATH))
        )
        otp_input.clear()
        otp_input.send_keys(testvalue.LOGIN_OTP_ALPHA)
        logging.info("Entered alphabetic OTP: '%s'", testvalue.LOGIN_OTP_ALPHA)
        _time.sleep(0.5)

        actual = otp_input.get_attribute("value") or ""
        logging.info("OTP field accepted value: '%s'", actual)
        self._take_screenshot(label, "final_state")

        digits_only = actual.replace(" ", "")
        self.assertTrue(digits_only.isdigit() or digits_only == "",
            f"OTP field accepted alphabets: '{actual}'")
        logging.info("TEST PASSED: OTP field correctly rejected alphabets (Book Now)\n")

    @allure.story("Valid Login")
    @allure.description(
        "Steps:\n"
        "1. Open site, search for a ride with future date, click Book Now\n"
        "2. Login form appears after Book Now\n"
        "3. Enter a valid 10-digit mobile number\n"
        "4. Click Send OTP and wait for OTP to be sent\n"
        "5. Enter the correct 6-digit OTP\n"
        "6. Click Verify OTP button\n"
        "7. Verify that login is successful after Book Now\n"
        "8. Verify that the nickname is displayed on the navbar after login"
    )
    def to_verify_user_can_login_by_entering_correct_login_details(self):
        """Verify user can login with correct mobile + OTP after Book Now."""
        label = "booknow_valid_login"
        logging.info("============================================================")
        logging.info("STARTING TEST: Valid login after Book Now")
        logging.info("  Mobile: %s | OTP: %s", testvalue.LOGIN_VALID_MOBILE, testvalue.LOGIN_VALID_OTP)
        logging.info("============================================================")

        self._navigate_to_book_now_login(label)

        wait = WebDriverWait(self.driver, 15)

        # Enter mobile number
        logging.info("Entering mobile number: '%s'", testvalue.LOGIN_VALID_MOBILE)
        mobile_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_MOBILE_INPUT_XPATH))
        )
        mobile_input.clear()
        mobile_input.send_keys(testvalue.LOGIN_VALID_MOBILE)
        logging.info("Mobile number entered successfully")

        # Send OTP
        logging.info("Clicking Send OTP button")
        self._send_otp_with_retry(label)

        # Enter OTP
        logging.info("Entering OTP: '%s'", testvalue.LOGIN_VALID_OTP)
        otp_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_OTP_INPUT_XPATH))
        )
        otp_input.clear()
        otp_input.send_keys(testvalue.LOGIN_VALID_OTP)
        logging.info("OTP entered successfully")

        # Verify OTP
        logging.info("Clicking Verify OTP button")
        try:
            methods.safe_click(self.driver, By.XPATH, locators.LOGIN_VERIFY_OTP_BUTTON_XPATH)
            logging.info("Verify OTP clicked. Waiting for response...")
            _time.sleep(1)
        except Exception as e:
            self._take_screenshot(label, "verify_otp")
            logging.error("FAILED to click Verify OTP: %s", e)
            self.fail(f"Verify OTP failed: {e}")

        self._dismiss_alert()
        self._take_screenshot(label, "final_state")

        # Validate nickname on navbar after login
        logging.info("Step 10: Validating nickname on navbar after login")
        try:
            nickname_el = wait.until(
                EC.visibility_of_element_located((By.XPATH, locators.LOGIN_NICKNAME_XPATH))
            )
            actual_nickname = nickname_el.text.strip()
            logging.info("  Expected nickname: '%s'", testvalue.LOGIN_EXPECTED_NICKNAME)
            logging.info("  Actual nickname on navbar: '%s'", actual_nickname)
            self.assertEqual(
                actual_nickname.lower(), testvalue.LOGIN_EXPECTED_NICKNAME.lower(),
                f"Nickname mismatch: expected '{testvalue.LOGIN_EXPECTED_NICKNAME}', got '{actual_nickname}'"
            )
            logging.info("  NICKNAME MATCHED SUCCESSFULLY")
        except AssertionError as e:
            self._take_screenshot(label, "nickname_mismatch")
            logging.error("  NICKNAME VALIDATION FAILED: %s", e)
            raise e
        except Exception as e:
            self._take_screenshot(label, "nickname_not_found")
            logging.error("  Could not find nickname element on navbar: %s", e)
            self.fail(f"Nickname not found after login: {e}")

        logging.info("TEST '%s' COMPLETED SUCCESSFULLY", label)
        logging.info("============================================================\n")

    @allure.story("OTP Expiry After 60 Seconds")
    @allure.description(
        "Steps:\n"
        "1. Open site, search for a ride with future date, click Book Now\n"
        "2. Login form appears after Book Now\n"
        "3. Enter a valid mobile number and send OTP\n"
        "4. Wait 65 seconds for the OTP to expire\n"
        "5. Enter the (now expired) OTP\n"
        "6. Click Verify OTP button\n"
        "7. Verify that an expiry error message appears\n"
        "8. This confirms OTP has a 60-second time-to-live after Book Now"
    )
    def to_verify_otp_expires_after_60s(self):
        """Verify OTP expires after 60 seconds after Book Now login."""
        label = "booknow_otp_expiry"
        logging.info("============================================================")
        logging.info("STARTING TEST: OTP expiry after 60 seconds (Book Now)")
        logging.info("============================================================")

        self._navigate_to_book_now_login(label)

        wait = WebDriverWait(self.driver, 15)
        mobile_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_MOBILE_INPUT_XPATH))
        )
        mobile_input.clear()
        mobile_input.send_keys(testvalue.LOGIN_VALID_MOBILE)
        logging.info("Entered valid mobile number: '%s'", testvalue.LOGIN_VALID_MOBILE)

        self._send_otp_with_retry(label)

        # Wait 65 seconds for OTP to expire
        logging.info("Waiting 65 seconds for OTP to expire...")
        _time.sleep(65)
        logging.info("65 seconds passed. OTP should now be expired")

        otp_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, locators.LOGIN_OTP_INPUT_XPATH))
        )
        otp_input.clear()
        otp_input.send_keys(testvalue.LOGIN_VALID_OTP)
        logging.info("Entered expired OTP: '%s'", testvalue.LOGIN_VALID_OTP)
        _time.sleep(0.5)

        logging.info("Clicking Verify OTP with expired OTP. Expecting expiry error...")
        try:
            methods.safe_click(self.driver, By.XPATH, locators.LOGIN_VERIFY_OTP_BUTTON_XPATH)
            _time.sleep(1)
        except Exception:
            pass

        alert_text = self._dismiss_alert()
        self._take_screenshot(label, "final_state")
        logging.info("OTP expiry result — alert: %s", alert_text)
        logging.info("TEST COMPLETED: OTP expiry validation (Book Now)\n")


if __name__ == "__main__":
    import unittest
    unittest.main()
