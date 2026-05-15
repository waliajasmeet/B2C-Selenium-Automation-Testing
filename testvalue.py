# testvalue.py
# Test values for all test cases (best case, worst case, present date).

from datetime import datetime, timedelta

# ════════════════════════════════════════════════════════════════
# AIRPORT TRANSFER — PICKUP FROM AIRPORT
# ════════════════════════════════════════════════════════════════

# ── Best case ─────────────────────────────────────────────────
BEST_DIRECTION = "pickup from airport"
BEST_CITY      = "Bengaluru"
BEST_DATE      = (datetime.today() + timedelta(days=60)).strftime("%d-%m-%Y")  # 60 days from today
BEST_TIME      = "10:30 AM"

# ── Worst case ────────────────────────────────────────────────
WORST_DIRECTION = "pickup from airport"
WORST_CITY      = "Bengaluru"            # Empty city — missing required field
WORST_DATE      = "01-01-2020"  # Past date
WORST_TIME      = "10:30 AM"    # Same as best case — only date differs

# ── Present date case ─────────────────────────────────────────
PRESENT_DIRECTION = "pickup from airport"
PRESENT_CITY      = "Bengaluru"
PRESENT_DATE      = datetime.today().strftime("%d-%m-%Y")  # Today's date
PRESENT_TIME      = "10:30 AM"

# ════════════════════════════════════════════════════════════════
# AIRPORT TRANSFER — DROP TO AIRPORT
# ════════════════════════════════════════════════════════════════

# ── Best case ─────────────────────────────────────────────────
DROP_BEST_DIRECTION = "drop to airport"
DROP_BEST_CITY      = "Bengaluru"
DROP_BEST_DATE      = (datetime.today() + timedelta(days=60)).strftime("%d-%m-%Y")  # 60 days from today
DROP_BEST_TIME      = "10:30 AM"

# ── Worst case ────────────────────────────────────────────────
DROP_WORST_DIRECTION = "drop to airport"
DROP_WORST_CITY      = "Bengaluru"
DROP_WORST_DATE      = "01-01-2020"  # Past date
DROP_WORST_TIME      = "10:30 AM"

# ── Present date case ─────────────────────────────────────────
DROP_PRESENT_DIRECTION = "drop to airport"
DROP_PRESENT_CITY      = "Bengaluru"
DROP_PRESENT_DATE      = datetime.today().strftime("%d-%m-%Y")  # Today's date
DROP_PRESENT_TIME      = "10:30 AM"

# ════════════════════════════════════════════════════════════════
# LOCAL RENTAL
# ════════════════════════════════════════════════════════════════

# ── Best case ─────────────────────────────────────────────────
LR_BEST_CITY    = "Bengaluru"
LR_BEST_PACKAGE = "8 Hrs / 80 Kms"
LR_BEST_DATE    = (datetime.today() + timedelta(days=60)).strftime("%d-%m-%Y")  # 60 days from today
LR_BEST_TIME    = "10:30 AM"

# ── Worst case ────────────────────────────────────────────────
LR_WORST_CITY    = "Bengaluru"
LR_WORST_PACKAGE = "8 Hrs / 80 Kms"
LR_WORST_DATE    = "01-01-2020"  # Past date
LR_WORST_TIME    = "10:30 AM"

# ── Present date case ─────────────────────────────────────────
LR_PRESENT_CITY    = "Bengaluru"
LR_PRESENT_PACKAGE = "8 Hrs / 80 Kms"
LR_PRESENT_DATE    = datetime.today().strftime("%d-%m-%Y")  # Today's date
LR_PRESENT_TIME    = "10:30 AM"

# ════════════════════════════════════════════════════════════════
# OUTSTATION TRIP
# ════════════════════════════════════════════════════════════════

# ── Best case ─────────────────────────────────────────────────
OS_BEST_TRIP_TYPE  = "one way"
OS_BEST_FROM_CITY  = "Delhi"
OS_BEST_TO_CITY    = "Mumbai"
OS_BEST_DATE       = (datetime.today() + timedelta(days=60)).strftime("%d-%m-%Y")  # 60 days from today
OS_BEST_TIME       = "10:30 AM"

# ── Worst case ────────────────────────────────────────────────
OS_WORST_TRIP_TYPE  = "one way"
OS_WORST_FROM_CITY  = "Bengaluru"
OS_WORST_TO_CITY    = "Mumbai"
OS_WORST_DATE       = "01-01-2020"  # Past date
OS_WORST_TIME       = "10:30 AM"

