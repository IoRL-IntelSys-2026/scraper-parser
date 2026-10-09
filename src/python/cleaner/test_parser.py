import re
from pathlib import Path
from parser import clean_html_directory

def test_clean_html(tmp_path: Path) -> None:
    # 1. Create a dummy uncleaned HTML page inside a temporary testing folder
    input_file = tmp_path / "example.html"
    input_file.write_text("""<html>
  <head>
    <script>alert("this is a test");</script>
     <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  </head>
  <body>
    <div>
      <div>
        <div>
          <p>Hello</p>
        </div>
      </div>
    </div>
    <script>alert("this is a test");</script>
  </body>
</html>""", encoding="utf-8")

    # 2. Run your cleaning function on the test folder
    clean_html_directory(target_dir=tmp_path)
    
    # 3. Verify the script stripped elements and flattened the structure properly
    output_file = tmp_path / "cleaned_example.html"
    assert output_file.exists(), "The cleaned file output was not generated."
    
    def normalize_whitespace(text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()

    actual_output = output_file.read_text(encoding="utf-8")
    
    # Matches BeautifulSoup's attribute order and structural unnesting limit
    expected_output = """<html>
  <head>
     <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  </head>
  <body>
    <div>
      <p>Hello</p>
    </div>
  </body>
</html>"""

    assert normalize_whitespace(actual_output) == normalize_whitespace(expected_output)
