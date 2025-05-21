import hashlib
import sys
import itertools
import string

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

def try_february_variants(key, hashes):
    """Try many variants of February"""
    hash_set = set(hashes)
    
    # Try simple letter removals - removing each letter one by one
    base = "February"
    for i in range(len(base)):
        variant = base[:i] + base[i+1:]
        hash_val = calculate_hash(key, variant)
        if hash_val in hash_set:
            position = hashes.index(hash_val) + 1
            print(f"MATCH FOUND! '{variant}' -> {hash_val} (position {position}/{len(hashes)})")
            return True

    # Try various vowel removals (common misspellings often drop vowels)
    vowels = "aeiou"
    for i, char in enumerate(base):
        if char.lower() in vowels:
            variant = base[:i] + base[i+1:]
            hash_val = calculate_hash(key, variant)
            if hash_val in hash_set:
                position = hashes.index(hash_val) + 1
                print(f"MATCH FOUND! '{variant}' -> {hash_val} (position {position}/{len(hashes)})")
                return True

    # Try character substitutions
    for i, char in enumerate(base):
        for replacement in string.ascii_lowercase:
            if replacement != char.lower():
                variant = base[:i] + replacement + base[i+1:]
                
                # Try with original capitalization
                hash_val = calculate_hash(key, variant)
                if hash_val in hash_set:
                    position = hashes.index(hash_val) + 1
                    print(f"MATCH FOUND! '{variant}' -> {hash_val} (position {position}/{len(hashes)})")
                    return True
                
                # Try capitalized
                capitalized = variant.capitalize()
                hash_val = calculate_hash(key, capitalized)
                if hash_val in hash_set:
                    position = hashes.index(hash_val) + 1
                    print(f"MATCH FOUND! '{capitalized}' -> {hash_val} (position {position}/{len(hashes)})")
                    return True

    return False

def try_variations_of_common_misspellings(key, hashes):
    """Try variations of commonly misspelled versions of February"""
    hash_set = set(hashes)
    common_misspellings = [
        "Febuary", "Feburary", "Febraury", "Februrary", 
        "Febrary", "Febriary", "Febrari", "Febraer",
        "Febrart", "Febraurt", "Febryary"
    ]
    
    for misspelling in common_misspellings:
        # Try the misspelling directly
        hash_val = calculate_hash(key, misspelling)
        if hash_val in hash_set:
            position = hashes.index(hash_val) + 1
            print(f"MATCH FOUND! '{misspelling}' -> {hash_val} (position {position}/{len(hashes)})")
            return True
        
        # Try all letter cases
        for variant in [misspelling.lower(), misspelling.upper()]:
            hash_val = calculate_hash(key, variant)
            if hash_val in hash_set:
                position = hashes.index(hash_val) + 1
                print(f"MATCH FOUND! '{variant}' -> {hash_val} (position {position}/{len(hashes)})")
                return True
                
        # Try with each letter altered
        for i, char in enumerate(misspelling):
            for replacement in string.ascii_lowercase:
                if replacement != char.lower():
                    variant = misspelling[:i] + replacement + misspelling[i+1:]
                    
                    hash_val = calculate_hash(key, variant)
                    if hash_val in hash_set:
                        position = hashes.index(hash_val) + 1
                        print(f"MATCH FOUND! '{variant}' -> {hash_val} (position {position}/{len(hashes)})")
                        return True
    
    return False

def main():
    """Main function to find the easy puzzle misspelling"""
    puzzle_file = "PUZZLE-EASY.txt"
    key = 6346
    
    try:
        hashes = load_hashes(puzzle_file)
        print(f"Loaded {len(hashes)} hashes from {puzzle_file}")
        
        # First try the currently known misspellings
        current = [
            "Febraurt",  # What was initially used
            "Febrart"    # What's currently in puzzle.py
        ]
        
        for word in current:
            hash_val = calculate_hash(key, word)
            exists = hash_val in set(hashes)
            print(f"Testing current guess '{word}' -> {hash_val} (In puzzle: {exists})")
            
            if exists:
                position = hashes.index(hash_val) + 1
                print(f"MATCH FOUND! '{word}' -> {hash_val} (position {position}/{len(hashes)})")
                return
        
        print("\nTrying variations of 'February'...")
        found = try_february_variants(key, hashes)
        
        if not found:
            print("\nTrying variations of common misspellings...")
            found = try_variations_of_common_misspellings(key, hashes)
        
        if not found:
            # Try changing February to more drastically altered forms 
            print("\nTrying more drastic alterations...")
            
            # Try consonant-only versions (Fbrry, etc.)
            consonant_only = ''.join([c for c in "February" if c.lower() not in "aeiou"])
            hash_val = calculate_hash(key, consonant_only)
            if hash_val in set(hashes):
                position = hashes.index(hash_val) + 1
                print(f"MATCH FOUND! '{consonant_only}' -> {hash_val} (position {position}/{len(hashes)})")
                return
            
            # Try consonant-only capitalized
            consonant_cap = consonant_only.capitalize()
            hash_val = calculate_hash(key, consonant_cap)
            if hash_val in set(hashes):
                position = hashes.index(hash_val) + 1
                print(f"MATCH FOUND! '{consonant_cap}' -> {hash_val} (position {position}/{len(hashes)})")
                return
            
            # Try with more specialized misspellings
            specialized = [
                # Try transformations similar to how "waiting" became "wkitpng"
                "Fbrry", "Fbruar", "Febry", "Fbry", "Fby", 
                "Fby", "Fbuar", "Febar",
                # Try phonetic misspellings
                "Phebuary", "Phebruary", "Febrooary", "Febrewary",
                # Try other cases
                "FBRRY", "fbrry", "Fbrry"
            ]
            
            for word in specialized:
                hash_val = calculate_hash(key, word)
                if hash_val in set(hashes):
                    position = hashes.index(hash_val) + 1
                    print(f"MATCH FOUND! '{word}' -> {hash_val} (position {position}/{len(hashes)})")
                    return
            
            print("No match found with systematic variations.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 