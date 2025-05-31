# Course Content Downloader
# This script downloads a GitHub repository as a ZIP file.
#
# Content: https://github.com/sanand0/tools-in-data-science-public/tree/tds-2025-01

import argparse
import os
import shutil
import tempfile
import zipfile
from urllib.parse import urlparse
import requests


def download_repo_zip(repo_url, ref, is_commit, dest_path):
    """
    Download the repository ZIP from GitHub for the given branch or commit.
    """
    # Determine correct URL based on branch or commit
    repo_url = repo_url.rstrip("/")
    if is_commit:
        zip_url = f"{repo_url}/archive/{ref}.zip"
        print(f"Downloading commit {ref} from {zip_url}...")
    else:
        zip_url = f"{repo_url}/archive/refs/heads/{ref}.zip"
        print(f"Downloading branch '{ref}' from {zip_url}...")

    resp = requests.get(zip_url, stream=True)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Saved ZIP to {dest_path}")


def extract_zip(zip_path, extract_to):
    """Extract ZIP file to the specified directory."""
    print(f"Extracting {zip_path} to {extract_to}...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_to)
    print("Extraction complete.")


def keep_only_md(root_dir):
    """Remove all non-.md files and delete empty directories."""
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Remove non-md files
        for fname in filenames:
            if (
                not fname.lower().endswith(".md")
                or fname.lower() == "readme.md"
                or "sidebar" in fname.lower()
            ):
                file_path = os.path.join(dirpath, fname)
                os.remove(file_path)
                # print(f"Removed file: {file_path}")

        # Remove empty directories
        if not os.listdir(dirpath):
            os.rmdir(dirpath)
            # print(f"Removed empty directory: {dirpath}")


def parse_args():
    p = argparse.ArgumentParser(
        description="Download a GitHub repo as ZIP (branch or specific commit), extract it, and keep only .md files."
    )
    group = p.add_mutually_exclusive_group()
    group.add_argument("--branch", help="Branch name to download (default: main).")
    group.add_argument("--commit", help="Specific commit SHA to download.")
    p.add_argument(
        "repo_url", help="GitHub repository URL (e.g., https://github.com/user/repo)"
    )
    p.add_argument(
        "--output", default=None, help="Output directory (default: <repo>-<ref>)"
    )
    args = p.parse_args()

    # Set default branch if neither branch nor commit is provided
    if args.branch is None and args.commit is None:
        args.branch = "main"
    return args


def main():
    args = parse_args()

    # Determine repo name and ref
    parsed = urlparse(args.repo_url)
    repo_name = os.path.basename(parsed.path)
    is_commit = args.commit is not None
    ref = args.commit if is_commit else args.branch
    out_dir = args.output or f"{repo_name}-{ref}"

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, f"{repo_name}.zip")
        download_repo_zip(args.repo_url, ref, is_commit, zip_path)
        extract_zip(zip_path, tmp)

        # Find extracted folder
        # GitHub names branch archives as repo-ref and commit archives as repo-<short-sha>
        extracted_folder = None
        for item in os.listdir(tmp):
            if os.path.isdir(os.path.join(tmp, item)):
                extracted_folder = os.path.join(tmp, item)
                break

        if not extracted_folder:
            raise FileNotFoundError("Could not locate extracted directory.")

        # Move extracted contents to output directory
        if os.path.exists(out_dir):
            print(f"Removing existing directory {out_dir}...")
            shutil.rmtree(out_dir)
        shutil.move(extracted_folder, out_dir)
        print(f"Moved contents to {out_dir}")

    keep_only_md(out_dir)
    print("Done. Only .md files remain.")


if __name__ == "__main__":
    main()
