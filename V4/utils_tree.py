import os


def normalize_path(path):
    return path.replace("\\", "/")


def build_tree(root=".", excluded_files=None, excluded_dirs=None):
    tree = {}
    extensions = set()

    excluded_files = excluded_files or []
    excluded_dirs = excluded_dirs or []

    for dirpath, dirnames, filenames in os.walk(root):

        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]

        rel = os.path.relpath(dirpath, root)
        current = tree

        if rel != ".":
            for part in rel.split(os.sep):
                current = current.setdefault(part, {})

        for f in filenames:

            if f in excluded_files:
                continue

            ext = os.path.splitext(f)[1]
            if ext:
                extensions.add(ext)

            current[f] = None

    return tree, sorted(list(extensions))