import sys
import hashlib
from pathlib import Path


def get_bucket(text, n):
    # Convert input text to a hash number
    hash_bytes = hashlib.blake2b(
        text.encode("utf-8"),
        digest_size=8
    ).digest()

    hash_number = int.from_bytes(hash_bytes, "big")

    # Select a bucket numbered from 1 to n
    remainder = hash_number % n
    return remainder if remainder != 0 else n


def main():
    # Check command-line arguments
    if len(sys.argv) != 3:
        print("Usage: hash_app n s")
        return

    try:
        n = int(sys.argv[1])
        s = int(sys.argv[2])

        if n <= 0 or s <= 0:
            raise ValueError
    except ValueError:
        print("n and s must be positive integers.")
        return

    # Create the main bucket files
    for i in range(1, n + 1):
        Path(f"{i}.txt").touch(exist_ok=True)

    # Continuously receive strings
    try:
        while True:
            text = input("Please enter the string: ")

            if text == "":
                continue

            bucket = get_bucket(text, n)
            filename = f"{bucket}.txt"

            with open(filename, "a", encoding="utf-8") as file:
                file.write(text)

            print(f"{text} added to {filename}")

    except (KeyboardInterrupt, EOFError):
        print("\nProgram stopped.")


if __name__ == "__main__":
    main()
