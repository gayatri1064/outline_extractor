def build_outline_hierarchy(flat_headings):
   
    return [
        {
            "level": h["level"],
            "text": h["text"],
            "page": h["page"]
            
        }
        for h in flat_headings
    ]


def build_outline_hierarchy_nested(flat_headings):
  
    outline = []
    stack = []

    def heading_rank(level):
        return {"H1": 1, "H2": 2, "H3": 3}.get(level, 99)

    for h in flat_headings:
        node = {
            "level": h["level"],
            "text": h["text"],
            "page": h["page"],
            "children": []
        }

        while stack and heading_rank(stack[-1]["level"]) >= heading_rank(h["level"]):
            stack.pop()

        if not stack:
            outline.append(node)
        else:
            stack[-1]["children"].append(node)

        stack.append(node)

    return outline


def print_outline_tree(outline, indent=0):
   
    for h in outline:
        print("  " * indent + f"{h['level']} - {h['text']} (Page {h['page']})")
        if h.get("children"):
            print_outline_tree(h["children"], indent + 1)
