import hashlib
import sys
import os
import time
from multiprocessing import Pool, cpu_count
from collections import Counter

# Usage: python optimized_crack_puzzle.py PUZZLE.txt 9 [start_key] [end_key]

# Most common English words - these are likely to appear in any text
COMMON_WORDS = [
    'the', 'and', 'was', 'for', 'that', 'with', 'they', 'this', 'have', 'from', 
    'not', 'were', 'are', 'but', 'had', 'his', 'her', 'she', 'him', 'their', 'you',
    'all', 'one', 'more', 'my', 'me', 'it', 'in', 'of', 'to', 'a', 'is', 'on',
    'those', 'little', 'out', 'there', 'tall', 'moon', 'full', 'bright', 'behind',
    'could', 'see', 'them', 'plain', 'day', 'though', 'deep', 'night'
]

def load_hashes(puzzle_file):
    """Load all hash values from the puzzle file"""
    with open(puzzle_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def find_duplicate_hashes(puzzle_hashes):
    """Find hashes that appear multiple times in the puzzle - these likely represent common words"""
    counts = Counter(puzzle_hashes)
    return [h for h, count in counts.items() if count > 1]

def check_key_with_common_words(key, duplicate_hashes, hash_set, encoded_common_words):
    """Check if a key is promising by testing it with common words"""
    key_encoded = key.encode('utf-8')
    matches = []
    matched_hashes = set()
    
    # First quickly check all common words
    for word, word_encoded in encoded_common_words:
        h = hashlib.md5(key_encoded + word_encoded).hexdigest()
        if h in hash_set:
            matches.append((h, word))
            matched_hashes.add(h)
            # Early success detection: if we match a duplicate hash, this is very promising
            if h in duplicate_hashes:
                return True, matches, matched_hashes
    
    # If we matched several words (even if not duplicates), that's promising
    if len(matches) >= 5:  # Threshold can be adjusted
        return True, matches, matched_hashes
        
    return False, matches, matched_hashes

def test_key_range(args):
    """Test a range of keys using stride for better distribution"""
    start_key, end_key, stride, key_format, duplicate_hashes, hash_set, encoded_common_words = args
    
    for key_num in range(start_key, end_key, stride):
        key = key_format.format(key_num)
        
        # Quick check with common words
        is_promising, matches, matched_hashes = check_key_with_common_words(
            key, duplicate_hashes, hash_set, encoded_common_words
        )
        
        if is_promising:
            # We found a promising key, report it immediately
            return (key_num, key, matches, matched_hashes)
            
        # Periodic status update
        if key_num % (stride * 100000) == start_key:
            print(f"Process {start_key % stride} checked up to {key_num}")
            
    return None

def verify_key(key, puzzle_hashes, wordlist=None):
    """Verify if a key is correct by testing it with a larger wordlist"""
    if wordlist is None:
        # Use a larger wordlist for verification if available
        if os.path.exists('common_words.txt'):
            with open('common_words.txt', 'r') as f:
                wordlist = [line.strip() for line in f]
        else:
            wordlist = COMMON_WORDS
    
    key_encoded = key.encode('utf-8')
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
    
    if match_ratio > 0.5:  # If we matched more than half, it's likely correct
        # Display partial decode
        decoded = []
        for h in puzzle_hashes:
            if h in hash_to_word:
                decoded.append(hash_to_word[h])
            else:
                decoded.append("[MISSING]")
        
        print("Partial decoded message:")
        print(" ".join(decoded[:30]) + "...")  # Just show the beginning
        
        return key, hash_to_word
    
    return None

def distribute_work(key_length, num_processes, start_key=None, end_key=None):
    """Create strided work distribution for better load balancing"""
    max_key = 10 ** key_length
    if start_key is None:
        start_key = 0
    if end_key is None:
        end_key = max_key
    
    # Create much more ranges than processes for better distribution
    stride = num_processes
    ranges = []
    for i in range(num_processes):
        ranges.append((start_key + i, end_key, stride))
    return ranges

def main():
    if len(sys.argv) < 3:
        print("Usage: python optimized_crack_puzzle.py PUZZLE.txt key_length [start_key] [end_key]")
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
    
    # Pre-encode common words for better performance
    encoded_common_words = [(word, word.encode('utf-8')) for word in COMMON_WORDS]
    
    # Prepare key format
    key_format = '{:0' + str(key_length) + 'd}'
    
    # Set up multiprocessing
    num_processes = min(cpu_count(), 8)
    ranges = distribute_work(key_length, num_processes, start_key, end_key)
    
    print(f"Starting search with {num_processes} processes")
    start_time = time.time()
    
    # Prepare arguments for each worker process
    tasks = [(r[0], r[1], r[2], key_format, duplicate_hashes, hash_set, encoded_common_words) for r in ranges]
    
    # Start worker processes
    with Pool(num_processes) as pool:
        promising_results = []
        for result in pool.imap_unordered(test_key_range, tasks):
            if result:
                key_num, key, matches, matched_hashes = result
                print(f"\nFound promising key: {key}")
                print(f"Matched {len(matched_hashes)} hashes with common words")
                promising_results.append((key_num, key, matches))
                
                # Immediately verify if this key is correct
                verified = verify_key(key, puzzle_hashes)
                if verified:
                    key, hash_to_word = verified
                    print(f"\n*** FOUND KEY: {key} ***")
                    
                    # Save the results to file
                    with open('found_key.txt', 'w') as f:
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
                    
                    print(f"Results saved to found_key.txt")
                    return
                
                print("False positive, continuing search...")
    
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