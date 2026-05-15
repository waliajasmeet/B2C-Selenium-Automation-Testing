# test_suites/Local_Rental.py
# Local Rental

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import allure
import locators
import methods
import testvalue

from base_test import ServiceBaseTestCase


@allure.feature("Local Rental")
class TestLocalRental(ServiceBaseTestCase):
    _test_name = "Local Rental"
    _tab_xpath = locators.LOCAL_RENTAL_TAB_XPATH
    _search_button_xpath = locators.LOCAL_RENTAL_SEARCH_BUTTON_XPATH
    _service_label = "Local Rental"

    def _run_search(self, label, city, package, date, time, go_to_payment=False, validate=False):
        """Core search flow — reused for all test cases."""

        logging.info("============================================================")
        logging.info("STARTING TEST: '%s'", label)
        logging.info("  City: %s | Package: %s | Date: %s | Time: %s", city, package, date, time)
        logging.info("  Payment flow: %s | Validation: %s", go_to_payment, validate)
        logging.info("============================================================")

        self._open_site(label)
        self._click_tab(label)

        # 3) Type city and select first suggestion
        if city:
            logging.info("Step 3: Typing city name '%s' and selecting from suggestions", city)
            try:
                methods.type_and_select_first_option(
                    self.driver,
                    locators.LOCAL_RENTAL_CITY_XPATH,
                    city,
                    first_option_xpath=locators.LOCAL_RENTAL_CITY_FIRST_OPTION_XPATH,
                )
                logging.info("City '%s' entered and first suggestion selected", city)
            except Exception as e:
                self._take_screenshot(label, "city")
                logging.error("FAILED to enter city: %s", e)
                self.fail(f"City input failed: {e}")
        else:
            logging.info("Step 3: Skipping city input (left empty for worst case test)")

        # 4) Select package from dropdown
        logging.info("Step 4: Selecting package '%s' from dropdown", package)
        try:
            wait = WebDriverWait(self.driver, 15)
            select_elem = wait.until(EC.element_to_be_clickable((By.XPATH, locators.LOCAL_RENTAL_PACKAGE_XPATH)))
            logging.info("Waiting for package dropdown options to load from server...")
            WebDriverWait(self.driver, 10).until(
                lambda d: len(Select(d.find_element(By.XPATH, locators.LOCAL_RENTAL_PACKAGE_XPATH)).options) > 1
            )
            sel = Select(select_elem)
            options = [o.text.strip() for o in sel.options if o.text.strip() and o.get_attribute("value")]
            match = next((o for o in options if package.lower() in o.lower()), None)
            if match:
                sel.select_by_visible_text(match)
                logging.info("Package '%s' selected successfully by matching text", match)
            else:
                sel.select_by_index(1)
                logging.info("Package selected by index 1 (available options: %s)", options)
        except Exception as e:
            self._take_screenshot(label, "package")
            logging.error("FAILED to select package: %s", e)
            self.fail(f"Package select failed: {e}")

        # 5-6) Set date and time
        self._set_date(label, locators.LOCAL_RENTAL_DATE_XPATH, date)
        self._set_time(label, locators.LOCAL_RENTAL_TIME_XPATH, time)

        # 7) Dismiss dropdown, click search, post-search flow
        self._dismiss_dropdown()
        self._click_search(label)
        self._post_search(label, city, date, time, go_to_payment, validate)

    # ── Test methods ─────────────────────────────────────────────────

    @allure.story("Future Date Search")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Local Rental tab\n"
        "3. Enter city name and select from suggestions\n"
        "4. Select rental package from dropdown\n"
        "5. Set a future date (60 days from today)\n"
        "6. Set pickup time\n"
        "7. Click 'Search Your Ride' button\n"
        "8. Validate results page shows correct location, date, and time\n"
        "9. Click Book Now, login, fill traveller details, and proceed to payment"
    )
    def to_verify_user_can_select_future_date(self):
        """Verify user can select future date — goes to final payment state."""
        self._run_search(
            "future_date",
            testvalue.LR_BEST_CITY,
            testvalue.LR_BEST_PACKAGE,
            testvalue.LR_BEST_DATE,
            testvalue.LR_BEST_TIME,
            go_to_payment=True,
            validate=True,
        )

    @allure.story("Future Time Search")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Local Rental tab\n"
        "3. Enter city name and select from suggestions\n"
        "4. Select rental package from dropdown\n"
        "5. Set today's date\n"
        "6. Set a future time (later today)\n"
        "7. Click 'Search Your Ride' button\n"
        "8. Validate results page shows correct location, date, and time\n"
        "9. Click Book Now, login, fill traveller details, and proceed to payment"
    )
    def to_verify_user_can_select_future_time(self):
        """Verify user can select future time — goes to final payment state."""
        self._run_search(
            "future_time",
            testvalue.LR_PRESENT_CITY,
            testvalue.LR_PRESENT_PACKAGE,
            testvalue.LR_PRESENT_DATE,
            testvalue.TIMING_FUTURE_12H,
            go_to_payment=True,
            validate=True,
        )

    @allure.story("Time Before 12 Hours Rejection")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Local Rental tab\n"
        "3. Enter city name and select from suggestions\n"
        "4. Select rental package from dropdown\n"
        "5. Set today's date\n"
        "6. Set a time less than 12 hours from now\n"
        "7. Click 'Search Your Ride' button\n"
        "8. Verify the site shows a validation error and does NOT navigate to results page"
    )
    def to_verify_user_cannot_select_time_before_12_hours(self):
        """Verify user cannot select a time less than 12 hours from now — site should reject."""
        self._run_search(
            "time_before_12h",
            testvalue.LR_PRESENT_CITY,
            testvalue.LR_PRESENT_PACKAGE,
            testvalue.LR_PRESENT_DATE,
            testvalue.TIMING_BEFORE_12H,
        )

    @allure.story("Past Date Rejection")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Local Rental tab\n"
        "3. Enter city name and select from suggestions\n"
        "4. Select rental package from dropdown\n"
        "5. Set a past date\n"
        "6. Set pickup time\n"
        "7. Click 'Search Your Ride' button\n"
        "8. Verify the site shows a validation error and does NOT navigate to results page"
    )
    def to_verify_user_cannot_select_past_date(self):
        """Verify user cannot select past date — site should show validation error."""
        self._run_search(
            "past_date",
            testvalue.LR_WORST_CITY,
            testvalue.LR_WORST_PACKAGE,
            testvalue.LR_WORST_DATE,
            testvalue.LR_WORST_TIME,
        )

    @allure.story("Present Date Search")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Local Rental tab\n"
        "3. Enter city name and select from suggestions\n"
        "4. Select rental package from dropdown\n"
        "5. Set today's date\n"
        "6. Set current time\n"
        "7. Click 'Search Your Ride' button\n"
        "8. Validate results page shows correct location, date, and time (if page loads)"
    )
    def to_verify_user_can_select_present_date(self):
        """Verify user can select present date — site should show results."""
        self._run_search(
            "present_date",
            testvalue.LR_PRESENT_CITY,
            testvalue.LR_PRESENT_PACKAGE,
            testvalue.LR_PRESENT_DATE,
            testvalue.LR_PRESENT_TIME,
            validate=True,
        )


if __name__ == "__main__":
    import unittest
    unittest.main()
