import unittest

from Sources.quantity import import_quantity


class QuantityTests(unittest.TestCase):
    def test_imports_positive_quantity(self):
        self.assertEqual(import_quantity({"value": 5}), 5)


if __name__ == "__main__":
    unittest.main()
