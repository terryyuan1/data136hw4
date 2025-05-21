import hashlib
import sys

def load_hashes(puzzle_file):
    with open(puzzle_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def load_words(text_file):
    with open(text_file, 'r') as f:
        return f.read().split()

def main():
    if len(sys.argv) != 4:
        print("Usage: python final_mapping.py PUZZLE.txt source_passage.txt 9_digit_key")
        sys.exit(1)
    puzzle_file = sys.argv[1]
    passage_file = sys.argv[2]
    key = sys.argv[3]
    puzzle_hashes = load_hashes(puzzle_file)
    words = load_words(passage_file)

    # Build hash->word mapping
    hash_to_word = {}
    for word in words:
        h = hashlib.md5(key.encode('utf-8') + word.encode('utf-8')).hexdigest()
        hash_to_word[h] = word

    # Decode the puzzle
    decoded = []
    unmatched_hashes = []
    for h in puzzle_hashes:
        if h in hash_to_word:
            decoded.append(hash_to_word[h])
        else:
            decoded.append("[MISSING]")
            unmatched_hashes.append(h)

    print("Decoded paragraph:")
    print(' '.join(decoded))
    print("\nUnmatched hashes:")
    for h in unmatched_hashes:
        print(h)

    # Save for next step
    with open("unmatched_hashes.txt", "w") as f:
        for h in unmatched_hashes:
            f.write(h + '\n')
    with open("decoded_paragraph.txt", "w") as f:
        f.write(' '.join(decoded) + '\n')

if __name__ == '__main__':
    main() 