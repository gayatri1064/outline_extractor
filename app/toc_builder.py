def build_outline_hierarchy(flat_headings):
    """
    Build outline structure. For the desired output format, 
    we return a flat structure without nested children.
    """
    # Simply return the flat structure since desired output shows flat list
    return [
        {
            "level": h["level"],
            "text": h["text"], 
            "page": h["page"]
        }
        for h in flat_headings
    ]

def build_outline_hierarchy_nested(flat_headings):
    """
    Alternative: Build true hierarchical structure with children if needed.
    Use this if you want nested structure in the future.
    """
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
    """Print the outline in a readable tree format."""
    for h in outline:
        print("  " * indent + f"{h['level']} - {h['text']} (Page {h['page']})")
        if h.get("children"):
            print_outline_tree(h["children"], indent + 1)