import re
from typing import Optional, List

def parse_page_request(q: str):
    s = q.lower()

    m = re.search(r"last\s+(\d+)\s+page", s)
    if m:
        return ("last", int(m.group(1)))

    m = re.search(r"page(?:s)?\s*(\d+)\s*(?:-|to)\s*(\d+)", s)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if a > b:
            a, b = b, a
        return ("range", a, b)

    return None

def parse_chapter_request(q: str) -> Optional[List[int]]:
    s = q.lower()

    # chapters 2-4
    m = re.search(r"chapters?\s+(\d+)\s*-\s*(\d+)", s)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        lo, hi = min(a, b), max(a, b)
        return list(range(lo, hi + 1))

    # chapters 2,3,4
    m = re.search(r"chapters?\s+((?:\d+\s*,\s*)*\d+)", s)
    if m:
        nums = [int(x.strip()) for x in m.group(1).split(",") if x.strip().isdigit()]
        return nums if nums else None

    # chapter 2
    m = re.search(r"\bchapter\s+(\d+)\b", s)
    if m:
        return [int(m.group(1))]

    return None
