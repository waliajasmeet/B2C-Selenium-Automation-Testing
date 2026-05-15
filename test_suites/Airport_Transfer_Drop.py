# test_suites/Airport_Transfer_Drop.py
# Airport Transfer — Drop To Airport

import logging

from selenium.webdriver.common.by import By

import allure
import locators
import methods
import testvalue

from base_test import ServiceBaseTestCase


@allure.feature("Airport Transfer - Drop To Airport")
class TestAirportTransferDrop(ServiceBaseTestCase):
    _test_name = "Airport Transfer Drop"
    _tab_xpath = locators.AIRPORT_TRANSFER_TAB_XPATH
    _search_button_xpath = locators.AIRPORT_SEARCH_BUTTON_XPATH
    _service_label = "Drop To Airport"

    def _run_search(self, label, direction, city, date, time, go_to_payment=False, validate=False):
        """Core search flow — reused for all test cases."""

        logging.info("============================================================")
        logging.info("STARTING TEST: '%s'", label)
        logging.info("  Direction: %s | City: %s | Date: %s | Time: %s", direction, city, date, time)
        logging.info("  Payment flow: %s | Validation: %s", go_to_payment, validate)
        logging.info("============================================================")

        self._open_site(label)
        self._click_tab(label)

        # 3) Select direction
        logging.info("Step 3: Selecting direction '%s' from dropdown", direction)
        try:
            methods.safe_click(self.driver, By.XPATH, locators.DIRECTION_SELECT_XPATH)
            option_xpath = locators.DIRECTION_OPTION_XPATH_TEMPLATE.format(direction)
            methods.safe_click(self.driver, By.XPATH, option_xpath)
            logging.info("Direction '%s' selected successfully", direction)
        except Exception as e:
            self._take_screenshot(label, "direction")
            logging.error("FAILED to select direction: %s", e)
            self.fail(f"Direction select failed: {e}")

        # 4) Type city
        if city:
            logging.info("Step 4: Typing city name '%s' and selecting from suggestions", city)
            try:
                methods.type_and_select_first_option(
                    self.driver,
                    locators.AIRPORT_CITY_XPATH,
                    city,
                    first_option_xpath=locators.AIRPORT_CITY_FIRST_OPTION_XPATH,
                )
                logging.info("City '%s' entered and first suggestion selected", city)
            except Exception as e:
                self._take_screenshot(label, "city")
                logging.error("FAILED to enter city: %s", e)
                self.fail(f"City input failed: {e}")
        else:
            logging.info("Step 4: Skipping city input (left empty for worst case test)")

        # 5-6) Set date and time
        self._set_date(label, locators.AIRPORT_DATE_XPATH, date)
        self._set_time(label, locators.AIRPORT_TIME_XPATH, time)

        # 7) Dismiss dropdown, click search, post-search flow
        self._dismiss_dropdown()
        self._click_search(label)
        self._post_search(label, city, date, time, go_to_payment, validate)

    # ── Test methods ─────────────────────────────────────────────────

    @allure.story("Future Date Search")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Airport Transfer tab\n"
        "3. Select direction: Drop to Airport\n"
        "4. Enter city name and select from suggestions\n"
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
            testvalue.DROP_BEST_DIRECTION,
            testvalue.DROP_BEST_CITY,
            testvalue.DROP_BEST_DATE,
            testvalue.DROP_BEST_TIME,
            go_to_payment=True,
            validate=True,
        )

    @allure.story("Future Time Search")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Airport Transfer tab\n"
        "3. Select direction: Drop to Airport\n"
        "4. Enter city name and select from suggestions\n"
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
            testvalue.DROP_PRESENT_DIRECTION,
            testvalue.DROP_PRESENT_CITY,
            testvalue.DROP_PRESENT_DATE,
            testvalue.TIMING_FUTURE_12H,
            go_to_payment=True,
            validate=True,
        )

    @allure.story("Time Before 12 Hours Rejection")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Airport Transfer tab\n"
        "3. Select direction: Drop to Airport\n"
        "4. Enter city name and select from suggestions\n"
        "5. Set today's date\n"
        "6. Set a time less than 12 hours from now\n"
        "7. Click 'Search Your Ride' button\n"
        "8. Verify the site shows a validation error and does NOT navigate to results page"
    )
    def to_verify_user_cannot_select_time_before_12_hours(self):
        """Verify user cannot select a time less than 12 hours from now — site should reject."""
        self._run_search(
            "time_before_12h",
            testvalue.DROP_PRESENT_DIRECTION,
            testvalue.DROP_PRESENT_CITY,
            testvalue.DROP_PRESENT_DATE,
            testvalue.TIMING_BEFORE_12H,
        )

    @allure.story("Past Date Rejection")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Airport Transfer tab\n"
        "3. Select direction: Drop to Airport\n"
        "4. Enter city name and select from suggestions\n"
        "5. Set a past date\n"
        "6. Set pickup time\n"
        "7. Click 'Search Your Ride' button\n"
        "8. Verify the site shows a validation error and does NOT navigate to results page"
    )
    def to_verify_user_cannot_select_past_date(self):
        """Verify user cannot select past date — site should show validation error."""
        self._run_search(
            "past_date",
            testvalue.DROP_WORST_DIRECTION,
            testvalue.DROP_WORST_CITY,
            testvalue.DROP_WORST_DATE,
            testvalue.DROP_WORST_TIME,
        )

    @allure.story("Present Date Search")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Airport Transfer tab\n"
        "3. Select direction: Drop to Airport\n"
        "4. Enter city name and select from suggestions\n"
        "5. Set today's date\n"
        "6. Set current time\n"
        "7. Click 'Search Your Ride' button\n"
        "8. Validate results page shows correct location, date, and time (if page loads)"
    )
    def to_verify_user_can_select_present_date(self):
        """Verify user can select present date — site should show results."""
        self._run_search(
            "present_date",
            testvalue.DROP_PRESENT_DIRECTION,
            testvalue.DROP_PRESENT_CITY,
            testvalue.DROP_PRESENT_DATE,
            testvalue.DROP_PRESENT_TIME,
            validate=True,
        )


if __name__ == "__main__":
    import unittest
    unittest.main()
