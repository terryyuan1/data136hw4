import hashlib

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

# Load puzzle hashes
puzzle_file = "PUZZLE-EASY.txt"
hashes = load_hashes(puzzle_file)
hash_set = set(hashes)

# Key for the easy puzzle
key = 6346

# Define common misspellings of February with different capitalizations
misspellings = [
    # Most common misspellings
    "Febuary", "febuary", "FEBUARY",
    "Feburary", "feburary", "FEBURARY",
    
    # Emphasizing capitalization options
    "february", "February", "FEBRUARY", 
    
    # Removing U
    "Febrary", "febrary", "FEBRARY",
    
    # Other common misspellings 
    "Feberry", "feberry", "FEBERRY",
    "Febery", "febery", "FEBERY",
]

print("Testing misspellings with key 6346:")
print("-" * 70)
print(f"{'Misspelling':<15} | {'MD5 Hash':<32} | {'Found':<6}")
print("-" * 70)

for word in misspellings:
    hash_val = calculate_hash(key, word)
    found = "YES" if hash_val in hash_set else "NO"
    
    print(f"{word:<15} | {hash_val:<32} | {found:<6}")

# If no common misspellings worked, let's check against all unmatched hashes
if all(calculate_hash(key, word) not in hash_set for word in misspellings):
    print("\nNone of the common misspellings matched. Trying every hash in the puzzle...")
    
    print(f"{'Hash':<33} | {'Position'}")
    print("-" * 44)
    
    for i, hash_val in enumerate(hashes, 1):
        # For each hash in the puzzle, try to find a misspelling that matches
        for word in misspellings:
            word_hash = calculate_hash(key, word)
            if hash_val == word_hash:
                print(f"{hash_val} | {i:<3} | MATCH: '{word}'")
                break
        else:
            # Check if this hash is one of the significant ones in the message
            if i in [1, 2, 4, 10, 15, 20, 22, 24, 26]:
                print(f"{hash_val} | {i:<3} | Significant position in message")

print("\n\nTrying other date-related words that might be misspelled:")
date_words = [
    "January", "january", "janury", "janaury",
    "March", "march", "mrch",
    "April", "april", "aprl",
    "August", "august", "augst",
    "September", "september", "septmber",
    "October", "october", "octber",
    "November", "november", "novmber",
    "December", "december", "decmber"
]

for word in date_words:
    hash_val = calculate_hash(key, word)
    if hash_val in hash_set:
        position = hashes.index(hash_val) + 1
        print(f"MATCH FOUND! '{word}' -> {hash_val} (position {position}/{len(hashes)})") 