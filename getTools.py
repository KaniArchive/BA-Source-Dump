import os
import platform

from lib.ApkDownloader import FileDownloader, FileExtractor

if __name__ == "__main__":
    os_system = platform.system()
    lib_dir = os.path.join(os.getcwd(), f'tools')
    
    # Il2CppInspectorRedux
    il2cppInspectorReduxUrl = "https://nightly.link/ArkanDash/Il2CppInspectorRedux/workflows/build/master/Il2CppInspectorRedux.CLI-linux-x64.zip"
    if os_system == "Windows":
        il2cppInspectorReduxUrl = "https://nightly.link/ArkanDash/Il2CppInspectorRedux/workflows/build/master/Il2CppInspectorRedux.CLI-win-x64.zip"
    il2cppDownloader = FileDownloader(il2cppInspectorReduxUrl, lib_dir, "il2cppinspector.zip")
    il2cppDownloader.download()
    FileExtractor(il2cppDownloader.local_filepath, lib_dir).extract_il2cppData()
    print("Successfully downloaded and extracted the Il2CppInspectorRedux")
    
    # FbsDumper
    fbsDumperUrl = "https://github.com/KaniArchive/FbsDumper/releases/download/v2.2.3/FbsDumper-linux-x64.zip"
    if os_system == "Windows":
        fbsDumperUrl = "https://github.com/KaniArchive/FbsDumper/releases/download/v2.2.3/FbsDumper-win-x64.zip"
    fbsDumperDownloader = FileDownloader(fbsDumperUrl, lib_dir, "fbsDumper.zip")
    fbsDumperDownloader.download()
    FileExtractor(fbsDumperDownloader.local_filepath, lib_dir).extract_fbsdumper()
    print("Successfully downloaded and extracted the FbsDumper")
    
    # DepotDownloader
    depotDownloaderUrl = "https://github.com/SteamRE/DepotDownloader/releases/download/DepotDownloader_3.4.0/DepotDownloader-linux-x64.zip"
    if os_system == "Windows":
        depotDownloaderUrl = "https://github.com/SteamRE/DepotDownloader/releases/download/DepotDownloader_3.4.0/DepotDownloader-windows-x64.zip"
    depotDownloaderDownloader = FileDownloader(depotDownloaderUrl, lib_dir, "depotDownloader.zip")
    depotDownloaderDownloader.download()
    FileExtractor(depotDownloaderDownloader.local_filepath, lib_dir).extract_depotdownloader()
    print("Successfully downloaded and extracted the DepotDownloader")