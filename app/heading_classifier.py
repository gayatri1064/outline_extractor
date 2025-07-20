def group_multiline_candidates(lines, max_y_diff=25, max_x_diff=20, lookahead=5, font_tolerance=1.0, debug=False):
    """
    Improved grouping function that better handles multi-line headings.
    """
    if not lines:
        return []

    # Sort lines by page, then by y-coordinate, then by x-coordinate
    lines = sorted(lines, key=lambda l: (l["page"], l["y"], l["x"]))
    
    grouped = []
    i = 0
    
    while i < len(lines):
        buffer = [lines[i]]
        if debug:
            print(f"Starting new group with: '{lines[i]['text'][:50]}...'")
        
        j = i + 1
        
        # Look ahead for potential continuation lines
        while j < min(i + lookahead + 1, len(lines)):
            curr = lines[j]
            prev = buffer[-1]

            # Basic compatibility checks
            same_page = curr["page"] == prev["page"]
            if not same_page:
                break
                
            # Font compatibility (with tolerance)
            font_compatible = abs(curr["font_size"] - prev["font_size"]) <= font_tolerance
            same_bold = curr["bold"] == prev["bold"]
            
            # Position checks
            x_aligned = abs(curr["x"] - prev["x"]) <= max_x_diff
            y_close = abs(curr["y"] - prev["y"]) <= max_y_diff
            
            # Text length heuristic - short lines are more likely to be part of headings
            curr_words = len(curr["text"].split())
            prev_words = len(prev["text"].split())
            likely_heading_parts = curr_words <= 8 and prev_words <= 8
            
            # Check if this looks like a continuation
            is_continuation = (same_page and font_compatible and same_bold and 
                             x_aligned and y_close and likely_heading_parts)
            
            # Additional check: if previous line doesn't end with period and current line starts with lowercase
            # it's likely a continuation
            text_continuation = (not prev["text"].rstrip().endswith('.') and 
                               curr["text"] and curr["text"][0].islower())
            
            if is_continuation or text_continuation:
                buffer.append(curr)
                if debug:
                    print(f"  → Added: '{curr['text'][:50]}...'")
                j += 1
            else:
                # Check if we should skip this line and continue looking
                # (for cases where there might be a small gap)
                if j < min(i + lookahead + 1, len(lines)) - 1:
                    next_line = lines[j + 1] if j + 1 < len(lines) else None
                    if next_line and next_line["page"] == prev["page"]:
                        # Check if next line might be a better continuation
                        next_font_compatible = abs(next_line["font_size"] - prev["font_size"]) <= font_tolerance
                        next_same_bold = next_line["bold"] == prev["bold"]
                        next_x_aligned = abs(next_line["x"] - prev["x"]) <= max_x_diff
                        next_y_close = abs(next_line["y"] - prev["y"]) <= max_y_diff * 1.5
                        
                        if next_font_compatible and next_same_bold and next_x_aligned and next_y_close:
                            if debug:
                                print(f"  ⏭️ Skipping line, trying next: '{lines[j]['text'][:30]}...'")
                            j += 1  # Skip current line and try next
                            continue
                break

        # Merge the collected lines
        merged_text = " ".join([b["text"] for b in buffer]).strip()
        if debug and len(buffer) > 1:
            print(f"  ✅ Final merged ({len(buffer)} lines): '{merged_text[:100]}...'")
        
        # Create merged entry with properties from the first line
        first_line = buffer[0]
        grouped.append({
            "text": merged_text,
            "font_size": first_line["font_size"],
            "bold": first_line["bold"],
            "x": first_line["x"],
            "y": first_line["y"],
            "page": first_line["page"]
        })

        i += len(buffer)  # Skip the merged lines

    return grouped

def classify_headings(lines, deduplicate=True, debug=False):
    """
    Classifies grouped lines into headings (H1, H2, H3) using heuristics.
    """
    lines = group_multiline_candidates(lines, debug=debug)

    font_sizes = [line["font_size"] for line in lines]
    max_font = max(font_sizes)
    avg_font = sum(font_sizes) / len(font_sizes)

    headings = []
    seen = set()

    for line in lines:
        score = 0
        text = line["text"].strip()

        # 🔎 Filter: Ignore junk lines
        if len(text.split()) <= 1:
            if debug:
                print(f"⛔ Too short: {text}")
            continue
        if not any(c.isalpha() for c in text):
            if debug:
                print(f"⛔ Not enough alphabets: {text}")
            continue

        # 🧠 Heading heuristics
        if line["font_size"] >= max_font * 0.9:
            score += 2  # H1
        elif line["font_size"] >= avg_font * 1.5:
            score += 1  # H2
        elif line["font_size"] >= avg_font * 1.2:
            score += 0.5  # H3

        if line["bold"]:
            score += 0.5
        if len(text.split()) <= 10:
            score += 0.5
        if line["y"] < 200:
            score += 0.2

        # 🏷️ Final classification
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

        key = (text.lower(), level, line["page"])  # 🛡️ prevent cross-page duplicates
        if deduplicate and key in seen:
            continue
        seen.add(key)

        headings.append({
            "level": level,
            "text": text,
            "page": line["page"]
        })

        if debug:
            print(f"✅ [{level}] {text} (Page {line['page']})")

    return headings
