
# hash_app — File-Based Hash Bucket System

## Project Description

hash_app is a Python application that stores input strings
in hash bucket files using a deterministic hashing algorithm.

The application supports:
- Command-line parameters for bucket count and capacity
- Hash-based string distribution
- Multiple strings in the same bucket
- Overflow bucket creation
- Overflow file referencing
- Persistent storage across restarts
- Continuous user input until Ctrl+C

## Requirements

- Python 3.8 or newer
- No external Python libraries required

## How to Run

Windows:

    py hash_app.py 5 20

Linux/macOS:

    ./hash_app 5 20

Alternatively:

    python3 hash_app.py 5 20

Parameters:
- n: Number of main buckets
- s: Maximum number of characters per bucket file

Example:

    py hash_app.py 5 20

This creates five files: 1.txt through 5.txt.
Each file has a maximum capacity of 20 characters.

## Hashing Algorithm

The application uses BLAKE2b from Python's built-in
hashlib library with digest_size=8.

1. Encode the input string using UTF-8.
2. Calculate its BLAKE2b digest.
3. Convert the digest to an integer.
4. Calculate the remainder using modulo n.
5. Map remainder 0 to bucket n.

BLAKE2b provides deterministic hashing, so identical
strings are assigned to the same main bucket.

## Bucket Storage

Strings are appended directly without separators.

Example:

    HelloWorldTest

No commas, spaces, or newlines are automatically added.

## Overflow Bucket Management

Every bucket file has a maximum capacity of s characters.

When the current file is full, the application creates
an overflow file.

Example:

    1.txt
    1_overflow_1.txt
    1_overflow_2.txt

The program writes to the current file until it is full,
then continues in the next overflow file.

Long strings may be split between multiple bucket files.

## Overflow Reference Method

The program uses a separate .links metadata file.

Example:

    1.links

Contents:

    1_overflow_1.txt
    1_overflow_2.txt

Each line records an overflow filename in creation order.

The application reads the last entry to locate the most
recent overflow file.

This allows the program to continue writing after
restarting with the same configuration.

## Testing

Run automated tests from the project root:

    py -m unittest discover -s tests -v

Tests cover hashing, overflow, partial capacity,
restarting, Unicode input, and invalid arguments.

## Notes

- Empty input is ignored.
- Ctrl+C stops the application.
- Generated bucket files are excluded from Git.
- Run tests in isolated temporary directories.
- Use a clean data directory when changing n or s,
  because existing bucket data may have been created
  with another capacity or bucket count.
