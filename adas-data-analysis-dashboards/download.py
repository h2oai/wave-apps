import os
import requests
from tqdm import tqdm

# Replace these URLs with the actual URLs from your GitHub Release

DATA_URLS = {
    'iraste_nxt_cas.csv': 'https://drive.google.com/uc?export=download&id=1h6AdKj3U6MiNXFILvKig8j32E3_SGdfG',
    'iraste_nxt_casdms.csv': 'https://drive.google.com/uc?export=download&id=1Vxl7Zv40NOBMWrsrHP9l8SxzdbNjvktm'
}
DATA_DIR = 'data'

def download_file(url, filename):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    filepath = os.path.join(DATA_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"{filename} already exists. Skipping download.")
        return
    
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(filepath, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

def main():
    for filename, url in DATA_URLS.items():
        print(f"Downloading {filename}...")
        download_file(url, filename)
    print("All files downloaded successfully.")

if __name__ == "__main__":
    main()