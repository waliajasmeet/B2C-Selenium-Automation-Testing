# locators.py
# ONLY locators + URL. Replace placeholders with real XPATHs.

URL = "https://b2c.ecoserp.in/"

# Airport Transfer tab (click if not active)
AIRPORT_TRANSFER_TAB_XPATH = '//*[@id="myTab"]/li[1]/a/img[2]'

# Drop To Airport
DROP_TO_AIRPORT_XPATH = '//*[@id="first"]/form/div[1]/div[1]/div/select/option[1]'
# Template or strategy to select option by visible text/value (we'll format with .format(value) in code)
DROP_TO_AIRPORT_OPTION_XPATH_TEMPLATE = '//*[@id="first"]/form/div[1]/div[1]/div/select/option[1]'

# Drop Airport/City input and first suggestion
DROP_AIRPORT_CITY_XPATH = '//*[@id="first"]/form/div[1]/div[2]/div/input'
DROP_AIRPORT_CITY_FIRST_OPTION_XPATH = '//*[@id="first"]/form/div[1]/div[2]/div/ul/li[1]'

# Pickup date field (input or widget)
PICKUP_DATE_XPATH = '//*[@id="pickup_date1"]'

# Start time field (input or widget)
START_TIME_XPATH = '//*[@id="first"]/form/div[1]/div[4]/div'

# Search button
SEARCH_RIDE_BUTTON_XPATH = '//*[@id="first"]/form/div[2]/button'

# Results validation
RESULTS_CONTAINER_XPATH = '//*[@id="root"]/main/section[1]'
RESULTS_PAGE_UNIQUE_XPATH = "//button[contains(text(),'Modify')]"

# Optional: no rides message
NO_RIDES_MESSAGE_XPATH = "//*[contains(text(),'No rides') or contains(text(),'no rides') or contains(text(),'No results')]"

# Book Now button - template: finds Book Now next to the chosen car name
# {} will be replaced with car name from testdata.BOOK_CAR_NAME
BOOK_NOW_BUTTON_XPATH_TEMPLATE = "//div[@class='car-title'][contains(text(),'{}')]/ancestor::div[contains(@class,'row')]//button[@class='book-now-btn']"

# Fallback: first Book Now button if car name not found
BOOK_NOW_BUTTON_FALLBACK_XPATH = "(//button[contains(text(),'Book Now')])[1]"

# Sign In with OTP page
MOBILE_NUMBER_INPUT_XPATH = "//input[@placeholder='Enter mobile number']"
SEND_OTP_BUTTON_XPATH = "//button[contains(text(),'SEND OTP')]"

# OTP verification
OTP_INPUT_XPATH = "//input[@placeholder='Enter 6-digit OTP']"
VERIFY_OTP_BUTTON_XPATH = "//button[contains(text(),'VERIFY OTP')]"

# Booking form - Traveller Details
LAST_NAME_XPATH = "//input[@placeholder='Last Name']"

# Booking form - Pick-Up / Drop
PICKUP_LOCATION_XPATH = '//*[@id="pickupLocation"]'
PICKUP_ADDRESS_XPATH = '//*[@id="pickupAddress"]'

# T&C checkbox
TNC_CHECKBOX_XPATH = "//label[@class='custom-checkbox mt-3']/input[@type='checkbox']"

# Pay button
PAY_BUTTON_XPATH = "//button[contains(text(),'Pay')]"
