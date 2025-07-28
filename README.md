This project extracts structured information from PDFs, including document titles and hierarchical outlines (headings), with logic designed to match Adobe’s behavior as closely as possible.



##Approach

The extraction pipeline includes:

1. **Visual Feature Extraction**
   - Extracts lines of text from the PDF using position (`x`, `y`), font size, boldness, and page number.
   - Groups multi-line heading candidates based on visual alignment and spacing.

2. **Heading Classification**
   - Assigns heading levels (`H1`, `H2`, `H3`) based on visual prominence (font size, bold, position).
   - Filters out noise such as date lines, signature blocks, and short field labels.
   - Optionally deduplicates similar headings using Jaccard similarity.

3. **Language Detection**
   - Attempts to detect the language of each heading using `langdetect`, with fallback heuristics (e.g., all-caps = English).
   - Final output strips out the `language` field for simplicity and alignment with Adobe's behavior.

4. **Outline Building**
   - Constructs a hierarchical structure (`outline`) from the list of classified headings.
   - Suppresses outlines for documents that resemble forms (e.g., mostly short field labels like "S.No", "Age", "Rs.") to match Adobe behavior.

5. **Postprocessing**
   - Title is inferred from the top-most meaningful line or top heading (based on visual prominence).
   - Page numbers are corrected to align with human-readable numbering (matching Adobe).

---

##Models & Libraries Used

PyMuPDF (fitz)
Used to parse PDF files and extract text lines along with their font size, position (x, y), page number, and styling information such as boldness.

langdetect
Provides lightweight language detection for text spans, used to support multilingual heading recognition.

sentence-transformers (CrossEncoder)
Optionally used for semantic similarity during deduplication of headings. Helps identify near-duplicate headings even if wording differs.

difflib (SequenceMatcher)
A built-in Python module used for simple string similarity matching, particularly for matching headings to the title.

Standard Python Libraries
Includes os, re, json, collections, etc., used for file handling, regular expressions, data manipulation, and serialization.





# Build & Run Instructions

###1. Install Dependencies

Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
python process_pdfs.py