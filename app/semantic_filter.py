def simple_text_similarity(text1, text2, threshold=0.8):
    """
    Fast text-based deduplication using word overlap instead of embeddings.
    Much faster than sentence transformers for hackathon constraints.
    """
    # Normalize texts
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return False
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    jaccard_similarity = intersection / union if union > 0 else 0
    return jaccard_similarity >= threshold

def semantic_deduplicate(headings, threshold=0.8):
    """
    Fast deduplication using word overlap instead of sentence transformers.
    This removes the heavy model dependency and speeds up processing significantly.
    """
    unique = []
    seen_texts = []

    for h in headings:
        text = h['text']
        is_duplicate = False

        for seen_text in seen_texts:
            if simple_text_similarity(text, seen_text, threshold):
                is_duplicate = True
                break

        if not is_duplicate:
            seen_texts.append(text)
            unique.append(h)

    return unique

# Alternative: If you still want to use embeddings but need speed, 
# here's a lighter approach with basic word embeddings
def fast_semantic_deduplicate(headings, threshold=0.85):
    """
    Alternative fast semantic deduplication using simple word overlap
    and basic text processing techniques.
    """
    import re
    
    def preprocess_text(text):
        # Remove numbers, punctuation, convert to lowercase
        text = re.sub(r'\d+\.?\d*', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text.lower().strip()
    
    unique = []
    processed_texts = []

    for h in headings:
        processed = preprocess_text(h['text'])
        words = set(processed.split())
        
        is_duplicate = False
        for seen_words in processed_texts:
            # Calculate word overlap
            overlap = len(words.intersection(seen_words))
            total = len(words.union(seen_words))
            
            if total > 0 and (overlap / total) >= threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            processed_texts.append(words)
            unique.append(h)
    
    return unique