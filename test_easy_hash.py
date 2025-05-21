import hashlib
import base64

def calculate_hash(key, word):
    """Calculate MD5 hash of key + word and return both hex and base64"""
    key_encoded = str(key).encode('utf-8')
    word_encoded = word.encode('utf-8')
    hash_raw = hashlib.md5(key_encoded + word_encoded).digest()
    hash_hex = hashlib.md5(key_encoded + word_encoded).hexdigest()
    hash_b64 = base64.b64encode(hash_raw).decode('utf-8')
    return hash_hex, hash_b64

# Load puzzle hashes
with open('PUZZLE-EASY.txt', 'r') as f:
    puzzle_hashes = [line.strip() for line in f if line.strip()]
    puzzle_hash_set = set(puzzle_hashes)

# Key for the easy puzzle
key = 6346

# List of potential misspellings of February
misspellings = [
    "february", "February", "FEBRUARY",
    "Febuary", "Feburary", "Febraury", "Februrary", "Februay", "Februrary",
    "Febrary", "Febriary", "Febuari", "Febrari", "Febraer", "Febraury", 
    "Febrart", "Febriary", "Feburary", "Febrary", "Febrari", "Febuery",
    "Febraurt", "Febwary", "Feberry", "Fabruary", "Fabuary", "Feabruary",
    "Feabuary", "Febrewary", "Febrouwary", "Febrouary", "Febuwary", "Ferbuary",
    "Beruary"
]

print("Testing various misspellings of February with key 6346:")
print("=" * 60)
print("| {:<15} | {:<32} | {:<10} |".format("Misspelling", "MD5 Hash", "Base64"))
print("=" * 60)

for word in misspellings:
    hash_hex, hash_b64 = calculate_hash(key, word)
    in_puzzle = "YES" if hash_hex in puzzle_hash_set else "NO"
    
    # Print results in table format
    print("| {:<15} | {:<32} | {:<10} | {}".format(
        word, hash_hex, hash_b64[:10], in_puzzle
    ))
    
    # Also try with different capitalization
    for variant in [word.lower(), word.upper(), word.capitalize()]:
        if variant == word:
            continue
            
        hash_hex, hash_b64 = calculate_hash(key, variant)
        in_puzzle = "YES" if hash_hex in puzzle_hash_set else "NO"
        
        if in_puzzle == "YES":
            print("| {:<15} | {:<32} | {:<10} | {}".format(
                variant, hash_hex, hash_b64[:10], in_puzzle
            ))

print("=" * 60)

# For the specific error message you saw, check if it has "6GV/" in the base64
print("\nMisspellings with '6GV/' in base64 encoding:")
for word in misspellings:
    _, hash_b64 = calculate_hash(key, word)
    if "6GV" in hash_b64:
        print(f"'{word}' -> {hash_b64} (contains 6GV)") 