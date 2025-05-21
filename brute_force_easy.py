import hashlib
import base64

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

# Load the puzzle hashes
puzzle_file = "PUZZLE-EASY.txt"
hashes = load_hashes(puzzle_file)
hash_set = set(hashes)

# Key for the easy puzzle
key = 6346

# Define misspellings to try - starting with what you've tried already
misspellings = [
    "Febraurt",  # What you've used initially
    "Febrart",   # What you have in puzzle.py now
    "Februrary",
    "Febuary", "Feburary", "Febraury", 
    "Februay", "Febrary", "Feburaury", "Febuari",
    "Februarey", "Feburary", "Febryuary", "Febrauary",
    "Febuary",
    "febrart", "FEBRART",  # Case variations
    "febuary", "FEBUARY",
    "feburary", "FEBURARY",
]

found = False
for word in misspellings:
    hash_val = calculate_hash(key, word)
    if hash_val in hash_set:
        position = hashes.index(hash_val) + 1
        print(f"MATCH FOUND! '{word}' -> {hash_val} (position {position}/{len(hashes)})")
        found = True

if not found:
    print("\nNo match found from the list. Let's try the original 'February' word:")
    
    original = "February"
    hash_val = calculate_hash(key, original)
    print(f"Original '{original}' -> {hash_val}")
    
    # Also try a direct hash comparison for puzzle-easy.py
    print("\nComparing with all hashes in PUZZLE-EASY.txt:")
    for i, h in enumerate(hashes):
        print(f"Hash {i+1}: {h}")
        
        # Calculate Base64 for comparison with error message
        hash_bytes = bytes.fromhex(h)
        hash_b64 = base64.b64encode(hash_bytes).decode('utf-8')
        print(f"Base64: {hash_b64}")
        
        if "6GV/" in hash_b64:  # The reported hash snippet from the error
            print(f"Found hash containing '6GV/' at position {i+1}: {h} (Base64: {hash_b64})")

    # Try Febryary - remove 'u' and replace with 'y'
    print("\nTrying 'Febryary':")
    febryary = "Febryary"
    hash_val = calculate_hash(key, febryary)
    print(f"'{febryary}' -> {hash_val}")
    if hash_val in hash_set:
        position = hashes.index(hash_val) + 1
        print(f"MATCH FOUND! '{febryary}' -> {hash_val} (position {position}/{len(hashes)})")

print("\nDone checking misspellings.") 