import hashlib
import os
import re

def load_hashes(puzzle_file):
    """Load all hash values from the puzzle file"""
    with open(puzzle_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def load_wordlist(filename):
    """Load words from a wordlist file"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    return []

def decode_puzzle(key, puzzle_file, wordlists):
    """Try to decode the puzzle using the given key and wordlists"""
    hashes = load_hashes(puzzle_file)
    hash_to_word = {}
    
    # Prepare key
    key_encoded = str(key).encode('utf-8')
    
    # Track which hashes we've matched
    matched_hashes = set()
    
    # Try each word from wordlists
    for wordlist_name, words in wordlists.items():
        print(f"Trying {len(words)} words from {wordlist_name}...")
        
        for word in words:
            if not word:
                continue
                
            hash_val = hashlib.md5(key_encoded + word.encode('utf-8')).hexdigest()
            
            if hash_val in hashes and hash_val not in matched_hashes:
                hash_to_word[hash_val] = word
                matched_hashes.add(hash_val)
    
    # Create decoded output
    decoded = []
    unmatched = []
    
    for h in hashes:
        if h in hash_to_word:
            decoded.append(hash_to_word[h])
        else:
            decoded.append("[MISSING]")
            unmatched.append(h)
    
    print(f"\nDecoded {len(matched_hashes)} out of {len(hashes)} hashes ({len(matched_hashes)/len(hashes):.1%})")
    print("\nPartially decoded message:")
    print(" ".join(decoded))
    
    print(f"\n{len(unmatched)} unmatched hashes:")
    for i, h in enumerate(unmatched, 1):
        print(f"{i}. {h}")
    
    return unmatched

def generate_february_variants():
    """Generate variants of February for testing"""
    base = "February"
    variants = [base]
    
    # Add common misspellings
    variants.extend([
        "Febuary", "Feburary", "Febraury", "Februrary", "Februay",
        "Febrary", "February", "Febraurt", "Febrart", "Febury",
        "Feby", "Febr", "Fbruary", "Fbrry", "Fbry"
    ])
    
    # Add all possible single-letter deletions
    for i in range(len(base)):
        variants.append(base[:i] + base[i+1:])
    
    # Add consonant-only version
    variants.append(''.join([c for c in base if c.lower() not in "aeiou"]))
    
    # Add case variations
    result = []
    for v in variants:
        result.append(v)
        result.append(v.lower())
        result.append(v.upper())
        result.append(v.capitalize())
    
    return list(set(result))  # Remove duplicates

def main():
    key = 6346
    puzzle_file = "PUZZLE-EASY.txt"
    
    # Load available wordlists
    wordlists = {}
    
    for filename in ["common_words.txt", "20k.txt", "combined_wordlist.txt", "words.txt"]:
        words = load_wordlist(filename)
        if words:
            wordlists[filename] = words
    
    # Add a small list of common words
    common_words = [
        "the", "and", "a", "to", "of", "in", "is", "you", "that", "it",
        "he", "was", "for", "on", "are", "as", "with", "his", "they", "I",
        "at", "be", "this", "have", "from", "or", "had", "by", "not", "but",
        "what", "all", "were", "we", "when", "your", "can", "said", "there", "use",
        "an", "each", "which", "she", "do", "how", "their", "if", "will", "up"
    ]
    wordlists["common_english"] = common_words
    
    # Add February variants
    february_variants = generate_february_variants()
    wordlists["february_variants"] = february_variants
    
    # Decode the puzzle
    unmatched = decode_puzzle(key, puzzle_file, wordlists)
    
    # Try to specifically find a hash match for February variants
    print("\nSpecifically checking February variants against all hashes...")
    key_encoded = str(key).encode('utf-8')
    
    for variant in february_variants:
        hash_val = hashlib.md5(key_encoded + variant.encode('utf-8')).hexdigest()
        
        if hash_val in unmatched:
            print(f"Found match for '{variant}': {hash_val}")
            
            # See if it's a reasonable misspelling
            if re.match(r'^[A-Za-z]+$', variant) and len(variant) >= 4:
                print(f"This looks like a valid misspelling of February!")
                
                # Update puzzle.py with this value
                print(f"Suggestion: Update puzzle_easy_misspell in puzzle.py to '{variant}'")

if __name__ == "__main__":
    main() 