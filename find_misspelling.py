import hashlib
import sys
import itertools
import string
from collections import Counter

def load_hashes(hash_file):
    """Load unmatched hashes from file"""
    with open(hash_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def load_text(text_file):
    """Load the decoded paragraph"""
    with open(text_file, 'r') as f:
        return f.read().strip()

def hamming_distance(s1, s2):
    """Calculate Hamming distance between two strings"""
    if len(s1) != len(s2):
        return float('inf')  # Different lengths
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def generate_hamming_variants(word, max_distance=2):
    """Generate all possible variants with Hamming distance up to max_distance"""
    if not word:
        return []
    
    variants = set()
    positions = range(len(word))
    chars = string.ascii_lowercase + string.ascii_uppercase
    
    # For Hamming distance 1
    for pos in positions:
        for c in chars:
            if c != word[pos]:
                variant = word[:pos] + c + word[pos+1:]
                variants.add(variant)
    
    # For Hamming distance 2
    if max_distance >= 2:
        for pos1, pos2 in itertools.combinations(positions, 2):
            for c1 in chars:
                if c1 == word[pos1]:
                    continue
                for c2 in chars:
                    if c2 == word[pos2]:
                        continue
                    variant = (
                        word[:pos1] + c1 + word[pos1+1:pos2] + 
                        c2 + word[pos2+1:]
                    )
                    variants.add(variant)
    
    return variants

def find_misspelling(unmatched_hashes, key, decoded_text):
    """Find the misspelled word by checking all possible variants"""
    key_encoded = str(key).encode('utf-8')
    words = decoded_text.split()
    hash_set = set(unmatched_hashes)
    
    # Count word frequencies to prioritize checking
    word_counts = Counter(words)
    common_words = [w for w, _ in word_counts.most_common()]
    print(f"Found {len(common_words)} unique words in decoded text")
    
    # Get the missing words (marked as [MISSING])
    missing_indices = [i for i, w in enumerate(words) if w == "[MISSING]"]
    print(f"Found {len(missing_indices)} missing words in decoded text")
    
    # Try to match each word in the text with a variant
    for word in common_words:
        if len(word) < 3:  # Skip very short words
            continue
            
        print(f"Checking variants for word: {word}")
        variants = generate_hamming_variants(word)
        found = 0
        
        for variant in variants:
            h = hashlib.md5(key_encoded + variant.encode('utf-8')).hexdigest()
            if h in hash_set:
                print(f"FOUND MATCH! Word: '{word}' -> Misspelled: '{variant}'")
                print(f"Hash: {h}")
                found += 1
        
        if found:
            print(f"Found {found} variants for '{word}'")
    
    # If we didn't find anything, try all common English words
    print("\nTrying common English words...")
    try:
        with open('common_words.txt', 'r') as f:
            english_words = [line.strip() for line in f]
            
        # Try words from the common words list
        for word in english_words:
            if len(word) < 3:  # Skip very short words
                continue
                
            # Check if this word might be the misspelled one
            variants = generate_hamming_variants(word)
            found = 0
            
            for variant in variants:
                h = hashlib.md5(key_encoded + variant.encode('utf-8')).hexdigest()
                if h in hash_set:
                    print(f"FOUND MATCH! Common word: '{word}' -> Misspelled: '{variant}'")
                    print(f"Hash: {h}")
                    found += 1
            
            if found:
                print(f"Found {found} variants for '{word}'")
                
    except FileNotFoundError:
        print("No common_words.txt file found for additional checks.")

def main():
    if len(sys.argv) != 4:
        print("Usage: python find_misspelling.py unmatched_hashes.txt key decoded_paragraph.txt")
        sys.exit(1)
        
    hash_file = sys.argv[1]
    key = sys.argv[2]
    text_file = sys.argv[3]
    
    unmatched_hashes = load_hashes(hash_file)
    decoded_text = load_text(text_file)
    
    print(f"Searching for misspellings with key: {key}")
    print(f"Unmatched hashes: {len(unmatched_hashes)}")
    
    find_misspelling(unmatched_hashes, key, decoded_text)

if __name__ == "__main__":
    main() 