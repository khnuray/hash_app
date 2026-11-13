
import sys
import hashlib
from pathlib import Path


# Find the bucket for a given string
def get_bucket(text, n):
    digest = hashlib.blake2b(
        text.encode("utf-8"),
        digest_size=8
    ).digest()

    hash_number = int.from_bytes(digest, "big")
    remainder = hash_number % n

    return remainder if remainder != 0 else n


# Create bucket files
def initialize_buckets(n):
    for i in range(1, n + 1):
        Path(f"{i}.txt").touch(exist_ok=True)


# Get the last file of a bucket
def get_last_file(bucket):
    links_file = Path(f"{bucket}.links")

    if links_file.exists():
        links = [
            line
            for line in links_file.read_text(
                encoding="utf-8"
            ).splitlines()
            if line
        ]
    else:
        links = []

    if links:
        return Path(links[-1]), len(links) + 1

    return Path(f"{bucket}.txt"), 1


# Save strings and handle overflow
def store_string(text, n, s):
    bucket = get_bucket(text, n)

    current_file, next_number = get_last_file(bucket)

    remaining = text

    while remaining:
        current_size = len(
            current_file.read_text(encoding="utf-8")
        )

        available = s - current_size

        # Create another file if the bucket is full
        if available <= 0:
            current_file = Path(
                f"{bucket}_overflow_{next_number}.txt"
            )

            current_file.touch(exist_ok=False)

            # Save the new file name
            links_file = Path(f"{bucket}.links")

            with links_file.open(
                "a", encoding="utf-8"
            ) as links:
                links.write(current_file.name + "\n")

            next_number += 1
            continue

        # Write as much as the file can hold
        part = remaining[:available]

        with current_file.open(
            "a", encoding="utf-8", newline=""
        ) as file:
            file.write(part)

        remaining = remaining[len(part):]

    return bucket


# Run the program
def main():
    if len(sys.argv) != 3:
        print("Usage: hash_app n s")
        return 1

    try:
        n = int(sys.argv[1])
        s = int(sys.argv[2])

        if n <= 0 or s <= 0:
            raise ValueError

    except ValueError:
        print("n and s must be positive integers.")
        return 1

    initialize_buckets(n)

    try:
        while True:
            text = input("Please enter the string: ")

            if text == "":
                continue

            bucket = store_string(text, n, s)

            print(f"{text} added to {bucket}.txt")

    except (KeyboardInterrupt, EOFError):
        print("\nProgram stopped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
