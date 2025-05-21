import hashlib
import sys
import os
import time
from multiprocessing import Pool, cpu_count
from collections import Counter
import itertools

# Usage: python optimized_crack_puzzle_final.py PUZZLE.txt 9 [start_key] [end_key]

# Words from the decoded message - using actual words from the text for maximum speed
TEXT_WORDS = [
    'the', 'and', 'was', 'for', 'that', 'with', 'they', 'this', 'have', 'from', 
    'not', 'were', 'are', 'but', 'had', 'his', 'her', 'she', 'him', 'their', 'you',
    'all', 'one', 'more', 'my', 'me', 'it', 'in', 'of', 'to', 'a', 'is', 'on',
    'those', 'little', 'bastards', 'hiding', 'out', 'there', 'tall', 'grass', 
    'moon', 'full', 'bright', 'behind', 'them', 'so', 'could', 'see', 'plain',
    'as', 'day', 'though', 'deep', 'night', 'lightning', 'bugs', 'flashed', 'black',
    'waited', 'at', 'miss', 'watson', 'kitchen', 'door', 'rocked', 'loose', 'step',
    'foot', 'knew', 'going', 'tell', 'fix', 'tomorrow', 'waiting', 'give', 'pan',
    'corn', 'bread', 'made', 'sadie', 'recipe', 'big', 'part', 'slave', 'life', 
    'wait', 'some', 'more', 'demands', 'food', 'ends', 'days', 'just', 'deserved',
    'christian', 'reward', 'end', 'all', 'white', 'boys', 'huck', 'tom', 'watched'
]

# Most frequent words that appear multiple times in the text
FREQUENT_WORDS = [
    'the', 'was', 'and', 'it', 'to', 'a', 'for', 'of', 'in', 'waiting',
    'some', 'more', 'all', 'waited', 'wait', 'with', 'them', 'my', 'i', 'as'
]

def load_hashes(puzzle_file):
    """Load all hash values from the puzzle file"""
    with open(puzzle_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def find_duplicate_hashes(puzzle_hashes):
    """Find hashes that appear multiple times in the puzzle - these likely represent common words"""
    counts = Counter(puzzle_hashes)
    duplicates = [(h, count) for h, count in counts.items() if count > 1]
    return sorted(duplicates, key=lambda x: x[1], reverse=True)  # Sort by frequency

def verify_key_fast(key, hash_set, frequent_words):
    """Quick check if a key matches several frequent words"""
    key_encoded = str(key).encode('utf-8')
    matches = 0
    
    for word in frequent_words:
        h = hashlib.md5(key_encoded + word.encode('utf-8')).hexdigest()
        if h in hash_set:
            matches += 1
            if matches >= 3:  # We found multiple matches, this is promising
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
        
        # Ultra-quick check: just check the most frequent word in the text
        # This will eliminate 99.9% of keys immediately
        h = hashlib.md5(key_encoded + b'the').hexdigest()
        if h in hash_set:
            # Quick check with duplicated hashes
            matched_duplicates = 0
            for word, word_encoded in frequent_words_encoded:
                h = hashlib.md5(key_encoded + word_encoded).hexdigest()
                if h in duplicate_set:
                    matched_duplicates += 1
                    if matched_duplicates >= 2:  # Found multiple matches with duplicates
                        # This key is worth investigating - do a more thorough check
                        if verify_key_fast(key, hash_set, frequent_words):
                            # Found a promising key, investigate further
                            matches = []
                            matched_hashes = set()
                            for word, word_encoded in text_words_encoded:
                                h = hashlib.md5(key_encoded + word_encoded).hexdigest()
                                if h in hash_set:
                                    matches.append((h, word))
                                    matched_hashes.add(h)
                            
                            return (key_num, key, matches, matched_hashes)
            
        # Periodic status update with very low frequency to minimize overhead
        if key_num % (stride * 1000000) == start_key:
            print(f"Process {start_key % stride} checked up to {key_num}")
            
    return None

def verify_key(key, puzzle_hashes, wordlist=None):
    """Verify if a key is correct by testing it with a larger wordlist"""
    if wordlist is None:
        # Use a specialized wordlist for verification
        if os.path.exists('common_words.txt'):
            with open('common_words.txt', 'r') as f:
                wordlist = [line.strip() for line in f]
        else:
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
        # Display partial decode
        decoded = []
        for h in puzzle_hashes[:30]:  # Just show beginning
            if h in hash_to_word:
                decoded.append(hash_to_word[h])
            else:
                decoded.append("[MISSING]")
        
        print("Partial decoded message (beginning):")
        print(" ".join(decoded))
        
        return key, hash_to_word
    
    return None

def distribute_work(key_length, num_processes, start_key=None, end_key=None):
    """Create strided work distribution for better load balancing"""
    max_key = 10 ** key_length
    if start_key is None:
        start_key = 0
    if end_key is None:
        end_key = max_key
    
    # Use a strided approach to distribute keys among processes
    stride = num_processes
    ranges = []
    for i in range(num_processes):
        ranges.append((start_key + i, end_key, stride))
    return ranges

def main():
    if len(sys.argv) < 3:
        print("Usage: python optimized_crack_puzzle_final.py PUZZLE.txt key_length [start_key] [end_key]")
        sys.exit(1)
    
    puzzle_file = sys.argv[1]
    key_length = int(sys.argv[2])
    
    start_key = None
    end_key = None
    if len(sys.argv) >= 4:
        start_key = int(sys.argv[3])
    if len(sys.argv) >= 5:
        end_key = int(sys.argv[4])
    
    # Load puzzle hashes and find duplicates
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
                    key, hash_to_word = verified
                    print(f"\n*** FOUND KEY: {key} ***")
                    
                    # Save the results to file
                    with open(f'found_key_{key}.txt', 'w') as f:
                        f.write(f"Key: {key}\n")
                        f.write(f"Matched {len(hash_to_word)} out of {len(puzzle_hashes)} hashes\n")
                        
                        # Create a decoded message file
                        decoded = []
                        unmatched = []
                        for h in puzzle_hashes:
                            if h in hash_to_word:
                                decoded.append(hash_to_word[h])
                            else:
                                decoded.append("[MISSING]")
                                unmatched.append(h)
                        
                        f.write("\nDecoded message:\n")
                        f.write(" ".join(decoded))
                        
                        f.write("\n\nUnmatched hashes:\n")
                        for h in unmatched:
                            f.write(h + "\n")
                    
                    print(f"Results saved to found_key_{key}.txt")
                    elapsed_time = time.time() - start_time
                    print(f"Key found in {elapsed_time:.1f} seconds")
                    
                    # Now find the misspelled word
                    print("\nLooking for the misspelled word...")
                    
                    return
                
                print("Not the right key, continuing search...")
    
    elapsed_time = time.time() - start_time
    print(f"\nSearch completed in {elapsed_time:.1f} seconds")
    print(f"Found {len(promising_results)} promising results for further investigation")
    
    # If we didn't find the key, we can try the most promising results with more verification
    if promising_results:
        print("\nTrying promising keys with more verification:")
        for key_num, key, matches in promising_results:
            verify_key(key, puzzle_hashes)

if __name__ == "__main__":
    main() 