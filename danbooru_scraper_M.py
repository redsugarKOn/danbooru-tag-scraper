import os
import requests
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_tag_category(tag_name):
    """
    Checks the category of a given tag on Danbooru.
    """
    url = f"https://danbooru.donmai.us/tags.json?search[name]={tag_name}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        tags = response.json()
        if tags:
            tag_info = tags[0]
            return tag_info.get("category")
        return None
    except Exception as e:
        print(f"Error fetching tag category for {tag_name}: {e}")
        return None

def clean_description(description, tag_name):
    # Remove sections starting with 'h4.' and their content
    description = re.sub(r'h4\..*?(?=\n\n|\Z)', '', description, flags=re.DOTALL)
    # Remove [[ and ]] and their content, but keep the text inside, handling '|' as well
    description = re.sub(r'\[\[(.*?)(?:\|.*?)?\]\]', r'\1', description)
    # Remove {{ and }} and their content, but keep the text inside, handling '|' as well
    description = re.sub(r'\{\{(.*?)(?:\|.*?)?\}\}\s*\\?', r'\1', description)
    # Remove [b] and [/b]
    description = description.replace('[b]', '').replace('[/b]', '')
    # Remove [i] and [/i]
    description = description.replace('[i]', '').replace('[/i]', '')

    # Remove the specific phrase "Note: This tag is automatically added to images."
    description = description.replace('Note: This tag is automatically added to images.', '').strip()
    # Remove the specific phrase "Note: This tag is help:autotags added to images."
    description = description.replace('Note: This tag is help:autotags added to images.', '').strip()
    # Remove tag name prefix
    if description.lower().startswith(tag_name.lower()):
        description = description[len(tag_name):].strip()
        if description.startswith(':'):
            description = description[1:].strip()
    
    # Simplify whitespace
    description = re.sub(r'\s+', ' ', description.replace('\n', ' ')).strip()
    
    # Extract first two sentences
    sentences = re.findall(r'[^.!?]*[.!?]', description)
    if len(sentences) >= 2:
        return (sentences[0] + sentences[1]).strip()
    return description

def get_tag_description(tag_name):
    """Fetch and clean tag description from Danbooru wiki"""
    url = f"https://danbooru.donmai.us/wiki_pages.json?search[title]={tag_name}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                raw_description = data[0].get('body', 'No description found.')
                return clean_description(raw_description, tag_name)
        return None
    except Exception as e:
        print(f"Error fetching description for {tag_name}: {e}")
        return None

def process_tag(tag, output_lock, skipped_lock, output_file, skipped_file, counter_lock, processed_count, total_count):
    """Process a single tag and write results with thread-safe locks"""
    with counter_lock:
        processed_count[0] += 1
        current_count = processed_count[0]
        print(f"[{current_count}/{total_count}] Processing: {tag}")
    
    # Step 1: Check if it's a general tag
    category = get_tag_category(tag)
    
    if category != 0:  # Not general
        skip_reason = f"{tag} (category {category})"
        with skipped_lock:
            skipped_file.write(skip_reason + "\n")
            skipped_file.flush()
        with counter_lock:
            print(f"  - Skipped: {skip_reason}")
        return None
    
    # Step 2: Fetch description for general tags
    description = get_tag_description(tag)
    
    if description:
        entry = f"{tag}: {description}\n\n"
        with output_lock:
            output_file.write(entry)
            output_file.flush()
        with counter_lock:
            print(f"  ✓ Saved: {tag}")
        return tag
    else:
        skip_reason = f"{tag} (no description)"
        with skipped_lock:
            skipped_file.write(skip_reason + "\n")
            skipped_file.flush()
        with counter_lock:
            print(f"  ! Skipped: {skip_reason}")
        return None

def process_tags(input_file_path, max_workers=5):
    """Process tags concurrently using multiple threads"""
    # Prepare output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    # Read input tags
    try:
        with open(input_file_path, "r", encoding="utf-8") as f:
            all_tags = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    total_count = len(all_tags)
    print(f"Starting processing of {total_count} tags with {max_workers} workers...")
    
    # Prepare output files
    output_path = os.path.join(output_dir, "general_tag_descriptions.txt")
    skipped_path = os.path.join(output_dir, "skipped_tags.txt")
    
    # Create locks for thread-safe writing
    output_lock = threading.Lock()
    skipped_lock = threading.Lock()
    counter_lock = threading.Lock()
    
    # Counter for processed tags
    processed_count = [0]
    general_count = [0]
    
    with open(output_path, "w", encoding="utf-8") as output_file, \
         open(skipped_path, "w", encoding="utf-8") as skipped_file:
        
        # Write headers
        output_file.write("General Tag Descriptions\n")
        output_file.write("=========================\n\n")
        skipped_file.write("Skipped Tags\n")
        skipped_file.write("============\n\n")
        output_file.flush()
        skipped_file.flush()
        
        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for tag in all_tags:
                # Submit tasks to the thread pool
                future = executor.submit(
                    process_tag,
                    tag,
                    output_lock,
                    skipped_lock,
                    output_file,
                    skipped_file,
                    counter_lock,
                    processed_count,
                    total_count
                )
                futures.append(future)
                # Add small delay between task submissions to avoid overwhelming server
                time.sleep(0.05)
            
            # Wait for all futures to complete and count successful general tags
            for future in as_completed(futures):
                if future.result() is not None:
                    general_count[0] += 1
    
    print("\nProcessing complete!")
    print(f"General tags processed: {general_count[0]}")
    print(f"Output file: {output_path}")
    print(f"Skipped tags saved to: {skipped_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_name = input("Enter input tag list filename (e.g., tags.txt): ")
    input_file_path = os.path.join(script_dir, input_file_name)
    
    # Get number of workers with validation
    while True:
        try:
            workers_input = input("Enter number of concurrent workers (default 5, max 20): ")
            max_workers = int(workers_input) if workers_input.strip() else 5
            if 1 <= max_workers <= 20:
                break
            else:
                print("Please enter a number between 1 and 20.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    if not os.path.exists(input_file_path):
        print(f"Error: File not found - {input_file_path}")
    else:
        process_tags(input_file_path, max_workers)