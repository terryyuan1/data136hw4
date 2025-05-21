import hashlib
import sys

def load_hashes(puzzle_file):
    """Load all hash values from the puzzle file"""
    with open(puzzle_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def calculate_hash(key, word):
    """Calculate MD5 hash of key + word"""
    key_encoded = str(key).encode('utf-8')
    word_encoded = word.encode('utf-8')
    hash_val = hashlib.md5(key_encoded + word_encoded).hexdigest()
    return hash_val

def generate_february_variants():
    """Generate common misspellings of February"""
    variants = [
        "Febraury", "Febuary", "Feburary", "Febuari", "Febrari",
        "Feburaury", "Februari", "Februrary", "Februay", "Febrary",
        "Febrart", "Febraurt", "Feburart", "Febrarey", "Feburey",
        "Febary", "Febury", "Febrary", "Februweary", "Febuwary", 
        "Februr", "Febr", "Feby", "Febrry", "Febry", 
        "febraury", "febuary", "feburary", "febuari", "febrari",
        "feburaury", "februari", "februrary", "februay", "febrary",
        "febrart", "febraurt", "feburart", "febrarey", "feburey",
        "febary", "febury", "febrary", "februweary", "febuwary",
        "februr", "febr", "feby", "febrry", "febry"
    ]
    
    # Add capitalization variants
    for word in list(variants):  # Make a copy of the list to avoid modifying during iteration
        variants.append(word.upper())
        variants.append(word.capitalize())
        
    return list(set(variants))  # Remove duplicates

def test_easy_puzzle_misspellings():
    easy_key = 6346
    puzzle_file = "PUZZLE-EASY.txt"
    
    try:
        hashes = load_hashes(puzzle_file)
        hash_set = set(hashes)
        
        variants = generate_february_variants()
        print(f"Testing {len(variants)} variants against {len(hashes)} hashes...")
        
        for variant in variants:
            hash_val = calculate_hash(easy_key, variant)
            if hash_val in hash_set:
                position = hashes.index(hash_val) + 1
                print(f"MATCH FOUND! '{variant}' -> {hash_val} (position {position})")
            
            # Also try with different case combinations
            for case_variant in [variant, variant.lower(), variant.upper(), variant.capitalize()]:
                if case_variant == variant:
                    continue
                    
                hash_val = calculate_hash(easy_key, case_variant)
                if hash_val in hash_set:
                    position = hashes.index(hash_val) + 1
                    print(f"MATCH FOUND! '{case_variant}' -> {hash_val} (position {position})")
        
        print("Done testing all variants.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_easy_puzzle_misspellings() 