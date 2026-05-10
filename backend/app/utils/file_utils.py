from pathlib import Path


def ensure_inside(base_dir: Path, target: Path) -> Path:
    resolved_base = base_dir.resolve()
    resolved_target = target.resolve()
    if resolved_base != resolved_target and resolved_base not in resolved_target.parents:
        raise ValueError("Path is outside the allowed directory.")
    return resolved_target


def relative_to_base(base_dir: Path, target: Path) -> str:
    return str(target.resolve().relative_to(base_dir.resolve())).replace("\\", "/")

