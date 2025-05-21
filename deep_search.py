import hashlib
import re
import string
import itertools
from datetime import datetime

def calculate_hash(key, word):
    """Calculate MD5 hash of key + word"""
    key_encoded = str(key).encode('utf-8')
    word_encoded = word.encode('utf-8')
    hash_val = hashlib.md5(key_encoded + word_encoded).hexdigest()
    return hash_val

def load_hashes(puzzle_file):
    """Load all hash values from the puzzle file"""
    with open(puzzle_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def try_date_words(key, hashes_list, hash_set):
    """Try all months and days of the week with variations"""
    month_names = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]
    
    day_names = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ]
    
    # Try normal months and days
    for word in month_names + day_names:
        hash_val = calculate_hash(key, word)
        if hash_val in hash_set:
            pos = hashes_list.index(hash_val) + 1
            print(f"MATCH for '{word}': {hash_val} (position {pos})")
    
    # Focus on February since we know that's the likely word
    base_word = "February"
    
    # Try with common substitutions (changing one letter at a time)
    alphabet = string.ascii_lowercase
    for i in range(len(base_word)):
        for c in alphabet:
            if c != base_word[i].lower():
                variant = base_word[:i] + c + base_word[i+1:]
                hash_val = calculate_hash(key, variant)
                if hash_val in hash_set:
                    pos = hashes_list.index(hash_val) + 1
                    print(f"MATCH for '{variant}': {hash_val} (position {pos})")
                    
                # Also try capitalized and uppercase
                variants = [variant.capitalize(), variant.upper()]
                for v in variants:
                    hash_val = calculate_hash(key, v)
                    if hash_val in hash_set:
                        pos = hashes_list.index(hash_val) + 1
                        print(f"MATCH for '{v}': {hash_val} (position {pos})")
    
    # Try dropping letters from February one by one
    for i in range(len(base_word)):
        variant = base_word[:i] + base_word[i+1:]
        hash_val = calculate_hash(key, variant)
        if hash_val in hash_set:
            pos = hashes_list.index(hash_val) + 1
            print(f"MATCH for '{variant}': {hash_val} (position {pos})")
            
        # Also try capitalized and lowercase
        variants = [variant.capitalize(), variant.lower()]
        for v in variants:
            hash_val = calculate_hash(key, v)
            if hash_val in hash_set:
                pos = hashes_list.index(hash_val) + 1
                print(f"MATCH for '{v}': {hash_val} (position {pos})")
    
    # Try common alternate spellings
    alternates = [
        # Common misspellings
        "Feburary", "Febuary", "Febrari", "Februray", "Febrary",
        # Case variations
        "FEBRUARY", "february", "FebruarY", "FEBruary", "FebRUARy",
        # Acronyms
        "FEB", "Feb", "feb", "FEBR", "Febr", "febr",
        # Removing vowels
        "Fbrry", "Fbruary", "Februry", "Fbry", "Fbr",
        # Simplified forms
        "Febru", "Februa",
        # From error messages and testing
        "Febrart", "Febraurt"
    ]
    
    for word in alternates:
        hash_val = calculate_hash(key, word)
        if hash_val in hash_set:
            pos = hashes_list.index(hash_val) + 1
            print(f"MATCH for '{word}': {hash_val} (position {pos})")

def check_potentially_interesting_hashes(key, hashes):
    """Check specific hashes at important positions in the message"""
    interesting_positions = [1, 2, 4, 10, 15, 20, 22, 24, 26, 63, 74]  # Positions based on meaningful parts of the message
    
    print("\nAnalyzing hashes at key positions:")
    for pos in interesting_positions:
        if pos <= len(hashes):
            hash_val = hashes[pos-1]
            print(f"Hash at position {pos}: {hash_val}")

def main():
    key = 6346
    puzzle_file = "PUZZLE-EASY.txt"
    hashes = load_hashes(puzzle_file)
    hash_set = set(hashes)
    
    print(f"Loaded {len(hashes)} hashes from {puzzle_file}")
    print("Searching for date-related words in the puzzle...")
    
    # Try date-related words
    try_date_words(key, hashes, hash_set)
    
    # Check hashes at specific positions
    check_potentially_interesting_hashes(key, hashes)
    
    # Try some dates in various formats
    print("\nTrying actual dates in different formats:")
    today = datetime.now()
    
    date_formats = [
        "%B", "%b",  # Month name
        "%B%d", "%b%d",  # Month and day
        "%B%Y", "%b%Y",  # Month and year
        "%d%B", "%d%b",  # Day and month
        "%Y%B", "%Y%b",  # Year and month
        "%m/%d", "%d/%m",  # Numeric dates
        "%m-%d", "%d-%m",  # Dashed dates
        "%B %d", "%b %d",  # With space
    ]
    
    for fmt in date_formats:
        try:
            date_str = today.strftime(fmt)
            hash_val = calculate_hash(key, date_str)
            if hash_val in hash_set:
                pos = hashes.index(hash_val) + 1
                print(f"MATCH for date '{date_str}': {hash_val} (position {pos})")
        except:
            pass
    
    # Try all numbers from 1-31 (dates of the month)
    for i in range(1, 32):
        for num_format in [str(i), f"{i:02d}", f"{i}th", f"{i}st" if i % 10 == 1 else f"{i}nd" if i % 10 == 2 else f"{i}rd" if i % 10 == 3 else f"{i}th"]:
            hash_val = calculate_hash(key, num_format)
            if hash_val in hash_set:
                pos = hashes.index(hash_val) + 1
                print(f"MATCH for number '{num_format}': {hash_val} (position {pos})")

if __name__ == "__main__":
    main() 