#!/usr/bin/env python3
"""
Puzzle Solver for CMSC13600-HW6
This script combines:
1. Fast key cracking using optimized techniques
2. Message decoding with the found key
3. Misspelled word identification with Hamming distance

Usage:
python puzzle_solver.py crack PUZZLE.txt 9 [start_key] [end_key]
python puzzle_solver.py verify PUZZLE.txt key 
python puzzle_solver.py find PUZZLE.txt key decoded.txt [unmatched.txt]
"""

import hashlib
import sys
import os
import time
import itertools
import string
from multiprocessing import Pool, cpu_count
from collections import Counter

# ======= Configuration =======
# Words likely to appear in the text - modify based on your knowledge of the text
TEXT_WORDS = [
    'the', 'and', 'was', 'for', 'that', 'with', 'they', 'this', 'have', 'from', 
    'not', 'were', 'are', 'but', 'had', 'his', 'her', 'she', 'him', 'their', 'you',
    'all', 'one', 'more', 'my', 'me', 'it', 'in', 'of', 'to', 'a', 'is', 'on',
    'those', 'little', 'bastards', 'were', 'hiding', 'out', 'there', 'tall', 'grass', 
    'moon', 'full', 'bright', 'behind', 'them', 'so', 'could', 'see', 'plain',
    'as', 'day', 'though', 'deep', 'night', 'lightning', 'bugs', 'flashed', 'black',
    'waited', 'at', 'miss', 'watson', 'kitchen', 'door', 'rocked', 'loose', 'step',
    'foot', 'knew', 'going', 'tell', 'fix', 'tomorrow', 'waiting', 'give', 'pan',
    'corn', 'bread', 'made', 'sadie', 'recipe', 'big', 'part', 'slave', 'life', 
    'wait', 'some', 'more', 'demands', 'food', 'ends', 'days', 'just', 'deserved',
    'christian', 'reward', 'end', 'all', 'white', 'boys', 'huck', 'tom', 'watched'
]

# Most frequent words that appear multiple times in texts
FREQUENT_WORDS = [
    'the', 'was', 'and', 'it', 'to', 'a', 'for', 'of', 'in', 'i', 'my',
    'that', 'you', 'with', 'me', 'on', 'at', 'by', 'this', 'but'
]

