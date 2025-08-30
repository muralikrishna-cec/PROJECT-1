import os
import zipfile
import tempfile
import shutil
import requests

# Supported extensions → language mapping
SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".js": "javascript"
}

def is_allowed(filename):
    """
    Check if a file has an allowed extension.
    """
    _, ext = os.path.splitext(filename)
    return ext in SUPPORTED_EXTENSIONS


def detect_language(filename):
    """
    Detect programming language from file extension.
    Returns None if not supported.
    """
    _, ext = os.path.splitext(filename)
    return SUPPORTED_EXTENSIONS.get(ext, None)


def extract_zip(zip_path, extract_to=None):
    """
    Extracts a zip file to a given directory.
    Returns the path to the extracted folder.
    """
    if extract_to is None:
        extract_to = tempfile.mkdtemp(prefix="batch_zip_")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    return extract_to


def download_github_repo(repo_url, extract_to=None):
    """
    Downloads a GitHub repo as zip and extracts it.
    Supports URLs like: https://github.com/user/repo
    Returns extracted folder path.
    """
    if repo_url.endswith("/"):
        repo_url = repo_url[:-1]
    zip_url = repo_url + "/archive/refs/heads/main.zip"

    if extract_to is None:
        extract_to = tempfile.mkdtemp(prefix="batch_repo_")

    zip_path = os.path.join(extract_to, "repo.zip")

    response = requests.get(zip_url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Failed to download repo: {response.status_code}")

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return extract_zip(zip_path, extract_to)


def list_code_files(base_path):
    """
    Recursively collects supported code files from a directory.
    Returns list of (filepath, language).
    """
    collected_files = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if is_allowed(file):
                lang = detect_language(file)
                collected_files.append((os.path.join(root, file), lang))
    return collected_files


def cleanup_temp(path):
    """Safely delete a temporary folder."""
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
