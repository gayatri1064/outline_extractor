import json
from difflib import SequenceMatcher

def match_ratio(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def evaluate(pred_path, gt_path, level_tolerance=1, threshold=0.85):
    with open(pred_path, encoding='utf-8') as f:
        pred = json.load(f)
    with open(gt_path, encoding='utf-8') as f:
        gt = json.load(f)

    gt_titles = [h['text'] for h in gt['outline']]
    pred_titles = [h['text'] for h in pred['outline']]

    matched = 0
    for g in gt_titles:
        for p in pred_titles:
            if match_ratio(g, p) >= threshold:
                matched += 1
                break

    precision = matched / len(pred_titles) if pred_titles else 0
    recall = matched / len(gt_titles) if gt_titles else 0
    f1 = 2 * precision * recall / (precision + recall + 1e-6)

    print(f"✅ Matched: {matched}/{len(gt_titles)}")
    print(f"📊 Precision: {precision:.2f}, Recall: {recall:.2f}, F1: {f1:.2f}")

if __name__ == "__main__":
    import sys
    evaluate(sys.argv[1], sys.argv[2])
