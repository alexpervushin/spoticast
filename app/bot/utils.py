def url_encode(text: str) -> str:
    """Simple URL encoding for search parameters"""
    return text.replace(" ", "+").replace("&", "%26").replace("?", "%3F")
