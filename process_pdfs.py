import os
import json
from app.visual_features import extract_visual_features
from app.heading_classifier import classify_headings
from app.toc_builder import build_outline_hierarchy, print_outline_tree

PDF_PATH = "sample_dataset/pdfs/policy_doc.pdf"
OUTPUT_PATH = "sample_dataset/outputs/outline.json"

lines = extract_visual_features(PDF_PATH)
print(f"Extracted {len(lines)} lines from {PDF_PATH}")


with open("output/visual_lines.json", "w", encoding="utf-8") as f:
    json.dump(lines, f, indent=2, ensure_ascii=False)
print("Saved visual features to output/visual_lines.json")


headings = classify_headings(lines, deduplicate=True, debug=True)
print(f" Found {len(headings)} heading candidates")


outline = build_outline_hierarchy(headings)


output_json = {
    "title": headings[0]["text"] if headings else "Untitled Document",
    "outline": outline
}

with open("output/outline.json", "w", encoding="utf-8") as f:
    json.dump(output_json, f, indent=2, ensure_ascii=False)
print("Saved structured outline to output/outline.json")

print(f"\nSaved structured outline to {OUTPUT_PATH}")
