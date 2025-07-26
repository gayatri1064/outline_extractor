import re


def group_multiline_candidates(lines, max_y_diff=25, max_x_diff=20, lookahead=5, font_tolerance=1.0, debug=False):
   
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
                                print(f"  Skipping line, trying next: '{lines[j]['text'][:30]}...'")
                            j += 1 
                            continue
                break

        
        merged_text = " ".join([b["text"] for b in buffer]).strip()
        if debug and len(buffer) > 1:
            print(f"  Final merged ({len(buffer)} lines): '{merged_text[:100]}...'")
        
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

def simple_text_similarity(text1, text2, threshold=0.85):
    """
    Fast text-based deduplication using word overlap instead of embeddings.
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return False
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    jaccard_similarity = intersection / union if union > 0 else 0
    return jaccard_similarity >= threshold

def classify_headings(lines, deduplicate=True, debug=False):
    lines = group_multiline_candidates(lines, debug=debug)

    font_sizes = [line["font_size"] for line in lines]
    if not font_sizes:
        return []
        
    max_font = max(font_sizes)
    avg_font = sum(font_sizes) / len(font_sizes)

    headings = []
    seen_texts = []

    for line in lines:
        text = line["text"].strip()
        
        # skip bad candidates
        if len(text.split()) <= 1 or not any(c.isalpha() for c in text):
            if debug:
                print(f" Rejected (too short/no alpha): {text}")
            continue
        
        # skip very long texts (likely paragraphs)
        if len(text.split()) > 15:
            if debug:
                print(f" Rejected (too long): {text[:50]}...")
            continue
        
        # enhanced pattern matching for structured headings
        score = 0
        
        # font size scoring
        font_ratio = line["font_size"] / max_font
        if font_ratio >= 0.9:  
            score += 2.0
        elif font_ratio >= 0.85:  
            score += 1.5
        elif font_ratio >= 0.75: 
            score += 1.0
        elif font_ratio >= 0.65: 
            score += 0.5
        
        
        # bold formatting
        if line["bold"]:
            score += 3.0
        
        # position-based scoring (top of page likely headings)
        if line["y"] < 150:
            score += 0.5
        
        # pattern-based scoring
        # check for numbered sections (1., 2.1, etc.)
        if re.match(r'^\d+\.', text) or re.match(r'^\d+\.\d+', text):
            score += 1.5
            
        # common heading words
        heading_keywords = ['introduction', 'overview', 'summary', 'conclusion', 'references', 
                           'acknowledgements', 'contents', 'history', 'background', 'objectives',
                           'requirements', 'structure', 'duration', 'audience', 'career', 'learning','options']
                           
        
        

        negative_keywords = ['signature', 'sign', 'date', 'approved', 'approval', 'name', 'designation', 'prepared by','availed','shortest route','amount','rsvp','please',]

        text_lower = text.lower() 
        if any(keyword in text_lower for keyword in heading_keywords):
         score += 0.5

        if any(neg in text_lower for neg in negative_keywords):
         score -= 5.0  # drastic reduction

         
        address_patterns = [
    r'\b\d{1,6}\s+(?:[A-Za-z]+\s)*(Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Parkway|Pkwy|Place|Pl|Square|Sq)\b',
    r'\b(?:Suite|Ste|Apt|Unit)\s*\d+\b',                                     # Suite 303, Apt 12
    r'\b[A-Z]{2}\s+\d{5}(-\d{4})?\b',                                        # US state + ZIP (e.g., CA 90210)
    r'\b[A-Z]{2}\s+[A-Z]?\d[A-Z]?\s*\d[A-Z]?\d\b',                           # Canadian postal code like M5C 1M3
    r'\b(?:Toronto|Vancouver|New York|San Francisco|Los Angeles|Chicago)\b',  # Common city names (optional)
]


        if any(re.search(pattern, text, re.IGNORECASE) for pattern in address_patterns):
          score -= 2.5  # penalise likely addresses

        date_patterns = [
    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',               # 12/03/2023, 12-03-2023
    r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',                 # 2023-03-12
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,-]*\d{1,2},?\s*\d{2,4}\b',  # March 12, 2023
    r'\b\d{1,2}[\s-]*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,-]*\d{2,4}\b',  # 12 March 2023
]
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in date_patterns):
            if debug:
                print(f" Rejected (date-like): {text}")
            continue

        
            
        # length preference for headings
        word_count = len(text.split())
        if word_count <= 5:
            score += 0.5
        elif word_count <= 8:
            score += 0.2
            
        # check if text ends with common heading patterns
        if text.strip().endswith((':', 'History', 'Contents', 'References', 'Acknowledgements')):
            score += 0.5

        # assign level based on score and patterns
        level = None
        if score >= 5.0:
            level = "H1"
        elif score >= 2.0:
            level = "H2"
        elif score >= 1.5:
            level = "H3"
        else:
            if debug:
                print(f"Low score ({score:.2f}): {text}")
            continue

        # fast deduplication using text similarity
        if deduplicate:
            is_duplicate = False
            for seen_text in seen_texts:
                if simple_text_similarity(text, seen_text, threshold=0.8):
                    is_duplicate = True
                    break
            
            if is_duplicate:
                if debug:
                    print(f" Rejected (duplicate): {text}")
                continue
            
            seen_texts.append(text)

        headings.append({
            "level": level,
            "text": text,
            "page": line["page"]
        })

        if debug:
            print(f" [{level}] {text} (Page {line['page']}, Score: {score:.2f})")

    return headings