# main.py
# Runs all test suites: Airport Transfer Pickup, Drop, Local Rental,
# Outstation Trip, Login Home, Login BookNow, Modify Search.

import unittest

from test_suites.Airport_Transfer_pick import TestAirportTransferPickup
from test_suites.Airport_Transfer_Drop import TestAirportTransferDrop
from test_suites.Local_Rental import TestLocalRental
from test_suites.Outstation_Trip import TestOutstationTrip
from test_suites.Login_Home import TestLoginHome
from test_suites.Login_BookNow import TestLoginBookNow
from test_suites.Modify_Search import TestModifySearch

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAirportTransferPickup))
    suite.addTests(loader.loadTestsFromTestCase(TestAirportTransferDrop))
    suite.addTests(loader.loadTestsFromTestCase(TestLocalRental))
    suite.addTests(loader.loadTestsFromTestCase(TestOutstationTrip))
    suite.addTests(loader.loadTestsFromTestCase(TestLoginHome))
    suite.addTests(loader.loadTestsFromTestCase(TestLoginBookNow))
    suite.addTests(loader.loadTestsFromTestCase(TestModifySearch))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
