def simple_text_similarity(text1, text2, threshold=0.8):
    """
    Fast Jaccard similarity for text deduplication.
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return False

    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    jaccard_similarity = intersection / union if union > 0 else 0

    return jaccard_similarity >= threshold


def semantic_deduplicate(headings, threshold=0.8):
    """
    Deduplicate headings, optionally respecting language boundaries.
    """
    unique = []
    seen = []

    for h in headings:
        text = h['text']
        
        is_duplicate = False

        for seen_h in seen:
            
                if simple_text_similarity(text, seen_h['text'], threshold):
                    is_duplicate = True
                    break

        if not is_duplicate:
            seen.append(h)
            unique.append(h)

    return unique


def fast_semantic_deduplicate(headings, threshold=0.85):
  
    import re

    def preprocess_text(text):
        text = re.sub(r'\d+\.?\d*', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text.lower().strip()

    unique = []
    seen = []

    for h in headings:
        text = preprocess_text(h['text'])
      
        words = set(text.split())

        is_duplicate = False
        for seen_h in seen:
           
                seen_words = set(preprocess_text(seen_h['text']).split())
                overlap = len(words.intersection(seen_words))
                total = len(words.union(seen_words))
                if total > 0 and (overlap / total) >= threshold:
                    is_duplicate = True
                    break

        if not is_duplicate:
            seen.append(h)
            unique.append(h)

    return unique
