import hashlib
import sys
from puzzle import puzzle_key, puzzle_misspell, puzzle_easy_key, puzzle_easy_misspell

def calculate_hash(key, word):
    """Calculate MD5 hash of key + word"""
    key_str = str(key)
    key_encoded = key_str.encode('utf-8')
    word_encoded = word.encode('utf-8')
    hash_val = hashlib.md5(key_encoded + word_encoded).hexdigest()
    return hash_val

def verify_misspelling_hash(key, misspelling, puzzle_file=None, find_in_hashes=False):
    """Verify that the hash of key + misspelling appears in the puzzle file"""
    hash_val = calculate_hash(key, misspelling)
    
    print(f"Key: {key} (type: {type(key)})")
    print(f"Misspelled word: '{misspelling}' (type: {type(misspelling)})")
    print(f"MD5 hash: {hash_val}")
    
    if puzzle_file and find_in_hashes:
        # Load puzzle hashes to see if our hash is in there
        with open(puzzle_file, 'r') as f:
            hashes = [line.strip() for line in f if line.strip()]
        
        if hash_val in hashes:
            print(f"✓ Success! Hash found in puzzle file at position {hashes.index(hash_val) + 1}")
        else:
            print("✗ Hash not found in puzzle file")

def main():
    # Verify main puzzle
    print("======= MAIN PUZZLE =======")
    verify_misspelling_hash(puzzle_key, puzzle_misspell)
    
    if len(sys.argv) > 1:
        # Check if hash exists in puzzle file
        verify_misspelling_hash(puzzle_key, puzzle_misspell, sys.argv[1], True)
    
    # Verify easy puzzle
    print("\n======= EASY PUZZLE =======")
    verify_misspelling_hash(puzzle_easy_key, puzzle_easy_misspell)
    
    if len(sys.argv) > 2:
        # Check if hash exists in easy puzzle file
        verify_misspelling_hash(puzzle_easy_key, puzzle_easy_misspell, sys.argv[2], True)

if __name__ == "__main__":
    main() 