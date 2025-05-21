import hashlib
import sys

def load_hashes(puzzle_file):
    """Load all hash values from the puzzle file"""
    with open(puzzle_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def load_words(wordlist_file):
    """Load words from a wordlist file"""
    with open(wordlist_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def verify_known_key(puzzle_file, key, wordlist_file=None):
    """Verify a known key works with the puzzle"""
    puzzle_hashes = load_hashes(puzzle_file)
    hash_set = set(puzzle_hashes)
    
    # Try with encoded key
    key_encoded = str(key).encode('utf-8')
    
    # Try with different wordlists
    wordlists = []
    if wordlist_file:
        wordlists.append((wordlist_file, load_words(wordlist_file)))
    
    # Try common English wordlists
    for filename in ['common_words.txt', '20k.txt', 'words.txt', 'combined_wordlist.txt']:
        try:
            wordlists.append((filename, load_words(filename)))
        except FileNotFoundError:
            pass
    
    if not wordlists:
        # Fallback to a small list of common words
        common_words = [
            'the', 'and', 'was', 'for', 'that', 'with', 'they', 'this', 'have', 'from',
            'not', 'were', 'are', 'but', 'had', 'his', 'her', 'she', 'him', 'their', 'you',
            'all', 'one', 'more', 'my', 'me', 'it', 'in', 'of', 'to', 'a', 'is', 'on', 
            'those', 'little', 'bastards', 'were', 'hiding', 'out', 'there', 'in', 'the', 'tall', 
            'grass', 'moon', 'not', 'quite', 'full', 'but', 'bright', 'and', 'it', 'was', 'behind',
            'them', 'so', 'I', 'could', 'see', 'them', 'as', 'plain', 'as', 'day', 'though', 'it',
            'was', 'deep', 'night'
        ]
        wordlists.append(('built-in common words', common_words))
    
    best_match_count = 0
    best_hash_to_word = {}
    best_wordlist = None
    
    for wordlist_name, wordlist in wordlists:
        print(f"Testing with wordlist: {wordlist_name} ({len(wordlist)} words)")
        
        hash_to_word = {}
        matched_count = 0
        
        for word in wordlist:
            h = hashlib.md5(key_encoded + word.encode('utf-8')).hexdigest()
            if h in hash_set:
                hash_to_word[h] = word
                matched_count += 1
        
        match_ratio = matched_count / len(puzzle_hashes)
        print(f"Key {key} matched {matched_count}/{len(puzzle_hashes)} hashes ({match_ratio:.1%})")
        
        if matched_count > best_match_count:
            best_match_count = matched_count
            best_hash_to_word = hash_to_word
            best_wordlist = wordlist_name
    
    print(f"\nBest match: {best_match_count}/{len(puzzle_hashes)} hashes ({best_match_count/len(puzzle_hashes):.1%}) using {best_wordlist}")
    
    # Output decoded message and unmatched hashes
    decoded = []
    unmatched_hashes = []
    
    for h in puzzle_hashes:
        if h in best_hash_to_word:
            decoded.append(best_hash_to_word[h])
        else:
            decoded.append("[MISSING]")
            unmatched_hashes.append(h)
    
    print("\nPartially decoded message:")
    print(" ".join(decoded))
    
    print("\nUnmatched hashes:")
    for h in unmatched_hashes:
        print(h)
    
    # Save the results to file
    with open('verification_results.txt', 'w') as f:
        f.write(f"Key: {key}\n")
        f.write(f"Best match: {best_match_count}/{len(puzzle_hashes)} hashes ({best_match_count/len(puzzle_hashes):.1%}) using {best_wordlist}\n")
        f.write("\nPartially decoded message:\n")
        f.write(" ".join(decoded))
        f.write("\n\nUnmatched hashes:\n")
        for h in unmatched_hashes:
            f.write(h + "\n")
    
    print("\nResults saved to verification_results.txt")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python verify_key.py PUZZLE.txt key [wordlist_file]")
        sys.exit(1)
    
    puzzle_file = sys.argv[1]
    key = sys.argv[2]
    wordlist_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    verify_known_key(puzzle_file, key, wordlist_file) 