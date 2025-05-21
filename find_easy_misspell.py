import hashlib
import string
import itertools

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

def generate_variants(base_word, max_changes=2):
    """Generate variants of a word with up to max_changes character changes"""
    variants = set()
    variants.add(base_word)
    
    # Add common case variations
    variants.add(base_word.lower())
    variants.add(base_word.upper())
    variants.add(base_word.capitalize())
    
    # Generate common misspellings based on common patterns
    feb_base = ["Feb", "Fab", "Fev", "Fe", "F"]
    endings = ["ruary", "uary", "ary", "ry", "ry", "ery", "urary", "ary", "uari", "rari", "ari"]
    
    for b in feb_base:
        for e in endings:
            variants.add(b + e)
            variants.add(b + e.capitalize())
    
    # Generate special misspellings known to be common
    known_misspellings = [
        "Febuary", "Feburary", "Febraury", "Februrary", "Februay",
        "Febrary", "Febriary", "Febuari", "Febrari", "Febraer",
        "Febrart", "Febraurt", "Febuwary", "Febrewary", "Febrouary"
    ]
    
    for misspelling in known_misspellings:
        variants.add(misspelling)
        variants.add(misspelling.lower())
        variants.add(misspelling.upper())
    
    # Add all possible single character variations
    alphabet = string.ascii_lowercase + string.ascii_uppercase
    
    # Single character changes
    for i in range(len(base_word)):
        for c in alphabet:
            if c != base_word[i]:
                new_word = base_word[:i] + c + base_word[i+1:]
                variants.add(new_word)
    
    # Single character deletions
    for i in range(len(base_word)):
        new_word = base_word[:i] + base_word[i+1:]
        variants.add(new_word)
    
    # Single character insertions
    for i in range(len(base_word) + 1):
        for c in alphabet:
            new_word = base_word[:i] + c + base_word[i:]
            variants.add(new_word)
    
    # If we want more variations, generate combinations of changes
    if max_changes > 1:
        new_variants = set()
        for variant in list(variants):
            if variant == base_word or len(variant) <= 3:
                continue
            
            # Apply single changes to each variant
            for i in range(len(variant)):
                for c in alphabet:
                    if c != variant[i]:
                        new_variants.add(variant[:i] + c + variant[i+1:])
        
        variants.update(new_variants)
    
    return variants

def find_misspellings():
    """Find misspellings by checking hashes"""
    key = 6346
    puzzle_file = "PUZZLE-EASY.txt"
    base_word = "February"
    
    print(f"Searching for misspellings of '{base_word}' in {puzzle_file}...")
    hashes = load_hashes(puzzle_file)
    hash_set = set(hashes)
    
    variants = generate_variants(base_word)
    print(f"Generated {len(variants)} variants to check")
    
    # Try each variant
    found = 0
    for variant in variants:
        h = calculate_hash(key, variant)
        if h in hash_set:
            position = hashes.index(h) + 1
            print(f"MATCH FOUND! '{variant}' -> {h} (position {position}/{len(hashes)})")
            found += 1
    
    if not found:
        print("No matches found with the generated variants.")
        
        # Try Feb with various suffixes
        print("\nTrying additional variants...")
        prefix = "Feb"
        for length in range(1, 8):
            for suffix in itertools.product(alphabet, repeat=length):
                suffix_str = ''.join(suffix)
                variant = prefix + suffix_str
                
                h = calculate_hash(key, variant)
                if h in hash_set:
                    position = hashes.index(h) + 1
                    print(f"MATCH FOUND! '{variant}' -> {h} (position {position}/{len(hashes)})")
                    found += 1
                    
                # Also try capitalized
                variant_cap = variant.capitalize()
                h = calculate_hash(key, variant_cap)
                if h in hash_set:
                    position = hashes.index(h) + 1
                    print(f"MATCH FOUND! '{variant_cap}' -> {h} (position {position}/{len(hashes)})")
                    found += 1
                    
                if found > 5:  # Limit to avoid excessive processing
                    break
            
            if found > 5:
                break

if __name__ == "__main__":
    find_misspellings() 