# ── Present date case ─────────────────────────────────────────
OS_PRESENT_TRIP_TYPE  = "one way"
OS_PRESENT_FROM_CITY  = "Bengaluru"
OS_PRESENT_TO_CITY    = "Mumbai"
OS_PRESENT_DATE       = datetime.today().strftime("%d-%m-%Y")  # Today's date
OS_PRESENT_TIME       = "10:30 AM"

# ════════════════════════════════════════════════════════════════
# LOGIN
# ════════════════════════════════════════════════════════════════

# ── Valid login ─────────────────────────────────────────────────
LOGIN_VALID_MOBILE   = "6239677566"
LOGIN_VALID_OTP      = "111111"
LOGIN_EXPECTED_NICKNAME = "nik"

# ── Invalid mobile ──────────────────────────────────────────────
LOGIN_INVALID_MOBILE = "0000000000"
LOGIN_INVALID_OTP    = "111111"

# ── Invalid OTP ─────────────────────────────────────────────────
LOGIN_WRONG_OTP_MOBILE = "6239677566"
LOGIN_WRONG_OTP        = "999999"

# ── Validation: mobile min/max digits ─────────────────────────
LOGIN_MOBILE_SHORT     = "62396"              # 5 digits — below minimum, should fail
LOGIN_MOBILE_OVERFLOW  = "62396775661234"     # 14 digits — only 10 should be accepted
LOGIN_MOBILE_ALPHA     = "abcd623967"         # alphabets mixed — should be rejected

# ── Validation: OTP min/max 6 digits ─────────────────────────
LOGIN_OTP_SHORT           = "111"             # 3 digits — below minimum, should fail
LOGIN_OTP_OVERFLOW        = "11111199999"     # 11 digits — only 6 should be accepted
LOGIN_OTP_ALPHA           = "abc123"          # alphabets mixed — should be rejected
LOGIN_OTP_ALPHA_MOBILE    = "6239677566"      # mobile for OTP alphabet test (separate to avoid rate limit)

# ════════════════════════════════════════════════════════════════
# TRAVELLER DETAILS (Booking form after Book Now + Login)
# ════════════════════════════════════════════════════════════════

TRAVELLER_FIRST_NAME     = "Test"
TRAVELLER_LAST_NAME      = "User"
TRAVELLER_MOBILE         = "6239677566"
TRAVELLER_EMAIL          = "testuser@gmail.com"
TRAVELLER_PICKUP_LOCATION = "Delhi"
TRAVELLER_PICKUP_ADDRESS  = "123 Main Street, New Delhi"
TRAVELLER_FLIGHT_NO       = "AI-202"

# ════════════════════════════════════════════════════════════════
# MODIFY SEARCH (change values after initial search)
# ════════════════════════════════════════════════════════════════

MODIFY_CITY = "Delhi"
MODIFY_DATE = (datetime.today() + timedelta(days=90)).strftime("%d-%m-%Y")
MODIFY_TIME = "2:30 PM"

# Airport Transfer Drop — modify values
MODIFY_DROP_DIRECTION = "drop to airport"
MODIFY_DROP_CITY      = "Delhi"
MODIFY_DROP_DATE      = (datetime.today() + timedelta(days=90)).strftime("%d-%m-%Y")
MODIFY_DROP_TIME      = "2:30 PM"

# Local Rental — modify values
MODIFY_LR_CITY    = "Delhi"
MODIFY_LR_PACKAGE = "12 Hrs / 120 Kms"
MODIFY_LR_DATE    = (datetime.today() + timedelta(days=90)).strftime("%d-%m-%Y")
MODIFY_LR_TIME    = "2:30 PM"

# Outstation Trip — modify values
MODIFY_OS_FROM_CITY = "Bengaluru"
MODIFY_OS_TO_CITY   = "Jaipur"
MODIFY_OS_DATE      = (datetime.today() + timedelta(days=90)).strftime("%d-%m-%Y")
MODIFY_OS_TIME      = "2:30 PM"

# ════════════════════════════════════════════════════════════════
# TIMING TEST VALUES (shared across all suites)
# ════════════════════════════════════════════════════════════════

_now = datetime.now()
TIMING_PRESENT = _now.strftime("%I:%M %p").lstrip("0")          # Current time e.g. "3:45 PM"
TIMING_BEFORE_12H = (_now + timedelta(hours=2)).strftime("%I:%M %p").lstrip("0")   # +2 hours (within 12h window, should be rejected)
TIMING_FUTURE_12H = "11:55 PM"  # Fixed future time in PM
