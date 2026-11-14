
import unittest
import subprocess
import sys
import tempfile
import hashlib
from pathlib import Path


APP = Path(__file__).resolve().parents[1] / "hash_app.py"


class HashAppTests(unittest.TestCase):

    # Test 1: Hashing and main bucket creation
    def test_hashing_and_bucket_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.run_app(
                folder, 5, 20, "Hello\nWorld\nTest\n"
            )

            expected = {i: "" for i in range(1, 6)}

            for word in ["Hello", "World", "Test"]:
                digest = hashlib.blake2b(
                    word.encode("utf-8"),
                    digest_size=8
                ).digest()

                remainder = int.from_bytes(digest, "big") % 5
                bucket = remainder if remainder else 5
                expected[bucket] += word

            for i in range(1, 6):
                file = root / f"{i}.txt"

                self.assertTrue(file.exists())
                self.assertEqual(
                    file.read_text(encoding="utf-8"),
                    expected[i]
                )

    # Test 2: Overflow bucket creation
    def test_overflow_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.run_app(
                folder, 1, 5, "Hello\nWorld\nTest\n"
            )

            self.assertEqual(
                (root / "1.txt").read_text(
                    encoding="utf-8"
                ),
                "Hello"
            )

            self.assertEqual(
                (root / "1_overflow_1.txt").read_text(
                    encoding="utf-8"
                ),
                "World"
            )

            self.assertEqual(
                (root / "1_overflow_2.txt").read_text(
                    encoding="utf-8"
                ),
                "Test"
            )

            links = (root / "1.links").read_text(
                encoding="utf-8"
            ).splitlines()

            self.assertEqual(
                links,
                [
                    "1_overflow_1.txt",
                    "1_overflow_2.txt"
                ]
            )

    # Test 3: Long strings and partial capacity
    def test_long_string_and_partial_capacity(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.run_app(
                folder, 1, 4, "AB\nCDEFGHIJ\n"
            )

            self.assertEqual(
                (root / "1.txt").read_text(
                    encoding="utf-8"
                ),
                "ABCD"
            )

            self.assertEqual(
                (root / "1_overflow_1.txt").read_text(
                    encoding="utf-8"
                ),
                "EFGH"
            )

            self.assertEqual(
                (root / "1_overflow_2.txt").read_text(
                    encoding="utf-8"
                ),
                "IJ"
            )

    # Test 4: Continue writing after restart
    def test_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            self.run_app(
                folder, 1, 5, "Hello\nWorld\nTest\n"
            )

            root = self.run_app(
                folder, 1, 5, "!\n"
            )

            self.assertEqual(
                (root / "1_overflow_2.txt").read_text(
                    encoding="utf-8"
                ),
                "Test!"
            )

            self.assertFalse(
                (root / "1_overflow_3.txt").exists()
            )

    # Test 5: Unicode characters
    def test_unicode(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.run_app(
                folder, 1, 3, "Ağsu 🙂\n"
            )

            first = (root / "1.txt").read_text(
                encoding="utf-8"
            )

            second = (root / "1_overflow_1.txt").read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                first + second,
                "Ağsu 🙂"
            )

            self.assertLessEqual(len(first), 3)
            self.assertLessEqual(len(second), 3)

    # Test 6: Invalid command-line parameters
    def test_invalid_parameters(self):
        with tempfile.TemporaryDirectory() as folder:
            for n, s in [
                (0, 5),
                (2, 0),
                (-1, 5),
                ("abc", 5)
            ]:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(APP),
                        str(n),
                        str(s)
                    ],
                    capture_output=True,
                    text=True,
                    cwd=folder
                )

                self.assertNotEqual(
                    result.returncode,
                    0
                )

    # Helper function used by the tests
    def run_app(self, folder, n, s, inputs):
        result = subprocess.run(
            [
                sys.executable,
                "-X",
                "utf8",
                str(APP),
                str(n),
                str(s)
            ],
            input=inputs,
            text=True,
            capture_output=True,
            encoding="utf-8",
            cwd=folder
        )

        self.assertEqual(
            result.returncode,
            0,
            result.stderr
        )

        return Path(folder)


if __name__ == "__main__":
    unittest.main()
