import subprocess
import os

def get_depot_manifest(app_id: str, depot_id: str, username: str, password: str, depot_executable: str, output_dir: str) -> str | None:
    if not os.path.exists(depot_executable):
        raise FileNotFoundError(f"DepotDownloader executable not found at: {depot_executable}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    cmd = [
        depot_executable,
        "-app", app_id,
        "-depot", depot_id,
        "-username", username,
        "-password", password,
        "-dir", output_dir,
        "-manifest-only"
    ]
    
    print(f"Getting the game manifest...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        print(f"Error: DepotDownloader failed with exit code {e.returncode}")
        return None

def download_pc_source(app_id: str, depot_id: str, username: str, password: str, filelist: str, depot_executable: str, output_dir: str):
    if not os.path.exists(depot_executable):
        raise FileNotFoundError(f"DepotDownloader executable not found at: {depot_executable}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    cmd = [
        depot_executable,
        "-app", app_id,
        "-depot", depot_id,
        "-username", username,
        "-password", password,
        "-filelist", filelist,
        "-dir", output_dir
    ]
    
    print(f"Starting download the game metadata...")
    try:
        subprocess.run(cmd, check=True)
        print(f"Files successfully saved to: {os.path.abspath(output_dir)}")
    except subprocess.CalledProcessError as e:
        print(f"Error: DepotDownloader failed with exit code {e.returncode}")
