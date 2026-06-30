from pathlib import Path


def resolve_path(path, base_path):
    """Return an absolute, normalised file path, or None if not found."""
    if not path:
        return None
    p = Path(path)
    if p.is_absolute():
        return str(p) if p.exists() else None
    if base_path:
        resolved = (Path(base_path) / p).resolve()
        return str(resolved) if resolved.exists() else None
    resolved = p.resolve()
    return str(resolved) if resolved.exists() else None
