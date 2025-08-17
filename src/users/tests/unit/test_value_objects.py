from __future__ import annotations

from django.test import SimpleTestCase

from src.users.domain.value_objects import Email, PasswordHash


class EmailValueObjectTests(SimpleTestCase):
    def test_valid_email(self):
        e = Email("john.doe@example.com")
        self.assertEqual(str(e), "john.doe@example.com")

    def test_invalid_email(self):
        for v in ["", "john", "john@", "@example.com", "john@com", "john@@example.com", "john@example"]:
            with self.assertRaises(ValueError):
                Email(v)


class PasswordHashValueObjectTests(SimpleTestCase):
    def test_valid_hash(self):
        h = PasswordHash("x" * 40)
        self.assertEqual(str(h), "x" * 40)

    def test_invalid_hash(self):
        with self.assertRaises(ValueError):
            PasswordHash("")
        with self.assertRaises(ValueError):
            PasswordHash("short")
