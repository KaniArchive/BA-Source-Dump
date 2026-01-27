import re
import cloudscraper
import urllib.parse

APKPURE_URL = "https://apkpure.com/blue-archive/{pkg}/download"
APKPURE_VER_PATTERN = r'property="og:title" content="Download [^"]+ ([\d\.]+)'
APKPURE_PKG_PATTERN = r'<link rel="canonical" href="https://apkpure\.com/[^/]+/([^/]+)/download"'

APKCOMBO_URL = "https://apkcombo.com/{app_name}/{pkg}/download/apk"
APKCOMBO_VER_PATTERN = r'Version:\s*([\d\.]+)'
APKCOMBO_CDN_PATTERN = r'https%3A%2F%2Fapks\.[^.]+\.r2\.cloudflarestorage\.com%2F[^&"]+'
    
def get_apk_url(pkg: str):
    (apk_pure_version, apk_pure_cdn_url) = get_apkpure_url(pkg)
    (apk_combo_version, apk_combo_cdn_url) = get_apkcombo_url(pkg)
    
    pure_build = parse_ver(apk_pure_version)
    combo_build = parse_ver(apk_combo_version)
    
    print(f"DEBUG: Pure Build: {pure_build} | Combo Build: {combo_build}")

    if pure_build == 0 and combo_build == 0:
        raise ValueError("Critical Error: Could not detect version builds from either source.")

    if pure_build > combo_build and apk_pure_cdn_url:
        return apk_pure_cdn_url
    
    if apk_combo_cdn_url:
        return apk_combo_cdn_url
        
    if apk_pure_cdn_url:
        return apk_pure_cdn_url
        
    raise ValueError(f"Could not retrieve a valid CDN URL for package: {pkg}")

def get_apkpure_url(pkg: str) -> (str, str):
    url = APKPURE_URL.format(pkg=pkg)
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url, timeout=10)
        response.raise_for_status()
        file_content = response.text
        
        version_match = re.search(APKPURE_VER_PATTERN, file_content)
        package_match = re.search(APKPURE_PKG_PATTERN, file_content)
        
        version: str | None = version_match.group(1) if version_match else None
        package = package_match.group(1) if package_match else None
        
        cdn_url = f"https://d.apkpure.com/b/XAPK/{package}?version=latest" if package else None
        
        # print(f"APKPure Version: {version}")
        # print(f"APKPure CDN URL: {cdn_url}")
        
        return version, cdn_url
    except Exception as e:
        return None, None

def get_apkcombo_url(pkg: str) -> (str, str):
    app_name = "blue-archive-jp" if pkg == "com.YostarJP.BlueArchive" else "blue-archive"
    url = APKCOMBO_URL.format(app_name=app_name, pkg=pkg)
    
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url, timeout=10)
        response.raise_for_status()
        file_content = response.text
        
        version_match = re.search(APKCOMBO_VER_PATTERN, file_content)
        cdn_match = re.search(APKCOMBO_CDN_PATTERN, file_content)
        
        version: str | None = version_match.group(1) if version_match else None
        raw_cdn = cdn_match.group(0) if cdn_match else None
        cdn_url = urllib.parse.unquote(raw_cdn) if raw_cdn else None
        
        # print(f"APKCombo Version: {version}")
        # print(f"APKCombo CDN URL: {cdn_url}")
        
        return version, cdn_url
    except Exception as e:
        return None, None
    
def parse_ver(v):
    try:
        return int(v.split(".")[-1]) if v else 0
    except:
        return 0