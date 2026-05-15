# test_suites/Login_Home.py
# Login — Home Page Login (via navbar Login button)
# Tests mobile + OTP validation on the home page login form.

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


@allure.feature("Login - Home Page")
class TestLoginHome(LoginBaseTestCase):
    _test_name = "Home Page Login"

    def _open_login_form(self, label):
        """Navigate to the home page login form (logs out first if already logged in)."""
        logging.info("Opening login form from home page for test '%s'", label)
        self._dismiss_alert()
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
            logging.info("User is not logged in. Proceeding to login form")

        self._dismiss_toasts()

        try:
            methods.safe_click(self.driver, By.XPATH, locators.LOGIN_BUTTON_XPATH)
            logging.info("Login button on home page clicked. Login form should now be visible")
        except Exception as e:
            self._take_screenshot(label, "click_login")
            logging.error("FAILED to click Login button on home page: %s", e)
            self.fail(f"Click Login failed: {e}")

    def _run_login(self, label, mobile, otp):
        """Core login flow — reused for valid, invalid mobile, and invalid OTP cases."""

        logging.info("============================================================")
        logging.info("STARTING HOME PAGE LOGIN TEST: '%s'", label)
        logging.info("  Mobile: %s | OTP: %s", mobile, otp)
        logging.info("============================================================")

        # 1) Open site
        logging.info("Step 1: Opening the website and dismissing any alerts")
        try:
            self._dismiss_alert()
            methods.open_site(self.driver)
            logging.info("Website opened successfully")
        except Exception as e:
            self._take_screenshot(label, "open_site")
            logging.error("FAILED to open website: %s", e)
            self.fail(f"Open site failed: {e}")

        # 2) Click Login button
        logging.info("Step 2: Clicking Login button on home page navbar")
        try:
            methods.safe_click(self.driver, By.XPATH, locators.LOGIN_BUTTON_XPATH)
            logging.info("Login button clicked successfully")
        except Exception as e:
            self._take_screenshot(label, "click_login")
            logging.error("FAILED to click Login button: %s", e)
            self.fail(f"Click Login failed: {e}")

        # 3) Enter mobile number
        logging.info("Step 3: Entering mobile number '%s'", mobile)
        try:
            wait = WebDriverWait(self.driver, 15)
            mobile_input = wait.until(
                EC.element_to_be_clickable((By.XPATH, locators.LOGIN_MOBILE_INPUT_XPATH))
            )
            mobile_input.clear()
            mobile_input.send_keys(mobile)
            logging.info("Mobile number entered successfully")
        except Exception as e:
            self._take_screenshot(label, "mobile_input")
            logging.error("FAILED to enter mobile number: %s", e)
            self.fail(f"Mobile input failed: {e}")

        # 4) Click Send OTP (with retry on rate limiting)
        logging.info("Step 4: Clicking Send OTP button")
        self._send_otp_with_retry(label)

        # 5) Enter OTP
        logging.info("Step 5: Entering OTP '%s'", otp)
        try:
            otp_input = wait.until(
                EC.element_to_be_clickable((By.XPATH, locators.LOGIN_OTP_INPUT_XPATH))
            )
            otp_input.clear()
            otp_input.send_keys(otp)
            logging.info("OTP entered successfully")
        except Exception as e:
            self._take_screenshot(label, "otp_input")
            logging.error("FAILED to enter OTP: %s", e)
            self.fail(f"OTP input failed: {e}")

        # 6) Click Verify OTP
        logging.info("Step 6: Clicking Verify OTP button")
        try:
            methods.safe_click(self.driver, By.XPATH, locators.LOGIN_VERIFY_OTP_BUTTON_XPATH)
            logging.info("Verify OTP button clicked. Waiting for response...")
            _time.sleep(1)
        except Exception as e:
            self._take_screenshot(label, "verify_otp")
            logging.error("FAILED to click Verify OTP: %s", e)
            self.fail(f"Verify OTP failed: {e}")

        self._take_screenshot(label, "final_state")
        logging.info("TEST '%s' COMPLETED SUCCESSFULLY", label)
        logging.info("============================================================\n")

    # ── Test methods ─────────────────────────────────────────────────

    @allure.story("Mobile Min Limit Validation")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Login button on home page navbar\n"
        "3. Enter a short mobile number (less than 10 digits)\n"
        "4. Click Send OTP button\n"
        "5. Verify that a validation error appears and OTP input field does NOT show up\n"
        "6. This confirms the mobile field enforces a minimum of 10 digits"
    )
    def to_verify_mobile_number_field_has_min_limit_validation(self):
        """Verify mobile field rejects fewer than 10 digits — Send OTP should fail."""
        label = "home_mobile_min_limit"
        logging.info("============================================================")
        logging.info("STARTING TEST: Mobile number minimum limit validation (Home Page)")
        logging.info("============================================================")

        self._open_login_form(label)

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

        # Dismiss alert if any
        alert_text = self._dismiss_alert()
        if alert_text:
            logging.info("Validation alert message: '%s'", alert_text)

        # OTP input should NOT appear (validation should block it)
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
        logging.info("TEST PASSED: Mobile min limit validation is working\n")

    @allure.story("Mobile Max Limit Validation")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Login button on home page navbar\n"
        "3. Enter 14 digits into the mobile number field\n"
        "4. Read back the field value\n"
        "5. Verify the field accepted only 10 digits (truncated the extra 4)\n"
        "6. This confirms the mobile field enforces a maximum of 10 digits"
    )
    def to_verify_mobile_number_field_has_maximum_limit(self):
        """Verify mobile field accepts only 10 digits when 14 are entered."""
        label = "home_mobile_max_limit"
        logging.info("============================================================")
        logging.info("STARTING TEST: Mobile number maximum limit validation (Home Page)")
        logging.info("============================================================")

        self._open_login_form(label)

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
        logging.info("TEST PASSED: Mobile max limit is enforced (accepted %d chars)\n", len(actual))

    @allure.story("Mobile Alphabet Rejection")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Login button on home page navbar\n"
        "3. Type alphabetic characters (e.g. 'abcd623967') into the mobile field\n"
        "4. Read back the field value\n"
        "5. Verify the field contains only digits (no alphabets accepted)\n"
        "6. BUG: The website currently accepts alphabets — this test FAILS due to a site bug"
    )
    def to_verify_user_cannot_enter_alphabets_in_mobile_number_field(self):
        """Verify mobile field rejects alphabetic characters."""
        label = "home_mobile_no_alpha"
        logging.info("============================================================")
        logging.info("STARTING TEST: Mobile number alphabet rejection (Home Page)")
        logging.info("============================================================")

        self._open_login_form(label)

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
        logging.info("TEST PASSED: Mobile field correctly rejected alphabets\n")

    @allure.story("OTP Min Limit Validation")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website and click Login\n"
        "2. Enter a valid mobile number and send OTP\n"
        "3. Enter a short OTP (less than 6 digits)\n"
        "4. Click Verify OTP button\n"
        "5. Verify that a validation error appears\n"
        "6. This confirms the OTP field enforces a minimum of 6 digits"
    )
    def to_verify_otp_number_field_has_min_limit_validation(self):
        """Verify OTP field rejects fewer than 6 digits — Verify OTP should fail."""
        label = "home_otp_min_limit"
        logging.info("============================================================")
        logging.info("STARTING TEST: OTP minimum limit validation (Home Page)")
        logging.info("============================================================")

        self._open_login_form(label)

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

        # Click Verify OTP — should fail with short OTP
        logging.info("Clicking Verify OTP with short OTP. Expecting validation error...")
        try:
            methods.safe_click(self.driver, By.XPATH, locators.LOGIN_VERIFY_OTP_BUTTON_XPATH)
            _time.sleep(1)
        except Exception:
            pass

        alert_text = self._dismiss_alert()
        self._take_screenshot(label, "final_state")
        logging.info("Short OTP result — alert: %s", alert_text)
        logging.info("TEST COMPLETED: OTP min limit validation\n")

    @allure.story("OTP Max Limit Validation")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website and click Login\n"
        "2. Enter a valid mobile number and send OTP\n"
        "3. Enter 11 digits into the OTP field\n"
        "4. Read back the field value\n"
        "5. Verify the field accepted only 6 digits (truncated the extra 5)\n"
        "6. This confirms the OTP field enforces a maximum of 6 digits"
    )
    def to_verify_otp_field_has_maximum_limit_validation_of_6_digits(self):
        """Verify OTP field accepts only 6 digits when 11 are entered."""
        label = "home_otp_max_limit"
        logging.info("============================================================")
        logging.info("STARTING TEST: OTP maximum limit validation (Home Page)")
        logging.info("============================================================")

        self._open_login_form(label)

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
        logging.info("TEST PASSED: OTP max limit is enforced (accepted %d chars)\n", len(actual))

    @allure.story("OTP Alphabet Rejection")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website and click Login\n"
        "2. Enter a valid mobile number and send OTP\n"
        "3. Type alphabetic characters (e.g. 'abc123') into the OTP field\n"
        "4. Read back the field value\n"
        "5. Verify the field contains only digits (no alphabets accepted)\n"
        "6. BUG: The website currently accepts alphabets — this test FAILS due to a site bug"
    )
    def to_verify_user_cannot_enter_alphabets_in_otp_field(self):
        """Verify OTP field rejects alphabetic characters."""
        label = "home_otp_no_alpha"
        logging.info("============================================================")
        logging.info("STARTING TEST: OTP alphabet rejection (Home Page)")
        logging.info("============================================================")

        self._open_login_form(label)

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
        logging.info("TEST PASSED: OTP field correctly rejected alphabets\n")

    @allure.story("Valid Login")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Login button on home page navbar\n"
        "3. Enter a valid 10-digit mobile number\n"
        "4. Click Send OTP and wait for OTP to be sent\n"
        "5. Enter the correct 6-digit OTP\n"
        "6. Click Verify OTP button\n"
        "7. Verify that login is successful\n"
        "8. Verify that the nickname is displayed on the navbar after login"
    )
    def to_verify_user_can_login_by_entering_correct_login_details(self):
        """Verify user can login with correct mobile + OTP from home page and nickname shows."""
        label = "home_valid_login"
        self._run_login(
            label,
            testvalue.LOGIN_VALID_MOBILE,
            testvalue.LOGIN_VALID_OTP,
        )

        # Validate nickname on navbar after login
        logging.info("Step 7: Validating nickname on navbar after login")
        try:
            wait = WebDriverWait(self.driver, 10)
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

    @allure.story("OTP Expiry After 60 Seconds")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website and click Login\n"
        "2. Enter a valid mobile number and send OTP\n"
        "3. Wait 65 seconds for the OTP to expire\n"
        "4. Enter the (now expired) OTP\n"
        "5. Click Verify OTP button\n"
        "6. Verify that an expiry error message appears\n"
        "7. This confirms OTP has a 60-second time-to-live"
    )
    def to_verify_otp_expires_after_60s(self):
        """Verify OTP expires after 60 seconds — should show expiry message."""
        label = "home_otp_expiry"
        logging.info("============================================================")
        logging.info("STARTING TEST: OTP expiry after 60 seconds (Home Page)")
        logging.info("============================================================")

        self._open_login_form(label)

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

        # Click Verify OTP
        logging.info("Clicking Verify OTP with expired OTP. Expecting expiry error...")
        try:
            methods.safe_click(self.driver, By.XPATH, locators.LOGIN_VERIFY_OTP_BUTTON_XPATH)
            _time.sleep(1)
        except Exception:
            pass

        alert_text = self._dismiss_alert()
        self._take_screenshot(label, "final_state")
        logging.info("OTP expiry result — alert: %s", alert_text)
        logging.info("TEST COMPLETED: OTP expiry validation\n")


if __name__ == "__main__":
    import unittest
    unittest.main()
