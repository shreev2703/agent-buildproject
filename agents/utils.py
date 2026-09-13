def file_to_string(path: str) -> str:
    """Read a whole text file and return its contents as one string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
