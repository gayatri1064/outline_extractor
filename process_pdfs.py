import os
import json
from app.visual_features import extract_visual_features
from app.heading_classifier import classify_headings
from app.toc_builder import build_outline_hierarchy
from app.semantic_filter import semantic_deduplicate


INPUT_DIR = "input"
OUTPUT_DIR = "output"

def process_all_pdfs():
    if not os.path.exists(INPUT_DIR):
        print(f"Input directory '{INPUT_DIR}' not found.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print(f"No PDF files found in '{INPUT_DIR}'")
        return

    for filename in pdf_files:
        input_path = os.path.join(INPUT_DIR, filename)
        output_filename = os.path.splitext(filename)[0] + ".json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        print(f"\nProcessing: {filename}")
        try:
            lines = extract_visual_features(input_path)
            print(f"Extracted {len(lines)} visual lines")

            headings = classify_headings(lines, deduplicate=True, debug=False)
            print(f"Found {len(headings)} heading candidates")

            headings = semantic_deduplicate(headings)
            print(f"After semantic deduplication: {len(headings)} headings")

            outline = build_outline_hierarchy(headings)

            output_json = {
                "title": headings[0]["text"] if headings else "Untitled Document",
                "outline": outline
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_json, f, indent=2, ensure_ascii=False)

            print(f"Saved structured outline to {output_path}")

        except Exception as e:
            print(f"Failed to process the pdfs!!! {filename}: {e}")

if __name__ == "__main__":
    process_all_pdfs()
