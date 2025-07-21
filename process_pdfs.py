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
            # Extract visual features
            lines = extract_visual_features(input_path)
            print(f"Extracted {len(lines)} visual lines")

            # Classify headings with improved logic
            headings = classify_headings(lines, deduplicate=False, debug=False)  # Handle deduplication separately
            print(f"Found {len(headings)} heading candidates")

            # Apply semantic deduplication (now fast)
            headings = semantic_deduplicate(headings)
            print(f"After semantic deduplication: {len(headings)} headings")

            # Build outline (flat structure to match desired output)
            outline = build_outline_hierarchy(headings)

            # Create output JSON
            output_json = {
                "title": headings[0]["text"] if headings else "Untitled Document",
                "outline": outline
            }

            # Save to file
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_json, f, indent=2, ensure_ascii=False)

            print(f"Saved structured outline to {output_path}")
            
            # Print summary for debugging
            print("\nExtracted headings:")
            for h in headings:
                print(f"  {h['level']}: {h['text']} (Page {h['page']})")

        except Exception as e:
            print(f"Failed to process {filename}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    process_all_pdfs()