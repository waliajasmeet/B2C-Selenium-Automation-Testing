# main.py
# Single test that runs whichever service is set in testdata.SERVICE_TYPE

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

SCREENSHOT_DIR = os.path.join(os.getcwd(), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class TestBooking(unittest.TestCase):
    screenshot_count = 0

    @classmethod
    def setUpClass(cls):
        logging.info("Setting up Chrome driver")
        logging.info("SERVICE_TYPE = %s", testdata.SERVICE_TYPE)
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")
        cls.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        cls.wait = methods.get_wait(cls.driver)
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
        TestBooking.screenshot_count += 1
        count = TestBooking.screenshot_count
        filename = f"error_{count}_{step_name}.png"
        path = os.path.join(SCREENSHOT_DIR, filename)
        logging.error("Step '%s' failed; saving screenshot #%d to %s", step_name, count, path)
        try:
            self.driver.save_screenshot(path)
        except Exception as e:
            logging.error("Failed to save screenshot: %s", e)

    def test_booking_flow(self):
        """Complete booking flow for the selected SERVICE_TYPE."""
        # 1) Open site
        try:
            methods.open_site(self.driver)
        except Exception as e:
            self._take_screenshot("open_site")
            self.fail(f"Open site failed: {e}")

        # 2) Click the correct tab
        try:
            methods.click_service_tab(self.driver)
        except Exception as e:
            self._take_screenshot("click_tab")
            self.fail(f"Click tab failed: {e}")

        # 3) Fill the search form
        try:
            methods.fill_search_form(self.driver)
        except Exception as e:
            self._take_screenshot("fill_form")
            self.fail(f"Fill form failed: {e}")

        # ── Self Drive: just submit the query and finish ──
        if methods.is_self_drive():
            try:
                methods.submit_self_drive_query(self.driver)
                logging.info("Self Drive query submitted successfully.")
            except Exception as e:
                self._take_screenshot("submit_query")
                self.fail(f"Submit query failed: {e}")

        # ── Other services: search > book > OTP > pay ──
        else:
            # 4) Click Search Your Ride
            try:
                methods.click_search_ride(self.driver)
            except Exception as e:
                self._take_screenshot("click_search")
                self.fail(f"Click search failed: {e}")

            # 5) Validate results
            try:
                result = methods.assert_results_loaded(self.driver)
                if result:
                    logging.info("Search returned results.")
                else:
                    logging.info("No rides found.")
                    return
            except Exception as e:
                self._take_screenshot("results_validation")
                self.fail(f"Results validation failed: {e}")

            # 6) Click Book Now
            try:
                methods.click_book_now(self.driver)
            except Exception as e:
                self._take_screenshot("book_now")
                self.fail(f"Book Now failed: {e}")

            # 7) Fill mobile + SEND OTP
            try:
                methods.fill_mobile_and_send_otp(self.driver)
            except Exception as e:
                self._take_screenshot("fill_mobile")
                self.fail(f"Fill mobile failed: {e}")

            # 8) Fill OTP + VERIFY
            try:
                methods.fill_otp_and_verify(self.driver)
            except Exception as e:
                self._take_screenshot("fill_otp")
                self.fail(f"OTP verification failed: {e}")

            # 9) Fill booking form
            try:
                methods.fill_booking_form(self.driver)
            except Exception as e:
                self._take_screenshot("fill_booking_form")
                self.fail(f"Fill booking form failed: {e}")

            # 10) T&C + Pay
            try:
                methods.tick_tnc_and_pay(self.driver)
            except Exception as e:
                self._take_screenshot("tnc_and_pay")
                self.fail(f"T&C and Pay failed: {e}")

        # Final screenshot
        import time as _time
        _time.sleep(3)
        stype = testdata.SERVICE_TYPE.strip().lower().replace(" ", "_")
        final_path = os.path.join(SCREENSHOT_DIR, f"final_{stype}.png")
        self.driver.save_screenshot(final_path)
        logging.info("Final screenshot saved: %s", final_path)


if __name__ == '__main__':
    unittest.main()
