# danbooru-tag-scraper

A Python script tool for scraping tag description information from Danbooru. This tool provides the following features:

+ Batch retrieval of tag descriptions from Danbooru
+ Automatic cleanup of empty wiki entries
+ Extraction of the most relevant descriptive content while removing redundant metadata
+ Real-time saving of results
+ Optional pre-filtering of non-General tags for special purposes
+ Segmenting known tag lists
+ 
## Update

**2025-7-1**
Merge the tag filter and main functionality into `danbooru_scraper_M.py`, now allowing for multithreading processing and tag filtering through a single program.

---

## System Requirements

- Python 3.6+
- `requests` library

## Installation Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/redsugarKOn/danbooru-tag-scraper.git
   cd danbooru-tag-scraper
   ```

2. Install required dependencies:

   ```bash
   pip install requests
   ```

## Usage

**danbooru_scraper.py[OLD]**

1. Create an input file (tag_list.txt) with one tag per line

2. Run the script:

   ```bash
   python danbooru_scraper.py tag_list.txt
   ```

3. View results A tag_descriptions_refined.txt file will be generated in the current directory

   + Tags without created descriptions will be skipped

   + The script saves data in real-time but does not provide crash recovery


---

**danbooru_tag_checker.py**

Used for bulk classification of tag lists into "General" and non-"General" tags. Automatically separates input tags into two categories.

1. reate an input file (e.g., my_tags.txt) with one tag per line

2. Run the script:

   ```bash
   python danbooru_tag_checker.py
   ```

3. Enter the tag filename when prompted (e.g., my_tags.txt)

4. View results:

  + General tags saved in outputs/general_tags.txt
    Non-General tags saved in outputs/non_general_tags.txt

---

**split_tags.py**

Used for splitting tag lists into chunks

1. Create an input file (tag_list.txt) with one tag per line

2. Run the script:

   ```bash
   python split_tags.py
   ```

3. Select the TXT file to split in the file chooser dialog

4. Edit the script to modify chunk size (default: 1000 tags per file):

   ```python
   chunk_size=1000
   ```

5. Check output folder Example output structure：

   ```
   output_tags/
       ├── tags_part_0001.txt
       ├── tags_part_0002.txt
       └── tags_part_0003.txt
   ```

---



## License

This project is licensed under the MIT License - see the LICENSE file for details.
