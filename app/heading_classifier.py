from sentence_transformers import SentenceTransformer, util
import torch
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
def group_multiline_candidates(lines, max_y_diff=25, max_x_diff=20, lookahead=5, font_tolerance=1.0, debug=False):
    """
    Improved grouping function that better handles multi-line headings.
    """
    if not lines:
        return []

    lines = sorted(lines, key=lambda l: (l["page"], l["y"], l["x"]))
    
    grouped = []
    i = 0
    
    while i < len(lines):
        buffer = [lines[i]]
        if debug:
            print(f"Starting new group with: '{lines[i]['text'][:50]}...'")
        
        j = i + 1
      
        while j < min(i + lookahead + 1, len(lines)):
            curr = lines[j]
            prev = buffer[-1]

            same_page = curr["page"] == prev["page"]
            if not same_page:
                break
                
           
            font_compatible = abs(curr["font_size"] - prev["font_size"]) <= font_tolerance
            same_bold = curr["bold"] == prev["bold"]
            
           
            x_aligned = abs(curr["x"] - prev["x"]) <= max_x_diff
            y_close = abs(curr["y"] - prev["y"]) <= max_y_diff
            
          
            curr_words = len(curr["text"].split())
            prev_words = len(prev["text"].split())
            likely_heading_parts = curr_words <= 8 and prev_words <= 8
            
            is_continuation = (same_page and font_compatible and same_bold and 
                             x_aligned and y_close and likely_heading_parts)
            
        
            text_continuation = (not prev["text"].rstrip().endswith('.') and 
                               curr["text"] and curr["text"][0].islower())
            
            if is_continuation or text_continuation:
                buffer.append(curr)
                if debug:
                    print(f"  → Added: '{curr['text'][:50]}...'")
                j += 1
            else:
                
                if j < min(i + lookahead + 1, len(lines)) - 1:
                    next_line = lines[j + 1] if j + 1 < len(lines) else None
                    if next_line and next_line["page"] == prev["page"]:
                      
                        next_font_compatible = abs(next_line["font_size"] - prev["font_size"]) <= font_tolerance
                        next_same_bold = next_line["bold"] == prev["bold"]
                        next_x_aligned = abs(next_line["x"] - prev["x"]) <= max_x_diff
                        next_y_close = abs(next_line["y"] - prev["y"]) <= max_y_diff * 1.5
                        
                        if next_font_compatible and next_same_bold and next_x_aligned and next_y_close:
                            if debug:
                                print(f"  ⏭️ Skipping line, trying next: '{lines[j]['text'][:30]}...'")
                            j += 1 
                            continue
                break

        # merge the collected lines
        merged_text = " ".join([b["text"] for b in buffer]).strip()
        if debug and len(buffer) > 1:
            print(f"  ✅ Final merged ({len(buffer)} lines): '{merged_text[:100]}...'")
        
        first_line = buffer[0]
        grouped.append({
            "text": merged_text,
            "font_size": first_line["font_size"],
            "bold": first_line["bold"],
            "x": first_line["x"],
            "y": first_line["y"],
            "page": first_line["page"]
        })

        i += len(buffer)  

    return grouped

def classify_headings(lines, deduplicate=True, debug=False):
    lines = group_multiline_candidates(lines, debug=debug)

    font_sizes = [line["font_size"] for line in lines]
    max_font = max(font_sizes)
    avg_font = sum(font_sizes) / len(font_sizes)

    headings = []
    seen = set()

    for line in lines:
        score = 0
        text = line["text"].strip()

        # Skip bad candidates
        if len(text.split()) <= 1 or not any(c.isalpha() for c in text):
            if debug:
                print(f"⛔ Rejected: {text}")
            continue

        # Heuristics
        if line["font_size"] >= max_font * 0.9:
            score += 2
        elif line["font_size"] >= avg_font * 1.5:
            score += 1
        elif line["font_size"] >= avg_font * 1.2:
            score += 0.5

        if line["bold"]:
            score += 0.5
        if len(text.split()) <= 10:
            score += 0.5
        if line["y"] < 200:
            score += 0.2

        # Assign level
        if score >= 2:
            level = "H1"
        elif score >= 1.5:
            level = "H2"
        elif score >= 1.0:
            level = "H3"
        else:
            if debug:
                print(f"⛔ Low score ({score:.2f}): {text}")
            continue

        key = (text.lower(), level, line["page"])
        if key in seen:
            continue
        seen.add(key)

        headings.append({
            "level": level,
            "text": text,
            "page": line["page"]
        })

        if debug:
            print(f"✅ [{level}] {text} (Page {line['page']})")

    # ✅ Semantic deduplication (AFTER collecting all headings)
    if deduplicate:
        unique_headings = []
        seen_embeddings = []

        for h in headings:
            text = h["text"]
            embedding = model.encode(text, convert_to_tensor=True)

            is_duplicate = False
            for seen in seen_embeddings:
                sim = util.pytorch_cos_sim(embedding, seen)[0][0].item()
                if sim > 0.88:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_headings.append(h)
                seen_embeddings.append(embedding)

        headings = unique_headings

    return headings