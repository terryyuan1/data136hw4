import hashlib
import sys
import os
import time
import pickle
from multiprocessing import Pool, cpu_count, Manager
import threading

# Usage: python crack_puzzle.py PUZZLE.txt 4 [wordlist] [start_key] [end_key] [match_threshold]
#        python crack_puzzle.py PUZZLE-EASY.txt 4 [wordlist] [start_key] [end_key] [match_threshold]

def load_hashes(puzzle_file):
    with open(puzzle_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def load_wordlist(wordlist_file=None):
    if wordlist_file and os.path.exists(wordlist_file):
        path = wordlist_file
    elif os.path.exists('common_words.txt'):
        path = 'common_words.txt'
    elif os.path.exists('/usr/share/dict/words'):
        path = '/usr/share/dict/words'
    elif os.path.exists('20k.txt'):
        path = '20k.txt'
    else:
        raise FileNotFoundError('No wordlist found! Please provide a wordlist file.')
    with open(path, 'r') as f:
        return [w.strip() for w in f if w.strip() and w[0].isalpha()]

def try_key_range(args):
    key_start, key_end, key_format, puzzle_hashes, encoded_words, match_threshold, batch_size = args
    n_hashes = len(puzzle_hashes)
    hash_set = set(puzzle_hashes)  # Convert to set for faster lookups
    best_match = (0, None, None, None)

    # Process keys in batches for better efficiency
    for batch_start in range(key_start, key_end, batch_size):
        batch_end = min(batch_start + batch_size, key_end)
        for key_num in range(batch_start, batch_end):
            key = key_format.format(key_num)
            key_encoded = key.encode('utf-8')
            
            hash_to_word = {}
            matched_count = 0
            
            # Test all words with this key
            for word, word_encoded in encoded_words:
                h = hashlib.md5(key_encoded + word_encoded).hexdigest()
                if h in hash_set:
                    hash_to_word[h] = word
                    matched_count += 1
            
            match_ratio = matched_count / n_hashes
            
            # If at least half the hashes match, this key is promising
            if match_ratio >= 0.5:
                # Get uncracked hashes
                uncracked_hashes = [h for h in puzzle_hashes if h not in hash_to_word]
                
                # If all but one matched, we likely found the solution
                if len(uncracked_hashes) == 1:
                    return (key, hash_to_word, uncracked_hashes, True)
                
                # If this is our best match so far, remember it
                if matched_count > best_match[0]:
                    best_match = (matched_count, key, hash_to_word, uncracked_hashes)
                
                # If enough matched, print partial decode for manual inspection
                if match_ratio >= match_threshold:
                    cracked_words = [hash_to_word.get(h) for h in puzzle_hashes]
                    paragraph = ' '.join([w for w in cracked_words if w is not None])
                    print(f"\n[Partial match] Key: {key} ({matched_count}/{n_hashes} matched, {match_ratio:.1%})")
                    print('Paragraph:')
                    print(paragraph[:100] + '...' if len(paragraph) > 100 else paragraph)
            
            # Periodically check if we should save progress
            if key_num % 10000 == 0:
                if os.path.exists('stop_cracking'):
                    print(f"Stop file detected, stopping at key {key}")
                    # Return our best match so far
                    if best_match[1]:
                        return (best_match[1], best_match[2], best_match[3], False)
                    return None
    
    # After processing all keys, return the best match if it's promising
    if best_match[0] / n_hashes >= 0.4:  # Lower threshold for final return
        return (best_match[1], best_match[2], best_match[3], False)
    return None

def periodic_progress_checker(done_chunks, total_chunks, start_time, stop_event, checkpoint_file):
    last_save = start_time
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        percent = 100.0 * done_chunks[0] / total_chunks
        
        # Save checkpoint every 5 minutes
        if time.time() - last_save > 300:
            with open(checkpoint_file, 'w') as f:
                f.write(str(done_chunks[0]))
            last_save = time.time()
            print(f"Checkpoint saved: {done_chunks[0]}/{total_chunks} chunks")
        
        print(f"[Progress] {done_chunks[0]}/{total_chunks} chunks done ({percent:.2f}%), elapsed: {elapsed:.1f}s")
        
        # If we're making progress, print estimated time remaining
        if done_chunks[0] > 0:
            time_per_chunk = elapsed / done_chunks[0]
            remaining_chunks = total_chunks - done_chunks[0]
            estimated_remaining = time_per_chunk * remaining_chunks
            print(f"Estimated time remaining: {estimated_remaining:.1f}s ({estimated_remaining/3600:.1f}h)")
        
        stop_event.wait(30)  # Check more frequently

def save_checkpoint(file_path, data):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)

