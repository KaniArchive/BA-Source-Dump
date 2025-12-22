import os, platform
import json
import argparse
import re

from lib.Il2CppInspectorDumper import Il2CppInspectorDumperCLI
from lib.FBSDumper import FbsDumperCLI
from lib.DepotDataDownloader import download_pc_source, get_depot_manifest 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download & extract Blue Archive PC Data"
    )
    parser.add_argument(
        "--username",
        required=False,
        default=None,
        help="Steam username (default: username)",
    )
    parser.add_argument(
        "--password",
        required=False,
        default=None,
        help="Steam password (default: password)",
    )
    args = parser.parse_args()
    username = args.username
    password = args.password
    
    os_system = platform.system()
    tools_dir = os.path.join(os.getcwd(), f'tools')
    extract_dir = os.path.join(os.getcwd(), 'globalpc_extracted')
    data_dir = os.path.join(os.getcwd(), 'globalpc_data')

    game_assembly_path = os.path.join(extract_dir, "GameAssembly.dll")
    metadata_path = os.path.join(extract_dir, "BlueArchive_Data", "il2cpp_data", "Metadata", "global-metadata.dat")
    dummydll_dir = os.path.join(data_dir, "dll")
    
    il2cpp_exec_path = os.path.join(tools_dir, "Il2CppInspector", "Il2CppInspector.Redux.CLI")
    fbsdumper_exec_path = os.path.join(tools_dir, "FbsDumper", "FbsDumper")
    depotdownloader_exec_path = os.path.join(tools_dir, "DepotDownloader", "DepotDownloader")
    if os_system == "Windows":
        il2cpp_exec_path = os.path.join(tools_dir, "Il2CppInspector", "Il2CppInspector.Redux.CLI.exe")
        fbsdumper_exec_path = os.path.join(tools_dir, "FbsDumper", "FbsDumper.exe")
        depotdownloader_exec_path = os.path.join(tools_dir, "DepotDownloader", "DepotDownloader.exe")

    xapk_manifest_path = os.path.join(extract_dir, "manifest.json")
    os.makedirs(data_dir, exist_ok=True)
    
    APP_ID = "3557620"
    DEPOT_ID = "3557621"
    FILELIST = os.path.join(os.getcwd(), "gamefilelist.txt")
    download_pc_source(APP_ID, DEPOT_ID, username, password, FILELIST, depotdownloader_exec_path, extract_dir)

    # Dump il2cpp data from the apk file
    print("Dumping il2cpp data...")
    il2cppDumper = Il2CppInspectorDumperCLI(il2cpp_exec_path, game_assembly_path, metadata_path)
    il2cppDumper.dump(data_dir)
    # il2cppDumper.dump(os.path.join(data_dir, "ida_disassember"), use_dissambler=True, dissambler_option="IDA")
    # il2cppDumper.dump(os.path.join(data_dir, "ghidra_disassember"), use_dissambler=True, dissambler_option="Ghidra")

    # Generate fbs both for V1 and V2
    print("Generating fbs...")
    fbsDumper = FbsDumperCLI(fbsdumper_exec_path, dummydll_dir)
    fbsDumper.dump(data_dir, "BlueArchiveV1.fbs")
    fbsDumper.dump(data_dir, "BlueArchiveV2.fbs", game_assembly_path)

    # Copy assembly & metadata
    # print("Copying assembly & metadata...")
    # shutil.copy(game_assembly_path, os.path.join(data_dir, "libil2cpp.so"))
    # shutil.copy(metadata_path, os.path.join(data_dir, "global-metadata.dat"))

    # Old fbs generator
    # dump_cs_path = os.path.join(dumped_dir, "dump.cs")
    # fbs_path = os.path.join(dumped_dir, "BlueArchive.fbs")
    # FBSGenerator(dump_cs_path, fbs_path).generate_fbs()

    # Get the game info
    metadata_file_path = os.path.join(data_dir, 'metadata.json')
    manifest_data = get_depot_manifest(APP_ID, DEPOT_ID, username, password, depotdownloader_exec_path, extract_dir)
    if manifest_data is None:
        print("Could not get Manifest data")
        exit(1)
        
    match = re.search(r"Manifest\s+(\d+)", manifest_data)
    if match:
        manifest_id = match.group(1)
        print(f"Latest Manifest ID: {manifest_id}")
    else:
        print("Could not find Manifest ID in output.")
    
    game_metadata = {
        "SteamAppId": APP_ID,
        "SteamDepotId": DEPOT_ID,
        "SteamManifestId": manifest_id if manifest_id is not None else "Unknown",
        "SteamDBManifestUrl": f"https://steamdb.info/depot/{DEPOT_ID}/history/?changeid=M:{manifest_id}",
    }

    with open(metadata_file_path, 'w', encoding='utf-8') as file:
        json.dump(game_metadata, file, indent=4, ensure_ascii=False)

    print(f"Data has been moved to {data_dir}")