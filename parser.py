import os
import re
from bs4 import BeautifulSoup, Comment

print("Starting Batch HTML Parser...")

# 1. Look through the current directory for any HTML file
for file_name in os.listdir("."):
    if file_name.endswith(".html") and not file_name.startswith("cleaned_"):
        print(f"Processing file: {file_name}")
        
        # Open and load the file
        with open(file_name, "r", encoding="utf-8") as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 2. Extract comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
            
        # 3. Decompose junk layout blocks
        for tag_name in ["script", "style", "link", "header", "footer"]:
            for element in soup.find_all(tag_name):
                element.decompose()
                
        # 4. Unnest nested structural divs
        flattening = True
        while flattening:
            flattening = False
            for div in soup.find_all("div"):
                children_tags = [c for c in div.contents if c.name is not None]
                if len(children_tags) == 1 and children_tags[0].name == "div":
                    div.unwrap()
                    flattening = True
        
        # 5. Clean up excessive empty blank lines (Whitespace Optimization)
        # Converts the page structure to raw text, then uses RegEx to collapse empty rows
        raw_html_string = str(soup)
        cleaned_html_string = re.sub(r'\n\s*\n', '\n', raw_html_string)
        
        # 6. Save output with a distinct prefix
        output_name = f"cleaned_{file_name}"
        with open(output_name, "w", encoding="utf-8") as output_file:
            output_file.write(cleaned_html_string)
            
        print(f" Saved clean file as: {output_name}")

print("\nAll files processed successfully! Ready for the CLI integration.")

