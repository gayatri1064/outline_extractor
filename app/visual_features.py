import fitz  

def extract_visual_features(pdf_path):
    """
    Extract visual features from PDF with improved error handling and feature detection.
    """
    lines = []
    doc = None
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num, page in enumerate(doc, start=1):
            blocks = page.get_text("dict")['blocks']
            for b in blocks:
                if 'lines' not in b:
                    continue
                for l in b['lines']:
                    line_text = " ".join([s['text'] for s in l['spans']]).strip()
                    if not line_text:
                        continue

              
                    font_sizes = [s['size'] for s in l['spans'] if s.get('size', 0) > 0]
                    if not font_sizes:
                        continue
                    font_size = max(font_sizes)  

                    bold = any(
                        "Bold" in s.get('font', '') or 
                        "bold" in s.get('font', '').lower() or 
                        (s.get('flags', 0) & 2**4)  
                        for s in l['spans']
                    )
                    
               
                    x_coords = [s['bbox'][0] for s in l['spans'] if len(s['bbox']) >= 4]
                    y_coords = [s['bbox'][1] for s in l['spans'] if len(s['bbox']) >= 4]
                    
                    if not x_coords or not y_coords:
                        continue
                        
                    x = min(x_coords)
                    y = min(y_coords)

                    lines.append({
                        'text': line_text,
                        'font_size': round(font_size, 1),
                        'font_name': l['spans'][0]['font'] if l['spans'] else '',
                        'bold': bold,
                        'x': round(x, 1),
                        'y': round(y, 1),
                        'page': page_num
                    })

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return []
    finally:
        if doc:
            doc.close()

    return lines