def load_checkpoint(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    return None

def crack_puzzle_parallel(puzzle_file, key_length, wordlist_file=None, num_chunks=2000, start_key=None, end_key=None, match_threshold=0.3, batch_size=1000):
    puzzle_hashes = load_hashes(puzzle_file)
    wordlist = load_wordlist(wordlist_file)
    
    # Pre-encode all words for better performance
    encoded_words = [(word, word.encode('utf-8')) for word in wordlist]
    
    key_format = '{:0' + str(key_length) + 'd}'
    max_key = 10 ** key_length
    if start_key is None:
        start_key = 0
    if end_key is None:
        end_key = max_key
        
    # Use smaller chunks for better progress tracking
    total_keys = end_key - start_key
    chunk_size = max(100, total_keys // num_chunks)
    num_chunks = (total_keys + chunk_size - 1) // chunk_size  # Recalculate based on actual chunk size
    
    # Try to load checkpoint
    checkpoint_file = f"crack_checkpoint_{os.path.basename(puzzle_file)}_{key_length}.pkl"
    checkpoint_simple = f"chunk_progress_{os.path.basename(puzzle_file)}_{key_length}.txt"
    checkpoint = load_checkpoint(checkpoint_file)
    done_chunks_list = []
    
    if checkpoint:
        done_chunks_list = checkpoint.get('done_chunks', [])
        print(f"Resuming from checkpoint: {len(done_chunks_list)}/{num_chunks} chunks already processed")
    
    nprocs = min(cpu_count(), 8)
    print(f"Trying keys {start_key} to {end_key-1} ({total_keys} total) using {nprocs} processes")
    print(f"Using {num_chunks} chunks of {chunk_size} keys each, batch size: {batch_size}")
    print(f"Total words to test per key: {len(wordlist)}")
    
    start_time = time.time()
    pool = Pool(nprocs)
    tasks = []
    
    # Prepare tasks, skipping already completed chunks
    for i in range(num_chunks):
        chunk_start = start_key + i * chunk_size
        chunk_end = min(start_key + (i + 1) * chunk_size, end_key)
        if chunk_start >= end_key:
            break
            
        # Skip chunks we've already processed
        if i in done_chunks_list:
            continue
            
        tasks.append((chunk_start, chunk_end, key_format, puzzle_hashes, encoded_words, match_threshold, batch_size))
    
    if not tasks:
        print("All chunks have been processed. Try with a different key range.")
        return None, None, None
    
    result = None
    manager = Manager()
    done_chunks = manager.list([len(done_chunks_list)])
    stop_event = manager.Event()
    progress_thread = threading.Thread(target=periodic_progress_checker, 
                                      args=(done_chunks, num_chunks, start_time, stop_event, checkpoint_simple))
    progress_thread.start()
    
    try:
        for res in pool.imap_unordered(try_key_range, tasks):
            chunk_idx = done_chunks[0]
            done_chunks[0] += 1
            done_chunks_list.append(chunk_idx)
            
            # Save checkpoint periodically
            if done_chunks[0] % 10 == 0:
                save_checkpoint(checkpoint_file, {'done_chunks': done_chunks_list})
            
            if res:
                key, hash_to_word, uncracked_hashes, is_full = res
                if is_full:
                    result = (key, hash_to_word, uncracked_hashes)
                    pool.terminate()
                    break
        
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt. Saving progress and shutting down gracefully...")
        save_checkpoint(checkpoint_file, {'done_chunks': done_chunks_list})
        pool.terminate()
        pool.join()
    finally:
        stop_event.set()
        progress_thread.join()
        
    print()
    if result:
        key, hash_to_word, uncracked_hashes = result
        elapsed = time.time() - start_time
        cracked_words = [hash_to_word.get(h) for h in puzzle_hashes]
        print(f"\nFound likely key: {key}")
        print(f"Unmatched hash count: {len(uncracked_hashes)}")
        paragraph = ' '.join([w for w in cracked_words if w is not None])
        print("Decoded message (paragraph):")
        print(paragraph)
        if uncracked_hashes:
            print(f"\nUncracked hashes ({len(uncracked_hashes)}):")
            for uh in uncracked_hashes[:10]:  # Show only first 10
                print(uh)
            if len(uncracked_hashes) > 10:
                print(f"...and {len(uncracked_hashes) - 10} more")
                
        # Calculate percentage of matched words
        matched_count = sum(1 for w in cracked_words if w is not None)
        print(f"Match ratio: {matched_count / len(puzzle_hashes):.2%}")
        print(f"Elapsed time: {elapsed:.2f} seconds")
        
        # Save the results to a file
        with open(f"result_{os.path.basename(puzzle_file)}_{key}.txt", 'w') as f:
            f.write(f"Key: {key}\n")
            f.write(f"Decoded paragraph: {paragraph}\n")
            f.write(f"Match ratio: {matched_count / len(puzzle_hashes):.2%}\n")
            f.write(f"Unmatched hashes ({len(uncracked_hashes)}):\n")
            for uh in uncracked_hashes:
                f.write(f"{uh}\n")
                
        return key, cracked_words, uncracked_hashes
    else:
        print("No key found!")
        return None, None, None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python crack_puzzle.py PUZZLE.txt 4 [wordlist] [start_key] [end_key] [match_threshold]\n       python crack_puzzle.py PUZZLE-EASY.txt 4 [wordlist] [start_key] [end_key] [match_threshold]")
        sys.exit(1)
    puzzle_file = sys.argv[1]
    key_length = int(sys.argv[2])
    wordlist_file = sys.argv[3] if len(sys.argv) > 3 else 'common_words.txt'
    start_key = int(sys.argv[4]) if len(sys.argv) > 4 else None
    end_key = int(sys.argv[5]) if len(sys.argv) > 5 else None
    match_threshold = float(sys.argv[6]) if len(sys.argv) > 6 else 0.3
    
    # Use smaller chunks and batch processing for better performance
    num_chunks = 2000 if key_length > 6 else 200
    batch_size = 1000 if key_length > 6 else 100
    
    print(f"Starting cracking with {num_chunks} chunks and batch size {batch_size}")
    print("Create a file named 'stop_cracking' to gracefully stop the process")
    
    crack_puzzle_parallel(
        puzzle_file, 
        key_length, 
        wordlist_file, 
        num_chunks=num_chunks, 
        start_key=start_key, 
        end_key=end_key, 
        match_threshold=match_threshold,
        batch_size=batch_size
    ) 