# ======= Utility Functions =======
def load_hashes(puzzle_file):
    """Load all hash values from the puzzle file"""
    with open(puzzle_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def find_duplicate_hashes(puzzle_hashes):
    """Find hashes that appear multiple times in the puzzle"""
    counts = Counter(puzzle_hashes)
    duplicates = [(h, count) for h, count in counts.items() if count > 1]
    return sorted(duplicates, key=lambda x: x[1], reverse=True)

def load_words(wordlist_file):
    """Load words from a wordlist file"""
    with open(wordlist_file, 'r') as f:
        return [line.strip().lower() for line in f if line.strip()]

def load_text(text_file):
    """Load the decoded paragraph"""
    with open(text_file, 'r') as f:
        return f.read().strip()

# ======= Key Cracking Functions =======
def verify_key_fast(key, hash_set, frequent_words):
    """Quick check if a key matches several frequent words"""
    key_encoded = str(key).encode('utf-8')
    matches = 0
    
    for word in frequent_words:
        h = hashlib.md5(key_encoded + word.encode('utf-8')).hexdigest()
        if h in hash_set:
            matches += 1
            if matches >= 3:  # We found multiple matches, promising key
                return True
    
    return False

def test_key_range(args):
    """Test a range of keys using stride for better distribution"""
    start_key, end_key, stride, key_format, duplicate_hashes, hash_set, frequent_words, text_words_encoded = args
    frequent_words_encoded = [(word, word.encode('utf-8')) for word in frequent_words]
    duplicate_set = {h for h, _ in duplicate_hashes}
    
    for key_num in range(start_key, end_key, stride):
        key = key_format.format(key_num)
        key_encoded = key.encode('utf-8')
        
        # Ultra-quick check: just check the most frequent word
        h = hashlib.md5(key_encoded + b'the').hexdigest()
        if h in hash_set:
            # Quick check with duplicated hashes
            matched_duplicates = 0
            for word, word_encoded in frequent_words_encoded:
                h = hashlib.md5(key_encoded + word_encoded).hexdigest()
                if h in duplicate_set:
                    matched_duplicates += 1
                    if matched_duplicates >= 2:  # Found multiple matches with duplicates
                        # This key is worth investigating further
                        if verify_key_fast(key, hash_set, frequent_words):
                            # Found a promising key, investigate more
                            matches = []
                            matched_hashes = set()
                            for word, word_encoded in text_words_encoded:
                                h = hashlib.md5(key_encoded + word_encoded).hexdigest()
                                if h in hash_set:
                                    matches.append((h, word))
                                    matched_hashes.add(h)
                            
                            return (key_num, key, matches, matched_hashes)
            
        # Periodic status update with very low frequency
        if key_num % (stride * 1000000) == start_key:
            print(f"Process {start_key % stride} checked up to {key_num}")
            
    return None

def verify_key(key, puzzle_hashes, wordlist=None, save_to_file=True):
    """Verify if a key is correct by testing it with a larger wordlist"""
    if wordlist is None:
        # Try to use a good wordlist for verification
        for filename in ['common_words.txt', '20k.txt', 'words.txt', 'combined_wordlist.txt']:
            if os.path.exists(filename):
                print(f"Using wordlist: {filename}")
                with open(filename, 'r') as f:
                    wordlist = [line.strip().lower() for line in f if line.strip()]
                break
        else:
            print("No wordlist found, using built-in word list")
            wordlist = TEXT_WORDS
    
    key_encoded = str(key).encode('utf-8')
    hash_set = set(puzzle_hashes)
    matched = 0
    hash_to_word = {}
    
    for word in wordlist:
        h = hashlib.md5(key_encoded + word.encode('utf-8')).hexdigest()
        if h in hash_set:
            hash_to_word[h] = word
            matched += 1
    
    match_ratio = matched / len(puzzle_hashes)
    print(f"Key {key} matched {matched}/{len(puzzle_hashes)} hashes ({match_ratio:.1%})")
    
    if match_ratio > 0.3:  # Lowered threshold for quicker results
        # Decode the message
        decoded = []
        unmatched = []
        
        for h in puzzle_hashes:
            if h in hash_to_word:
                decoded.append(hash_to_word[h])
            else:
                decoded.append("[MISSING]")
                unmatched.append(h)
        
        decoded_text = " ".join(decoded)
        print("\nPartial decoded message:")
        print(decoded_text[:200] + "..." if len(decoded_text) > 200 else decoded_text)
        
        if save_to_file:
            # Save to files
            with open(f'decoded_{key}.txt', 'w') as f:
                f.write(decoded_text)
            
            with open(f'unmatched_{key}.txt', 'w') as f:
                for h in unmatched:
                    f.write(h + '\n')
            
            print(f"Saved decoded message to decoded_{key}.txt")
            print(f"Saved unmatched hashes to unmatched_{key}.txt")
        
        return key, hash_to_word, decoded_text, unmatched
    
    return None

def distribute_work(key_length, num_processes, start_key=None, end_key=None):
    """Create work distribution for better load balancing"""
    max_key = 10 ** key_length
    if start_key is None:
        start_key = 0
    if end_key is None:
        end_key = max_key
    
    stride = num_processes
    ranges = []
    for i in range(num_processes):
        ranges.append((start_key + i, end_key, stride))
    return ranges

def crack_key(puzzle_file, key_length, start_key=None, end_key=None):
    """Main function to crack the key"""
    puzzle_hashes = load_hashes(puzzle_file)
    hash_set = set(puzzle_hashes)
    duplicate_hashes = find_duplicate_hashes(puzzle_hashes)
    
    print(f"Loaded {len(puzzle_hashes)} hashes from {puzzle_file}")
    print(f"Found {len(duplicate_hashes)} duplicate hashes")
    
    if duplicate_hashes:
        print("Most frequent duplicates:")
        for h, count in duplicate_hashes[:5]:
            print(f"  Hash {h[:8]}... appears {count} times")
    
    # Pre-encode text words for better performance
    text_words_encoded = [(word, word.encode('utf-8')) for word in TEXT_WORDS]
    
    # Prepare key format
    key_format = '{:0' + str(key_length) + 'd}'
    
    # Set up multiprocessing
    num_processes = min(cpu_count(), 8)
    ranges = distribute_work(key_length, num_processes, start_key, end_key)
    
    print(f"Starting search with {num_processes} processes")
    if start_key is not None and end_key is not None:
        print(f"Searching keys from {start_key} to {end_key}")
        print(f"This is {(end_key - start_key) / 10**key_length * 100:.6f}% of the key space")
    
    start_time = time.time()
    
    # Prepare arguments for each worker process
    tasks = [
        (r[0], r[1], r[2], key_format, duplicate_hashes, hash_set, FREQUENT_WORDS, text_words_encoded) 
        for r in ranges
    ]
    
    # Start worker processes
    with Pool(num_processes) as pool:
        promising_results = []
        for result in pool.imap_unordered(test_key_range, tasks):
            if result:
                key_num, key, matches, matched_hashes = result
                print(f"\nFound promising key: {key}")
                print(f"Matched {len(matched_hashes)} hashes with text words")
                promising_results.append((key_num, key, matches))
                
                # Immediately verify if this key is correct
                verified = verify_key(key, puzzle_hashes)
                if verified:
                    key, hash_to_word, decoded_text, unmatched = verified
                    print(f"\n*** FOUND KEY: {key} ***")
                    elapsed_time = time.time() - start_time
                    print(f"Key found in {elapsed_time:.1f} seconds")
                    
                    # Find misspellings
                    print("\nLooking for misspelled words...")
                    find_misspellings(key, unmatched, decoded_text)
                    
                    return key, hash_to_word, decoded_text, unmatched
                
                print("Not the right key, continuing search...")
    
    elapsed_time = time.time() - start_time
    print(f"\nSearch completed in {elapsed_time:.1f} seconds")
    print(f"Found {len(promising_results)} promising results for further investigation")
    
    # If we didn't find the key, try the most promising results again
    for key_num, key, matches in promising_results:
        verified = verify_key(key, puzzle_hashes)
        if verified:
            return verified
    
    return None

# ======= Misspelling Finder Functions =======
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

def find_misspellings(key, unmatched_hashes, decoded_text):
    """Find misspelled words by checking Hamming distance 2 variants"""
    key_encoded = str(key).encode('utf-8')
    words = decoded_text.split()
    hash_set = set(unmatched_hashes)
    
    # Count word frequencies to prioritize checking
    word_counts = Counter([w for w in words if w != "[MISSING]"])
    common_words = [w for w, _ in word_counts.most_common(50)]  # Top 50 words
    print(f"Checking {len(common_words)} most common words for misspellings")
    
    # Get the missing words (marked as [MISSING])
    missing_indices = [i for i, w in enumerate(words) if w == "[MISSING]"]
    print(f"Found {len(missing_indices)} missing words in decoded text")
    
    # Try to match each common word with a variant
    found_misspellings = []
    for word in common_words:
        if len(word) < 3:  # Skip very short words
            continue
            
        variants = generate_hamming_variants(word)
        for variant in variants:
            h = hashlib.md5(key_encoded + variant.encode('utf-8')).hexdigest()
            if h in hash_set:
                print(f"FOUND MISSPELLING! '{word}' -> '{variant}'")
                print(f"Hash: {h}")
                found_misspellings.append((word, variant, h))
    
    # Try with additional word lists
    for filename in ['common_words.txt', '20k.txt']:
        if os.path.exists(filename):
            print(f"\nChecking misspellings against {filename}...")
            try:
                wordlist = load_words(filename)[:5000]  # Limit to first 5000 words
                for word in wordlist:
                    if word in common_words or len(word) < 3:
                        continue
                        
                    variants = generate_hamming_variants(word)
                    for variant in variants:
                        h = hashlib.md5(key_encoded + variant.encode('utf-8')).hexdigest()
                        if h in hash_set:
                            print(f"FOUND MISSPELLING! '{word}' -> '{variant}'")
                            print(f"Hash: {h}")
                            found_misspellings.append((word, variant, h))
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    # Save results
    if found_misspellings:
        with open(f'misspellings_{key}.txt', 'w') as f:
            f.write(f"Key: {key}\n\n")
            f.write("Found misspellings:\n")
            for word, variant, h in found_misspellings:
                f.write(f"Correct: '{word}' -> Misspelled: '{variant}' (Hash: {h})\n")
        print(f"\nFound {len(found_misspellings)} potential misspellings")
        print(f"Results saved to misspellings_{key}.txt")
    else:
        print("\nNo misspellings found!")
    
    return found_misspellings

# ======= Main Functions =======
def cmd_crack(args):
    """Command to crack a puzzle key"""
    if len(args) < 2:
        print("Usage: python puzzle_solver.py crack PUZZLE.txt key_length [start_key] [end_key]")
        return
    
    puzzle_file = args[0]
    key_length = int(args[1])
    start_key = int(args[2]) if len(args) > 2 else None
    end_key = int(args[3]) if len(args) > 3 else None
    
    result = crack_key(puzzle_file, key_length, start_key, end_key)
    if result:
        key, hash_to_word, decoded_text, unmatched = result
        print("\nCracking completed successfully!")
    else:
        print("\nCracking failed - no key found.")

def cmd_verify(args):
    """Command to verify a known key"""
    if len(args) < 2:
        print("Usage: python puzzle_solver.py verify PUZZLE.txt key [wordlist.txt]")
        return
    
    puzzle_file = args[0]
    key = args[1]
    wordlist_file = args[2] if len(args) > 2 else None
    
    puzzle_hashes = load_hashes(puzzle_file)
    
    if wordlist_file:
        wordlist = load_words(wordlist_file)
    else:
        wordlist = None
    
    result = verify_key(key, puzzle_hashes, wordlist)
    if result:
        key, hash_to_word, decoded_text, unmatched = result
        print("\nVerification successful!")
    else:
        print("\nVerification failed - key doesn't match enough hashes.")

def cmd_find(args):
    """Command to find misspellings"""
    if len(args) < 3:
        print("Usage: python puzzle_solver.py find PUZZLE.txt key decoded.txt [unmatched.txt]")
        return
    
    puzzle_file = args[0]
    key = args[1]
    decoded_file = args[2]
    unmatched_file = args[3] if len(args) > 3 else None
    
    if unmatched_file:
        unmatched = load_hashes(unmatched_file)
    else:
        # Generate unmatched hashes
        puzzle_hashes = load_hashes(puzzle_file)
        _, _, _, unmatched = verify_key(key, puzzle_hashes, save_to_file=False)
    
    decoded_text = load_text(decoded_file)
    
    print(f"Looking for misspellings in {len(unmatched)} unmatched hashes")
    find_misspellings(key, unmatched, decoded_text)

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python puzzle_solver.py [crack|verify|find] [arguments...]")
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if command == "crack":
        cmd_crack(args)
    elif command == "verify":
        cmd_verify(args)
    elif command == "find":
        cmd_find(args)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: crack, verify, find")

if __name__ == "__main__":
    main() 