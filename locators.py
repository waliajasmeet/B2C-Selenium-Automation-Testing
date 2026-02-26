# locators.py
# ONLY locators + URL. Replace placeholders with real XPATHs.

URL = "https://b2c.ecoserp.in/"

# ════════════════════════════════════════════════════════════════
# TAB SELECTORS
# ════════════════════════════════════════════════════════════════

AIRPORT_TRANSFER_TAB_XPATH = '//*[@id="myTab"]/li[1]/a/img[2]'
LOCAL_RENTAL_TAB_XPATH = '//*[@id="myTab"]/li[2]'
OUTSTATION_TRIP_TAB_XPATH = '//*[@id="myTab"]/li[3]'
SELF_DRIVE_TAB_XPATH = '//*[@id="myTab"]/li[4]/a'

# ════════════════════════════════════════════════════════════════
# AIRPORT TRANSFER
# ════════════════════════════════════════════════════════════════

# Direction dropdown
DIRECTION_SELECT_XPATH = '//*[@id="first"]/form/div[1]/div[1]/div/select'
DIRECTION_OPTION_XPATH_TEMPLATE = (
    '//*[@id="first"]/form/div[1]/div[1]/div/select/option['
    'translate(normalize-space(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="{0}"]'
)

# Airport/City input and first suggestion
AIRPORT_CITY_XPATH = '//*[@id="first"]/form/div[1]/div[2]/div/input'
AIRPORT_CITY_FIRST_OPTION_XPATH = '//*[@id="first"]/form/div[1]/div[2]/div/ul/li[1]'

# Date, Time, Search
AIRPORT_DATE_XPATH = '//*[@id="pickup_date1"]'
AIRPORT_TIME_XPATH = '//*[@id="first"]/form/div[1]/div[4]/div'
AIRPORT_SEARCH_BUTTON_XPATH = '//*[@id="first"]/form/div[2]/button'

# Booking form — Pickup From Airport
FLIGHT_NO_XPATH = "//input[@placeholder='Enter Flight No.']"
DROP_ADDRESS_XPATH = "//input[@placeholder='Enter Drop Address']"

# Booking form — Drop To Airport
PICKUP_LOCATION_XPATH = '//*[@id="pickupLocation"]'
PICKUP_ADDRESS_XPATH = '//*[@id="pickupAddress"]'

# ════════════════════════════════════════════════════════════════
# LOCAL RENTAL
# ════════════════════════════════════════════════════════════════

LOCAL_RENTAL_CITY_XPATH = '//*[@id="second"]/form/div[1]/div[1]/div/input'
LOCAL_RENTAL_CITY_FIRST_OPTION_XPATH = '//*[@id="second"]/form/div[1]/div[1]/div/ul/li[1]'

LOCAL_RENTAL_PACKAGE_XPATH = '//*[@id="second"]/form/div[1]/div[2]/div/select'
LOCAL_RENTAL_PACKAGE_OPTION_XPATH_TEMPLATE = (
    '//*[@id="second"]/form/div[1]/div[2]/div/select/option['
    'translate(normalize-space(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="{0}"]'
)

LOCAL_RENTAL_DATE_XPATH = '//*[@id="pickup_date2"]'
LOCAL_RENTAL_TIME_XPATH = '//*[@id="second"]/form/div[1]/div[4]/div'
LOCAL_RENTAL_SEARCH_BUTTON_XPATH = '//*[@id="second"]/form/div[2]/button'

# ════════════════════════════════════════════════════════════════
# OUTSTATION TRIP
# ════════════════════════════════════════════════════════════════

# Trip Type dropdown
OUTSTATION_TRIP_TYPE_XPATH = '//*[@id="third"]/form/div[1]/div[1]/div/select'
OUTSTATION_TRIP_TYPE_OPTION_XPATH_TEMPLATE = (
    '//*[@id="third"]/form/div[1]/div[1]/div/select/option['
    'translate(normalize-space(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="{0}"]'
)

