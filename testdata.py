# testdata.py
# ONLY input/test values. Replace placeholders with real test data.
# All text values are CASE-INSENSITIVE — type in any case you want.

# ════════════════════════════════════════════════════════════════
# STEP 1 — Choose which service to test (case does NOT matter)
# ════════════════════════════════════════════════════════════════
# Options:  "Airport Transfer"  |  "Local Rental"  |  "Outstation Trip"  |  "Self Drive"

SERVICE_TYPE = "Self Drive"

# ════════════════════════════════════════════════════════════════
# COMMON (used across all service types)
# ════════════════════════════════════════════════════════════════

MOBILE_NUMBER = "6239677566"
OTP_VALUE = "111111"

# ────────────────────────────────────────────────────────────────
# AIRPORT TRANSFER
# ────────────────────────────────────────────────────────────────

# Direction: "Drop To Airport" or "Pickup From Airport"
AIRPORT_DIRECTION = "pickup from airport"

AIRPORT_CITY = "Bengaluru"
AIRPORT_DATE = "28-04-2026"
AIRPORT_TIME = "10:30 AM"
AIRPORT_CAR_NAME = "Toyota Innova Crysta"
AIRPORT_LAST_NAME = "test"

# Pickup From Airport fields
PICKUP_FLIGHT_NO = "AI-101"
PICKUP_DROP_ADDRESS = "MG Road, Bengaluru"

# Drop To Airport fields
DROP_PICKUP_LOCATION = "Bengaluru"
DROP_PICKUP_ADDRESS = "MG Road, Bengaluru"

# ────────────────────────────────────────────────────────────────
# LOCAL RENTAL
# ────────────────────────────────────────────────────────────────

LOCAL_RENTAL_CITY = "Delhi"
LOCAL_RENTAL_PACKAGE = "8 Hrs / 80 Kms"
LOCAL_RENTAL_DATE = "28-04-2026"
LOCAL_RENTAL_TIME = "10:30 AM"
LOCAL_RENTAL_CAR_NAME = "Toyota Innova Crysta"
LOCAL_RENTAL_LAST_NAME = "test"
LOCAL_RENTAL_PICKUP_ADDRESS = "MG Road, Delhi"

# ────────────────────────────────────────────────────────────────
# OUTSTATION TRIP
# ────────────────────────────────────────────────────────────────

# Trip Type: "One Way" or "Round Trip"
OUTSTATION_TRIP_TYPE = "One Way"

OUTSTATION_FROM_CITY = "Delhi"
OUTSTATION_TO_CITY = "Jaipur"
OUTSTATION_DATE = "28-04-2026"
OUTSTATION_TIME = "10:30 AM"
OUTSTATION_CAR_NAME = "Toyota Innova Crysta"
OUTSTATION_LAST_NAME = "test"
OUTSTATION_PICKUP_ADDRESS = "MG Road, Delhi"

# ────────────────────────────────────────────────────────────────
# SELF DRIVE  (query form — just fills and submits, no booking flow)
# ────────────────────────────────────────────────────────────────

SELF_DRIVE_NAME = "Happy"
SELF_DRIVE_MOBILE = "6239677566"
SELF_DRIVE_EMAIL = "happytechsapphire@gmail.com"
SELF_DRIVE_CITY = "Delhi"
SELF_DRIVE_VEHICLE_TYPE = "SUV"
SELF_DRIVE_TRAVEL_DATE = "28-04-2026"
SELF_DRIVE_NO_OF_DAYS = "3"
