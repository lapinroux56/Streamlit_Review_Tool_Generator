import streamlit as st
import os
import json

from utils_git import get_current_branch, get_commits, get_merge_base
from utils_tree import build_tree, normalize_path


# ---------------------------
# CONFIG
# ---------------------------
with open("config.json") as f:
    config = json.load(f)

EXCLUDED_FILES = config["excluded_files"]
EXCLUDED_DIRS = config["excluded_dirs"]


st.set_page_config(layout="wide")
st.title("📦 Git Review Tool V3")


# ---------------------------
# STATE
# ---------------------------
if "selected_commits" not in st.session_state:
    st.session_state.selected_commits = set()


# ---------------------------
# GIT
# ---------------------------
branch = get_current_branch()

if branch == "main":
    st.subheader(f"🌿 Branche : {branch}")
    st.info("Sur main — aucun commit spécifique à afficher.")
    commits = []
else:
    merge_base = get_merge_base(branch)

    st.subheader(f"🌿 Branche : {branch}")
    st.caption(f"Comparé à main depuis : {merge_base[:7]}")

    commits = get_commits(branch)

    st.subheader("📜 Commits")

    if branch != "main":
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Select all commits"):
                for commit in commits:
                    key = f"commit_{commit['hash']}"
                    st.session_state[key] = True
                    st.session_state.selected_commits.add(commit["hash"])

        with col2:
            if st.button("❌ Unselect all commits"):
                for commit in commits:
                    key = f"commit_{commit['hash']}"
                    st.session_state[key] = False
                st.session_state.selected_commits.clear()

    st.write(f"🔢 {len(st.session_state.selected_commits)} commits sélectionnés")

    for commit in commits:
        key = commit["hash"]
        checkbox_key = f"commit_{key}"

        # Init si absent
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = False

        with st.expander(f"{commit['hash'][:7]} - {commit['message']}"):

            st.checkbox(
                "Sélectionner",
                key=checkbox_key
            )

            st.write(f"📅 {commit['date']}")

            st.write("📂 Fichiers :")
            for f in commit["files"]:
                st.write(f"- {f}")

        # 🔥 Sync état réel → selected_commits
        if st.session_state[checkbox_key]:
            st.session_state.selected_commits.add(key)
        else:
            st.session_state.selected_commits.discard(key)


# ---------------------------
# 🔥 CALCUL CENTRAL (NOUVEAU)
# ---------------------------
selected_files = set()

for commit in commits:
    if commit["hash"] in st.session_state.selected_commits:
        for f in commit["files"]:
            selected_files.add(normalize_path(f).lstrip("doc/"))


# ---------------------------
# FILE TREE + EXTENSIONS
# ---------------------------
tree, extensions = build_tree(
    ".",
    EXCLUDED_FILES,
    EXCLUDED_DIRS
)

st.subheader("📁 Fichiers")

selected_exts = st.multiselect(
    "Filtrer par extension",
    extensions,
    default=extensions
)


# ---------------------------
# RENDER TREE (MATCH EXACT)
# ---------------------------
def render_tree(node, path=""):
    for name, child in node.items():
        full_path = os.path.join(path, name)
        normalized = normalize_path(full_path)

        if child is None:
            ext = os.path.splitext(name)[1]

            if ext not in selected_exts:
                continue

            # 🔥 SOURCE DE VÉRITÉ = commits
            st.session_state[normalized] = (normalized in selected_files)

            # 🔥 Matching exact ici
            checked = st.checkbox(
                name,
                value=False,
                key=normalized
            )

        else:
            with st.expander(name):
                render_tree(child, full_path)


render_tree(tree)


# ---------------------------
# FORM
# ---------------------------
st.subheader("📝 Review")

review_type = st.radio(
    "Type",
    ["Light", "Full", "Certification"]
)

tags = st.multiselect(
    "Tags",
    ["Safety", "Performance", "Security", "Refactoring"]
)

comment = st.text_area("Commentaire")


# ---------------------------
# EXPORT
# ---------------------------
if st.button("🚀 Generate Review file"):

    os.makedirs("data-output", exist_ok=True)

    output = {
        "branch": branch,
        "all_commits": commits,
        "selected_commits": [
            c for c in commits if c["hash"] in st.session_state.selected_commits
        ],
        "selected_files": list(selected_files),
        "review_type": review_type,
        "tags": tags,
        "comment": comment
    }

    with open("data-output/review.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    st.success("✅ JSON généré")