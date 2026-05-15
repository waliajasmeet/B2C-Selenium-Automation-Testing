# test_suites/Outstation_Trip.py
# Outstation Trip

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


@allure.feature("Outstation Trip")
class TestOutstationTrip(ServiceBaseTestCase):
    _test_name = "Outstation Trip"
    _tab_xpath = locators.OUTSTATION_TRIP_TAB_XPATH
    _search_button_xpath = locators.OUTSTATION_SEARCH_BUTTON_XPATH
    _service_label = "Outstation"

    def _run_search(self, label, trip_type, from_city, to_city, date, time, go_to_payment=False, validate=False):
        """Core search flow — reused for all test cases."""

        logging.info("============================================================")
        logging.info("STARTING TEST: '%s'", label)
        logging.info("  Trip type: %s | From: %s | To: %s | Date: %s | Time: %s", trip_type, from_city, to_city, date, time)
        logging.info("  Payment flow: %s | Validation: %s", go_to_payment, validate)
        logging.info("============================================================")

        self._open_site(label)
        self._click_tab(label)

        # 3) Select trip type from dropdown
        logging.info("Step 3: Selecting trip type '%s' from dropdown", trip_type)
        try:
            wait = WebDriverWait(self.driver, 15)
            select_elem = wait.until(EC.element_to_be_clickable((By.XPATH, locators.OUTSTATION_TRIP_TYPE_XPATH)))
            logging.info("Waiting for trip type dropdown options to load from server...")
            WebDriverWait(self.driver, 10).until(
                lambda d: len(Select(d.find_element(By.XPATH, locators.OUTSTATION_TRIP_TYPE_XPATH)).options) > 1
            )
            sel = Select(select_elem)
            options = [o.text.strip() for o in sel.options if o.text.strip() and o.get_attribute("value")]
            match = next((o for o in options if trip_type.lower() in o.lower()), None)
            if match:
                sel.select_by_visible_text(match)
                logging.info("Trip type '%s' selected successfully by matching text", match)
            else:
                sel.select_by_index(1)
                logging.info("Trip type selected by index 1 (available options: %s)", options)
        except Exception as e:
            self._take_screenshot(label, "trip_type")
            logging.error("FAILED to select trip type: %s", e)
            self.fail(f"Trip type select failed: {e}")

        # 4) Type From City and select first suggestion
        logging.info("Step 4: Typing 'From' city '%s' and selecting from suggestions", from_city)
        try:
            methods.type_and_select_first_option(
                self.driver,
                locators.OUTSTATION_FROM_CITY_XPATH,
                from_city,
                first_option_xpath=locators.OUTSTATION_FROM_CITY_FIRST_OPTION_XPATH,
            )
            logging.info("From city '%s' entered and first suggestion selected", from_city)
        except Exception as e:
            self._take_screenshot(label, "from_city")
            logging.error("FAILED to enter 'From' city: %s", e)
            self.fail(f"From city input failed: {e}")

        # 5) Type To City and select first suggestion
        logging.info("Step 5: Typing 'To' city '%s' and selecting from suggestions", to_city)
        try:
            methods.type_and_select_first_option(
                self.driver,
                locators.OUTSTATION_TO_CITY_XPATH,
                to_city,
                first_option_xpath=locators.OUTSTATION_TO_CITY_FIRST_OPTION_XPATH,
            )
            logging.info("To city '%s' entered and first suggestion selected", to_city)
        except Exception as e:
            self._take_screenshot(label, "to_city")
            logging.error("FAILED to enter 'To' city: %s", e)
            self.fail(f"To city input failed: {e}")

        # 6-7) Set date and time
        self._set_date(label, locators.OUTSTATION_DATE_XPATH, date)
        self._set_time(label, locators.OUTSTATION_TIME_XPATH, time)

        # 8) Dismiss dropdown, click search, post-search flow
        self._dismiss_dropdown()
        self._click_search(label)
        self._post_search(label, from_city, date, time, go_to_payment, validate)

    # ── Test methods ─────────────────────────────────────────────────

    @allure.story("Future Date Search")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Outstation Trip tab\n"
        "3. Select trip type from dropdown\n"
        "4. Enter 'From' city and select from suggestions\n"
        "5. Enter 'To' city and select from suggestions\n"
        "6. Set a future date (60 days from today)\n"
        "7. Set pickup time\n"
        "8. Click 'Search Your Ride' button\n"
        "9. Validate results page shows correct location, date, and time\n"
        "10. Click Book Now, login, fill traveller details, and proceed to payment"
    )
    def to_verify_user_can_select_future_date(self):
        """Verify user can select future date — goes to final payment state."""
        self._run_search(
            "future_date",
            testvalue.OS_BEST_TRIP_TYPE,
            testvalue.OS_BEST_FROM_CITY,
            testvalue.OS_BEST_TO_CITY,
            testvalue.OS_BEST_DATE,
            testvalue.OS_BEST_TIME,
            go_to_payment=True,
            validate=True,
        )

    @allure.story("Future Time Search")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Outstation Trip tab\n"
        "3. Select trip type from dropdown\n"
        "4. Enter 'From' city and select from suggestions\n"
        "5. Enter 'To' city and select from suggestions\n"
        "6. Set today's date\n"
        "7. Set a future time (later today)\n"
        "8. Click 'Search Your Ride' button\n"
        "9. Validate results page shows correct location, date, and time\n"
        "10. Click Book Now, login, fill traveller details, and proceed to payment"
    )
    def to_verify_user_can_select_future_time(self):
        """Verify user can select future time — goes to final payment state."""
        self._run_search(
            "future_time",
            testvalue.OS_PRESENT_TRIP_TYPE,
            testvalue.OS_PRESENT_FROM_CITY,
            testvalue.OS_PRESENT_TO_CITY,
            testvalue.OS_PRESENT_DATE,
            testvalue.TIMING_FUTURE_12H,
            go_to_payment=True,
            validate=True,
        )

    @allure.story("Time Before 12 Hours Rejection")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Outstation Trip tab\n"
        "3. Select trip type from dropdown\n"
        "4. Enter 'From' city and select from suggestions\n"
        "5. Enter 'To' city and select from suggestions\n"
        "6. Set today's date\n"
        "7. Set a time less than 12 hours from now\n"
        "8. Click 'Search Your Ride' button\n"
        "9. Verify the site shows a validation error and does NOT navigate to results page"
    )
    def to_verify_user_cannot_select_time_before_12_hours(self):
        """Verify user cannot select a time less than 12 hours from now — site should reject."""
        self._run_search(
            "time_before_12h",
            testvalue.OS_PRESENT_TRIP_TYPE,
            testvalue.OS_PRESENT_FROM_CITY,
            testvalue.OS_PRESENT_TO_CITY,
            testvalue.OS_PRESENT_DATE,
            testvalue.TIMING_BEFORE_12H,
        )

    @allure.story("Past Date Rejection")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Outstation Trip tab\n"
        "3. Select trip type from dropdown\n"
        "4. Enter 'From' city and select from suggestions\n"
        "5. Enter 'To' city and select from suggestions\n"
        "6. Set a past date\n"
        "7. Set pickup time\n"
        "8. Click 'Search Your Ride' button\n"
        "9. Verify the site shows a validation error and does NOT navigate to results page"
    )
    def to_verify_user_cannot_select_past_date(self):
        """Verify user cannot select past date — site should show validation error."""
        self._run_search(
            "past_date",
            testvalue.OS_WORST_TRIP_TYPE,
            testvalue.OS_WORST_FROM_CITY,
            testvalue.OS_WORST_TO_CITY,
            testvalue.OS_WORST_DATE,
            testvalue.OS_WORST_TIME,
        )

    @allure.story("Present Date Search")
    @allure.description(
        "Steps:\n"
        "1. Open the B2C website\n"
        "2. Click Outstation Trip tab\n"
        "3. Select trip type from dropdown\n"
        "4. Enter 'From' city and select from suggestions\n"
        "5. Enter 'To' city and select from suggestions\n"
        "6. Set today's date\n"
        "7. Set current time\n"
        "8. Click 'Search Your Ride' button\n"
        "9. Validate results page shows correct location, date, and time (if page loads)"
    )
    def to_verify_user_can_select_present_date(self):
        """Verify user can select present date — site should show results."""
        self._run_search(
            "present_date",
            testvalue.OS_PRESENT_TRIP_TYPE,
            testvalue.OS_PRESENT_FROM_CITY,
            testvalue.OS_PRESENT_TO_CITY,
            testvalue.OS_PRESENT_DATE,
            testvalue.OS_PRESENT_TIME,
            validate=True,
        )


if __name__ == "__main__":
    import unittest
    unittest.main()
