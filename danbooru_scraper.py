import os
import argparse
import requests
import json
import re

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

    # Remove the tag name from the beginning of the description if it exists
    if description.lower().startswith(tag_name.lower()):
        if len(description) == len(tag_name) or (len(description) > len(tag_name) and not description[len(tag_name)].isalnum()):
            description = description[len(tag_name):].strip()
            if description.startswith(':'):
                description = description[1:].strip()

    # Replace all newlines with a single space
    description = description.replace('\n', ' ')
    # Replace multiple spaces with a single space
    description = re.sub(r'\s+', ' ', description).strip()

    # Extract up to the first two sentences
    sentences = re.findall(r'[^.!?]*[.!?]', description)
    if len(sentences) >= 2:
        extracted_text = (sentences[0] + sentences[1]).strip()
    elif len(sentences) == 1:
        extracted_text = sentences[0].strip()
    else:
        extracted_text = description.strip()

    return extracted_text

def get_tag_description(tag_name):
    url = f"https://danbooru.donmai.us/wiki_pages.json?search[title]={tag_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            raw_description = data[0].get('body', 'No description found.')
            return clean_description(raw_description, tag_name)
    return None

def main():
    parser = argparse.ArgumentParser(description='Scrape tag descriptions from Danbooru.')
    parser.add_argument('input_file', type=str, help='Path to the input text file containing tags, one per line.')
    args = parser.parse_args()

    tags = []
    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            tags = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Input file not found at {args.input_file}")
        return

    total_tags = len(tags)
    output_file = os.path.join(os.getcwd(), 'tag_descriptions_refined.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, tag in enumerate(tags):
            print(f"Processing tag {i+1}/{total_tags}: {tag}")
            description = get_tag_description(tag)
            if description:
                f.write(f"{tag}: {description}\n\n")
                f.flush()
                os.fsync(f.fileno())
            else:
                print(f"Tag \'{tag}\' filtered out (no description found).")
    print(f"Scraping complete. Descriptions saved to {output_file}")

if __name__ == "__main__":
    main()


