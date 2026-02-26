# main.py
# Unittest runner that uses locators.py, testdata.py, and methods.py

import os
import unittest
import logging
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import locators
import testdata
import methods

# Ensure screenshots dir exists
SCREENSHOT_DIR = os.path.join(os.getcwd(), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class TestAirportTransfer(unittest.TestCase):
    screenshot_count = 0  # class-level counter, persists across runs

    @classmethod
    def setUpClass(cls):
        logging.info("Setting up Chrome driver")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")
        cls.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        cls.wait = methods.get_wait(cls.driver)
        # Count existing screenshots to continue numbering
        existing = [f for f in os.listdir(SCREENSHOT_DIR) if f.startswith("error_") and f.endswith(".png")]
        cls.screenshot_count = len(existing)

    @classmethod
    def tearDownClass(cls):
        logging.info("Quitting driver")
        try:
            cls.driver.quit()
        except Exception:
            pass

    def _take_screenshot(self, step_name):
        """Take an instant screenshot when an error occurs."""
        TestAirportTransfer.screenshot_count += 1
        count = TestAirportTransfer.screenshot_count
        filename = f"error_{count}_{step_name}.png"
        path = os.path.join(SCREENSHOT_DIR, filename)
        logging.error("Step '%s' failed; saving screenshot #%d to %s", step_name, count, path)
        try:
            self.driver.save_screenshot(path)
            logging.info("Screenshot #%d saved: %s", count, path)
        except Exception as e:
            logging.error("Failed to save screenshot: %s", e)

    def test_airport_transfer_search(self):
        """Complete Airport Transfer flow and validate results."""
        # 1) Open URL
        try:
            methods.open_site(self.driver)
        except Exception as e:
            self._take_screenshot("open_site")
            self.fail(f"Open site failed: {e}")

        # 2) Ensure Airport Transfer tab active
        try:
            methods.ensure_airport_transfer_tab(self.driver)
        except Exception as e:
            self._take_screenshot("airport_transfer_tab")
            self.fail(f"Airport transfer tab failed: {e}")

        # 3-6) Fill form (drop to airport, city, date, time)
        try:
            methods.fill_airport_transfer_form(self.driver)
        except Exception as e:
            self._take_screenshot("fill_form")
            self.fail(f"Fill form failed: {e}")

        # 7) Click search
        try:
            methods.click_search_ride(self.driver)
        except Exception as e:
            self._take_screenshot("click_search")
            self.fail(f"Click search failed: {e}")

        # 8) Validate results loaded (or handle 'no rides')
        try:
            result = methods.assert_results_loaded(self.driver)
            if result:
                logging.info("Search returned results.")
            else:
                logging.info("Search completed but no rides found (handled).")
                return  # no results to book
        except Exception as e:
            self._take_screenshot("results_validation")
            self.fail(f"Results validation failed: {e}")

        # 9) Click Book Now on first car
        try:
            methods.click_book_now(self.driver)
            logging.info("Booking page opened successfully.")
        except Exception as e:
            self._take_screenshot("book_now")
            self.fail(f"Book Now failed: {e}")

        # 10) Fill mobile number and click SEND OTP
        try:
            methods.fill_mobile_and_send_otp(self.driver)
            logging.info("Mobile number submitted, OTP sent.")
        except Exception as e:
            self._take_screenshot("fill_mobile")
            self.fail(f"Fill mobile number failed: {e}")

        # 11) Fill OTP and verify (waits for user input in terminal)
        try:
            methods.fill_otp_and_verify(self.driver)
            logging.info("OTP verified successfully.")
        except Exception as e:
            self._take_screenshot("fill_otp")
            self.fail(f"OTP verification failed: {e}")

        # 12) Fill booking form (last name, pickup location, pickup address)
        try:
            methods.fill_booking_form(self.driver)
            logging.info("Booking form filled.")
        except Exception as e:
            self._take_screenshot("fill_booking_form")
            self.fail(f"Fill booking form failed: {e}")

        # 13) Tick T&C checkbox and click Pay
        try:
            methods.tick_tnc_and_pay(self.driver)
            logging.info("T&C ticked and Pay clicked.")
        except Exception as e:
            self._take_screenshot("tnc_and_pay")
            self.fail(f"T&C and Pay failed: {e}")

        # 14) Take final screenshot
        import time as _time
        _time.sleep(3)
        final_path = os.path.join(SCREENSHOT_DIR, "final_result.png")
        self.driver.save_screenshot(final_path)
        logging.info("Final screenshot saved: %s", final_path)


if __name__ == '__main__':
    unittest.main()
