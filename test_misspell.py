import hashlib
import base64
import itertools

def generate_variants(word):
    """Generate variants of a word by swapping, duplicating, or removing letters"""
    variants = []
    
    # Original word
    variants.append(word)
    
    # Original word with different capitalizations
    variants.append(word.lower())
    variants.append(word.upper())
    variants.append(word.capitalize())
    
    # Common misspellings of February
    variants.extend([
        "Febrart", "Febraury", "Feburary", "Febuary", "Febraurt",
        "Febrary", "Feburaury", "Febuari", "Februrary", "Februay",
        "Februrary", "Februaru", "Frbruary", "Febrry", "Febryary",
        "Febuari", "Febuwary", "Febewary", "Febrewary", "Feburari",
    ])
    
    # Try some more variations
    base = "Februar"  # Basic part of February
    for suffix in ["y", "i", "ie", "ey", "ary", "uary", "uray", "airy", "ry"]:
        variants.append(f"Febr{suffix}")
        variants.append(f"Feb{suffix}")
    
    # Swap letters in February
    feb = list("February")
    for i in range(len(feb)-1):
        swapped = feb.copy()
        swapped[i], swapped[i+1] = swapped[i+1], swapped[i]
        variants.append("".join(swapped))
    
    # Add common typos
    for i, char in enumerate("February"):
        for replacement in "abcdefghijklmnopqrstuvwxyz":
            if replacement != char.lower():
                typo = list("February")
                typo[i] = replacement
                variants.append("".join(typo))
    
    return list(set(variants))  # Remove duplicates

def check_hash(key, word):
    """Check if hash of word with key ends with the required suffix"""
    h = hashlib.md5(str(key).encode('utf-8') + word.encode('utf-8')).hexdigest()
    # Print just the word and hash without base64 to make output cleaner
    print(f"{word}: {h}")
    return h

key = 6346
variants = generate_variants("February")
print(f"Generated {len(variants)} variants to test")

for word in variants:
    h = check_hash(key, word)
    # If we get a hash that seems close to what's in the error message
    # The error message showed a hash that ends with "6GV/"
    if 'a1' in h and 'e5' in h:  # Just some elements from the error message hash
        print(f"Potential match: {word} -> {h}")

print("\nSpecial cases for the easy puzzle misspelling:")
special_cases = ["Febraury", "Feburary", "Februry", "Febuary"]
for word in special_cases:
    h = check_hash(key, word)
    print(f"Special case: {word} -> {h}") 