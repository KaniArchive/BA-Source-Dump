import os
import argparse

from lib.ApkDownloader import (
    FileDownloader,
    FileExtractor
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download & extract Blue Archive Android Data"
    )
    parser.add_argument(
        "--client",
        choices=["global", "jp"],
        required=True,
        default="jp",
        help="Which game client to download (default: jp)",
    )
    args = parser.parse_args()
    
    client = args.client

    download_dir = os.path.join(os.getcwd(), f'apk_downloads')
    extract_dir = os.path.join(os.getcwd(), f'{client}_extracted')

    if client == "global":
        pkg = "com.nexon.bluearchive"
    else:
        pkg = "com.YostarJP.BlueArchive"

    # Download and Extract the Game XAPK
    print(f"Downloading {client} Data...")
    xapk_url = f"https://d.apkpure.com/b/XAPK/{pkg}?version=latest"
    downloader = FileDownloader(xapk_url, download_dir, f"{pkg}.xapk")
    downloader.download()
    FileExtractor(downloader.local_filepath, extract_dir, client).extract_xapk()
        
    print("Successfully downloaded and extracted files")