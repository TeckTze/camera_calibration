"""
Utility functions for downloading and extracting files.
"""

import requests
import zipfile
import os
from pathlib import Path


def download_file(url, filename=None, show_progress=True):
    """
    Download a file from a URL with optional progress indication.

    Args:
        url (str): URL to download from
        filename (str, optional): Local filename to save as. If None, extracts from URL.
        show_progress (bool): Whether to show download progress bar

    Returns:
        str: Path to downloaded file

    Raises:
        requests.exceptions.RequestException: If download fails
    """
    if filename is None:
        filename = url.split('/')[-1]

    print(f"Downloading {filename} from {url}...")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        with open(filename, 'wb') as f:
            if total_size == 0 or not show_progress:
                f.write(response.content)
                print(f"Downloaded {filename}")
            else:
                downloaded = 0
                chunk_size = 8192

                for chunk in response.iter_content(chunk_size=chunk_size):
                    downloaded += len(chunk)
                    f.write(chunk)

                    if show_progress:
                        done = int(50 * downloaded / total_size)
                        percent = int(100 * downloaded / total_size)
                        bar = '=' * done + ' ' * (50 - done)
                        print(f"\r[{bar}] {percent}% ({downloaded}/{total_size} bytes)", end='')

                if show_progress:
                    print()  # New line after progress bar
                print(f"Download complete: {filename}")

        return filename

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        raise


def unzip_file(zip_path, extract_to='.'):
    """
    Extract a zip file to a specified location.

    Args:
        zip_path (str): Path to the zip file
        extract_to (str): Directory to extract files to (default: current directory)

    Returns:
        str: Path to extraction directory

    Raises:
        zipfile.BadZipFile: If the file is not a valid zip file
        FileNotFoundError: If zip file doesn't exist
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    print(f"Extracting {zip_path}...")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

        print(f"Extraction complete to: {extract_to}")
        return extract_to

    except zipfile.BadZipFile as e:
        print(f"Error: Invalid zip file: {e}")
        raise


def extract_from_location(zip_path, extract_to='.', cleanup=False):
    """
    Extract a zip file from a known location.

    Args:
        zip_path (str): Path to the zip file
        extract_to (str): Directory to extract files to (default: current directory)
        cleanup (bool): Whether to delete the zip file after extraction (default: False)

    Returns:
        str: Path to extraction directory

    Raises:
        Exception: If extraction fails
    """
    try:
        # Extract the file
        extract_dir = unzip_file(zip_path, extract_to)

        # Optionally cleanup
        if cleanup:
            os.remove(zip_path)
            print(f"Cleaned up: {zip_path}")

        return extract_dir

    except Exception as e:
        print(f"Error in extract_from_location: {e}")
        raise


def download_and_extract(url, filename=None, extract_to='.', cleanup=False, show_progress=True):
    """
    Download and extract a zip file in one step.

    Args:
        url (str): URL to download from
        filename (str, optional): Local filename to save as. If None, extracts from URL.
        extract_to (str): Directory to extract files to (default: current directory)
        cleanup (bool): Whether to delete the zip file after extraction (default: False)
        show_progress (bool): Whether to show download progress bar (default: True)

    Returns:
        tuple: (downloaded_file_path, extraction_directory)

    Raises:
        Exception: If download or extraction fails
    """
    try:
        # Download the file
        downloaded_file = download_file(url, filename, show_progress)

        # Extract the file
        extract_dir = unzip_file(downloaded_file, extract_to)

        # Optionally cleanup
        if cleanup:
            os.remove(downloaded_file)
            print(f"Cleaned up: {downloaded_file}")

        return downloaded_file, extract_dir

    except Exception as e:
        print(f"Error in download_and_extract: {e}")
        raise


if __name__ == "__main__":
    # Example usage for downloading
    # url = "https://stereo-vision.s3.eu-west-3.amazonaws.com/stereo_vision_data.zip"
    # download_and_extract(url)

    # Example usage for extracting from a known location
    extract_from_location("stereo_vision_data.zip")
