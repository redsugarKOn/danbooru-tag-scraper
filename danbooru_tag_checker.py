import requests
import concurrent.futures
import threading
import os

# Lock for thread-safe list appending
list_lock = threading.Lock()

def get_tag_category(tag_name):
    """
    Checks the category of a given tag on Danbooru.
    """
    url = f"https://danbooru.donmai.us/tags.json?search[name]={tag_name}"
    try:
        response = requests.get(url, timeout=5) # Added timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        tags = response.json()
        if tags:
            # Assuming the first result is the most relevant one
            tag_info = tags[0]
            return tag_info.get("category")
        else:
            return None  # Tag not found
    except requests.exceptions.RequestException as e:
        # print(f"Error fetching tag {tag_name}: {e}") # Commented out to avoid excessive output
        return None

def is_general_tag(tag_name):
    """
    Checks if a tag is categorized as \'General\' on Danbooru.
    Returns a tuple (tag_name, is_general_bool).
    """
    category = get_tag_category(tag_name)
    # Category \'0\' corresponds to \'General\' based on Danbooru API documentation
    return (tag_name, category == 0)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    input_file_name = input("Please enter the name of the input tag list file (e.g., my_tags.txt): ")
    input_file = os.path.join(script_dir, input_file_name)

    output_dir = os.path.join(script_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    output_true_file = os.path.join(output_dir, "general_tags.txt")
    output_false_file = os.path.join(output_dir, "non_general_tags.txt")

    all_tags = []
    try:
        with open(input_file, "r", encoding="utf-8") as f_in:
            for line in f_in:
                tag = line.strip()
                if tag:
                    all_tags.append(tag)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}. Please make sure the file exists and the name is correct.")
        exit()

    general_tags = []
    non_general_tags = []

    total_tags = len(all_tags)
    processed_count = 0

    print(f"Starting to process {total_tags} tags...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks and store futures along with the original tag
        future_to_tag = {executor.submit(is_general_tag, tag): tag for tag in all_tags}

        for future in concurrent.futures.as_completed(future_to_tag):
            tag = future_to_tag[future]
            try:
                tag_name, is_general = future.result()
                if is_general:
                    general_tags.append(tag_name)
                    result_str = "General"
                else:
                    non_general_tags.append(tag_name)
                    result_str = "Non-General"
            except Exception as exc:
                result_str = f"Error: {exc}"
            finally:
                processed_count += 1
                print(f"Processed {processed_count}/{total_tags}: {tag} -> {result_str}")

    with open(output_true_file, "w", encoding="utf-8") as f_true:
        for tag in general_tags:
            f_true.write(tag + "\n")

    with open(output_false_file, "w", encoding="utf-8") as f_false:
        for tag in non_general_tags:
            f_false.write(tag + "\n")

    print(f"\nFinished processing all tags.\nProcessed tags from {input_file}.\nGeneral tags saved to {output_true_file}.\nNon-general tags saved to {output_false_file}.")


