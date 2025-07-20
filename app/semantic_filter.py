from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_deduplicate(headings, threshold=0.85):
    unique = []
    seen_embeddings = []

    for h in headings:
        embedding = model.encode(h['text'], convert_to_tensor=True)
        is_duplicate = False

        for seen in seen_embeddings:
            if util.cos_sim(embedding, seen).item() >= threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            seen_embeddings.append(embedding)
            unique.append(h)

    return unique
