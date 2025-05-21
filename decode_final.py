import hashlib
import os

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

def load_wordlist(filename):
    """Load words from a wordlist file"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    return []

def decode_puzzle(key, puzzle_file, additional_words=None):
    """Decode the puzzle using the given key"""
    hashes = load_hashes(puzzle_file)
    hash_to_word = {}
    
    # Load wordlists
    wordlists = []
    for filename in ["common_words.txt", "20k.txt", "words.txt"]:
        words = load_wordlist(filename)
        if words:
            wordlists.extend(words)
    
    # Add a small list of common words if no wordlist is found
    if not wordlists:
        wordlists = [
            "the", "and", "a", "to", "of", "in", "is", "you", "that", "it",
            "he", "was", "for", "on", "are", "as", "with", "his", "they", "I",
            "at", "be", "this", "have", "from", "or", "had", "by", "not", "but",
            "what", "all", "were", "we", "when", "your", "can", "said", "there", "use",
            "an", "each", "which", "she", "do", "how", "their", "if", "will", "up"
        ]
    
    # Add additional known words
    if additional_words:
        wordlists.extend(additional_words)
    
    # Prepare key
    key_encoded = str(key).encode('utf-8')
    
    # Try each word from wordlists
    for word in wordlists:
        hash_val = hashlib.md5(key_encoded + word.encode('utf-8')).hexdigest()
        if hash_val in hashes:
            hash_to_word[hash_val] = word
    
    # Create decoded output
    decoded = []
    unmatched = []
    
    for h in hashes:
        if h in hash_to_word:
            decoded.append(hash_to_word[h])
        else:
            decoded.append("[MISSING]")
            unmatched.append(h)
    
    # Check how many we decoded
    match_percentage = len(hash_to_word) / len(hashes) * 100
    print(f"Decoded {len(hash_to_word)} out of {len(hashes)} hashes ({match_percentage:.1f}%)")
    
    # Print decoded message with line breaks every 15 words
    message = ""
    for i, word in enumerate(decoded):
        message += word + " "
        if (i + 1) % 15 == 0:
            message += "\n"
    
    print("\nDecoded message:")
    print(message)
    
    print(f"\n{len(unmatched)} unmatched hashes:")
    for i, h in enumerate(unmatched, 1):
        print(f"{i}. {h}")

if __name__ == "__main__":
    # For PUZZLE-EASY.txt
    easy_key = 6346
    easy_puzzle = "PUZZLE-EASY.txt"
    
    # Add known specific words from our analysis
    known_words = [
        "Wednesday", "18th", "February", "wednesday", "february", 
        "North", "Carolina", "Life", "agent", "fly", "Mercy", "Lake",
        "Superior", "door", "yellow", "take", "off", "forgive", "loved", "Robert",
        "three", "days", "before", "event", "place", "little", "p.m.", "on", 
        "of", "away", "my", "own", "me", "I", "you"
    ]
    
    decode_puzzle(easy_key, easy_puzzle, known_words) 