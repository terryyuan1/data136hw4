import hashlib
import random
'''Code to inefficiently and ineffectively scramble a source
text that requires a little bit of programming to brute force.
'''

# The 9-digit key that was used to generate the hashes
puzzle_key = 485066843  # Integer value, not a string

# The misspelled word that couldn't be decoded
# This is the misspelling of "waiting"
puzzle_misspell = "wkitpng"  # Just the exact string, no quotes in the value

# For easy testing
puzzle_easy_key = 6346  # Integer value
puzzle_easy_misspell = "18th"  # Date from the decoded message

# The code below is commented out because it attempts to access files that may not exist in all environments
# Uncomment if needed and if the TEXT file exists in your environment
'''
words = open("TEXT", "r").read()
with open("PUZZLE", "w") as puzzle:
    for word in words.split():
        puzzle.write(
            hashlib.md5(str(puzzle_key).encode("utf-8") +
            word.encode("utf-8")).hexdigest() + "\n"
            )
'''
