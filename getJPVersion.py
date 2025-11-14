import os, platform
import json
import requests

from lib.CatalogFetcher import decrypt_game_config, find_game_config
from lib.Il2CppInspectorDumper import Il2CppInspectorDumperCLI
from lib.FBSDumper import FbsDumperCLI

if __name__ == "__main__":
    # Setup paths
    os_system = platform.system()
    lib_dir = os.path.join(os.getcwd(), f'dump_lib')
    extract_dir = os.path.join(os.getcwd(), 'jp_extracted')
    data_dir = os.path.join(os.getcwd(), 'jp_data')

    libil2cpp_path = os.path.join(extract_dir, "config_arm64_v8a", "lib", "arm64-v8a", "libil2cpp.so")
    metadata_path = os.path.join(extract_dir, "BlueArchive_apk", "assets", "bin", "Data", "Managed", "Metadata", "global-metadata.dat")
    dummydll_dir = os.path.join(data_dir, "dll")

    il2cpp_exec_path = os.path.join(lib_dir, "Il2CppInspector", "Il2CppInspector.Redux.CLI")
    fbsdumper_exec_path = os.path.join(lib_dir, "FbsDumper", "FbsDumper")
    if os_system == "Windows":
        il2cpp_exec_path = os.path.join(lib_dir, "Il2CppInspector", "Il2CppInspector.Redux.CLI.exe")
        fbsdumper_exec_path = os.path.join(lib_dir, "FbsDumper", "FbsDumper.exe")

    xapk_manifest_path = os.path.join(extract_dir, "manifest.json")
    os.makedirs(data_dir, exist_ok=True)

    # Dump il2cpp data from the apk file
    print("Dumping il2cpp data...")
    il2cppDumper = Il2CppInspectorDumperCLI(il2cpp_exec_path, libil2cpp_path, metadata_path)
    il2cppDumper.dump(data_dir)
    # il2cppDumper.dump(os.path.join(data_dir, "ida_disassember"), use_dissambler=True, dissambler_option="IDA")
    # il2cppDumper.dump(os.path.join(data_dir, "ghidra_disassember"), use_dissambler=True, dissambler_option="Ghidra")

    # Generate fbs both for V1 and V2
    print("Generating fbs...")
    fbsDumper = FbsDumperCLI(fbsdumper_exec_path, dummydll_dir)
    fbsDumper.dump(data_dir, "BlueArchiveV1.fbs")
    fbsDumper.dump(data_dir, "BlueArchiveV2.fbs", libil2cpp_path)

    # Copy assembly & metadata
    # print("Copying assembly & metadata...")
    # shutil.copy(libil2cpp_path, os.path.join(data_dir, "libil2cpp.so"))
    # shutil.copy(metadata_path, os.path.join(data_dir, "global-metadata.dat"))

    # Old fbs generator
    # dump_cs_path = os.path.join(dumped_dir, "dump.cs")
    # fbs_path = os.path.join(dumped_dir, "BlueArchive.fbs")
    # FBSGenerator(dump_cs_path, fbs_path).generate_fbs()

    # Get the game url
    output_file_path = os.path.join(data_dir, "config.json")
    metadata_file_path = os.path.join(data_dir, 'metadata.json')

    game_config = find_game_config(os.path.join(extract_dir, "UnityDataAssetPack", "assets", "bin", "Data"))
    if game_config is None:
        print("Game config not found")
        exit(1)
    config_url = decrypt_game_config(game_config)
    with open(xapk_manifest_path, encoding='utf-8') as f:
        manifest = json.load(f)

    # Request the data from config and save to the disk
    try:
        response = requests.get(config_url)
        response.raise_for_status()
        config_data_res = response.json()

        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(config_data_res, file, indent=4, ensure_ascii=False)

        print(f"Config data has been written to {output_file_path}")
    except requests.RequestException as e:
        print(f"Error fetching config data: {e}")

    addressVersion = config_data_res["ConnectionGroups"][0]["OverrideConnectionGroups"][-1]["Name"]
    addressUrl = config_data_res["ConnectionGroups"][0]["OverrideConnectionGroups"][-1]["AddressablesCatalogUrlRoot"]
    addressGameVersion = f"{addressVersion}.{addressUrl.split('/')[-1]}"
    game_metadata = {
        "ServerInfoDataUrl": config_url,
        "GameVersion": manifest["version_name"],
        "BuildVersion": manifest["version_code"],
        "AddressableVersion": addressGameVersion,
        "AddressableBuildVersion": addressUrl.split('/')[-1],
        "AddressableUrl": addressUrl
    }

    with open(metadata_file_path, 'w', encoding='utf-8') as file:
        json.dump(game_metadata, file, indent=4, ensure_ascii=False)

    print(f"Data has been moved to {data_dir}")