import logging
import re
from pathlib import Path
from bs4 import BeautifulSoup, Comment

# Configure logging at the entry point of your script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_html_directory(target_dir: str | Path = ".") -> None:
    """
    Scans a directory for HTML files, strips out tracking tags/comments,
    unnests structural wrappers, and saves optimized output copies.
    """
    directory = Path(target_dir)
    logger.info(f"Starting Batch HTML Parser scanning directory: {directory.resolve()}")

    # 4. Using pathlib glob to find html targets safely
    for file_path in directory.glob("*.html"):
        if file_path.name.startswith("cleaned_"):
            continue
            
        logger.info(f"Processing file: {file_path.name}")
        
        # Read the file text directly using pathlib
        html_content = file_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 2. Replaced extract() with decompose() as they behave identically here
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.decompose()
            
        # 3. Clean up unwanted layout tags
        for tag_name in ["script", "style", "link", "header", "footer"]:
            for element in soup.find_all(tag_name):
                element.decompose()
                
        # Flatten nested styling wrappers
        flattening = True
        while flattening:
            flattening = False
            for div in soup.find_all("div"):
                children_tags = [c for c in div.contents if c.name is not None]
                if len(children_tags) == 1 and children_tags[0].name == "div":
                    div.unwrap()
                    flattening = True
        
        # Optimize vertical empty line spacing
        raw_html_string = str(soup)
        cleaned_html_string = re.sub(r'\n\s*\n', '\n', raw_html_string)
        
        # Save output file cleanly via pathlib path math
        output_file_path = directory / f"cleaned_{file_path.name}"
        output_file_path.write_text(cleaned_html_string, encoding="utf-8")
        
        # 3. Utilizing logging instead of print calls
        logger.info(f"Saved clean file as: {output_file_path.name}")

if __name__ == "__main__":
    clean_html_directory()