# From City input and first suggestion
OUTSTATION_FROM_CITY_XPATH = '//*[@id="third"]/form/div[1]/div[2]/div/input'
OUTSTATION_FROM_CITY_FIRST_OPTION_XPATH = '//*[@id="third"]/form/div[1]/div[2]/div/ul/li[1]'

# To City input and first suggestion
OUTSTATION_TO_CITY_XPATH = '//*[@id="third"]/form/div[1]/div[3]/div/input'
OUTSTATION_TO_CITY_FIRST_OPTION_XPATH = '//*[@id="third"]/form/div[1]/div[3]/div/ul/li[1]'

# Date, Time, Search
OUTSTATION_DATE_XPATH = '//*[@id="pickup_date"]'
OUTSTATION_TIME_XPATH = '//*[@id="third"]/form/div[1]/div[5]/div'
OUTSTATION_SEARCH_BUTTON_XPATH = '//*[@id="third"]/form/div[2]/button'

# ════════════════════════════════════════════════════════════════
# SELF DRIVE  (query form — no search/book/OTP/pay flow)
# ════════════════════════════════════════════════════════════════

SELF_DRIVE_NAME_XPATH = '//*[@id="fourth"]/form/div[1]/div[1]/div/input'
SELF_DRIVE_MOBILE_XPATH = '//*[@id="fourth"]/form/div[1]/div[2]/div/input'
SELF_DRIVE_EMAIL_XPATH = '//*[@id="fourth"]/form/div[1]/div[3]/div/input'
SELF_DRIVE_CITY_XPATH = '//*[@id="fourth"]/form/div[1]/div[4]/div/input'
SELF_DRIVE_VEHICLE_TYPE_XPATH = '//*[@id="fourth"]/form/div[1]/div[5]/div/input'
SELF_DRIVE_TRAVEL_DATE_XPATH = '//*[@id="travel_date"]'
SELF_DRIVE_NO_OF_DAYS_XPATH = '//*[@id="fourth"]/form/div[1]/div[7]/div/input'
SELF_DRIVE_SUBMIT_BUTTON_XPATH = '//*[@id="fourth"]/form/div[2]/button'

# ════════════════════════════════════════════════════════════════
# COMMON (Results, Book Now, OTP, Booking form, Payment)
# ════════════════════════════════════════════════════════════════

# Results validation
RESULTS_CONTAINER_XPATH = '//*[@id="root"]/main/section[1]'
RESULTS_PAGE_UNIQUE_XPATH = "//button[contains(text(),'Modify')]"
NO_RIDES_MESSAGE_XPATH = "//*[contains(text(),'No rides') or contains(text(),'no rides') or contains(text(),'No results')]"

# Book Now button (case-insensitive car name match)
BOOK_NOW_BUTTON_XPATH_TEMPLATE = (
    "//div[@class='car-title']"
    "[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{0}')]"
    "/ancestor::div[contains(@class,'row')]//button[@class='book-now-btn']"
)
BOOK_NOW_BUTTON_FALLBACK_XPATH = "(//button[contains(text(),'Book Now')])[1]"

# Sign In with OTP
MOBILE_NUMBER_INPUT_XPATH = "//input[@placeholder='Enter mobile number']"
SEND_OTP_BUTTON_XPATH = "//button[contains(text(),'SEND OTP')]"
OTP_INPUT_XPATH = "//input[@placeholder='Enter 6-digit OTP']"
VERIFY_OTP_BUTTON_XPATH = "//button[contains(text(),'VERIFY OTP')]"

# Booking form
LAST_NAME_XPATH = "//input[@placeholder='Last Name']"

# T&C and Pay
TNC_CHECKBOX_XPATH = "//label[@class='custom-checkbox mt-3']/input[@type='checkbox']"
PAY_BUTTON_XPATH = "//button[contains(text(),'Pay')]"
