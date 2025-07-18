# In mcshell/ppdownloader.py
import requests
import os
from pathlib import Path

from mcshell.constants import *


class PaperDownloader:
    """Handles downloading Paper server JARs from the official PaperMC v3 API."""
    # The new API base URL is for the 'paper' project specifically
    API_URL = "https://fill.papermc.io/v3/projects/paper"

    def __init__(self, download_dir: Path):
        self.download_dir = download_dir
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def get_jar_path(self, mc_version: str) -> Optional[Path ]:
        """
        Returns the local path to a Paper JAR for the given Minecraft version.
        It will download the JAR if it doesn't already exist locally.
        """
        build = self._get_latest_build_for_version(mc_version)
        if not build:
            return None

        # The download name is constructed from the API response.
        jar_name = build['downloads']['server:default']['name']
        jar_path = self.download_dir / jar_name
        jar_url = urlpath.URL(build['downloads']['server:default']['url'])

        if jar_path.exists():
            print(f"Paper JAR for version {mc_version} already exists at: {jar_path}")
            return jar_path

        return self._download_jar(jar_url, jar_path)

    def _get_latest_build_for_version(self, mc_version: str) -> Optional[dict]:
        """
        Finds the latest build object for a given Minecraft version.
        Corresponds to the GET /v3/projects/paper/versions/{version}/builds endpoint.
        """
        builds_url = f"{self.API_URL}/versions/{mc_version}/builds/latest"
        print(f"Fetching build info from: {builds_url}")
        try:
            response = requests.get(builds_url)
            response.raise_for_status()
            data = response.json()

            # if not isinstance(data, list) or not data:
            #     print(f"Error: No builds found for Minecraft version '{mc_version}'. It may be an invalid version.")
            #     return None

            return data
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Error: Minecraft version '{mc_version}' not found in Paper API.")
            else:
                print(f"Error: HTTP error while fetching build info: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while fetching build info: {e}")
            return None

    def _download_jar(self, download_url:urlpath.URL, jar_path:pathlib.Path) -> Optional[Path]:
        """
        Downloads the specified JAR file.
        Corresponds to the GET /v3/projects/paper/versions/{version}/builds/{build}/download endpoint.
        """
        # download_url = f"{self.API_URL}/versions/{mc_version}/builds/{build_number}/download"
        # jar_path = self.download_dir / jar_name

        # print(f"Downloading Paper {mc_version} (build {build_number})...")
        print(f"Downloading from: {download_url}")

        try:
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(jar_path, 'wb') as f:
                    # Download in chunks for efficiency with large files
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"Download complete. Saved to: {jar_path}")
            return jar_path
        except Exception as e:
            print(f"Error: Failed to download JAR file. Details: {e}")
            # Clean up partial downloads on failure
            if jar_path.exists():
                os.remove(jar_path)
            return None

    def install_plugins(self, plugin_urls: list[str], world_plugins_dir: Path) -> list[str]:
        """
        Downloads and installs a list of plugins from their URLs into the
        specified plugins directory. Handles both .jar and .zip files.

        Args:
            plugin_urls: A list of direct download URLs for the plugins.
            world_plugins_dir: The Path object for the world's 'plugins' folder.

        Returns:
            A list of the filenames of successfully installed plugins.
        """
        if not plugin_urls:
            return []

        world_plugins_dir.mkdir(exist_ok=True)
        successful_installs = []

        print("\n--- Installing Plugins ---")
        for url in plugin_urls:
            filename = url.split('/')[-1]
            destination_path = world_plugins_dir / filename

            print(f"Processing plugin: {filename}")

            try:
                if filename.endswith(".jar"):
                    if self._download_file(url, destination_path):
                        successful_installs.append(filename)
                elif filename.endswith(".zip"):
                    extracted_jar_name = self._download_and_extract_zip(url, world_plugins_dir)
                    if extracted_jar_name:
                        successful_installs.append(extracted_jar_name)
                else:
                    print(f"Warning: Skipping file with unknown extension: {filename}")
            except Exception as e:
                print(f"Error processing plugin from {url}: {e}")

        print("--- Plugin Installation Finished ---")
        return successful_installs

    def _download_file(self, url: str, destination: Path) -> bool:
        """Helper to download a single file to a destination."""
        print(f"  Downloading to {destination}...")
        try:
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(destination, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print("  Download successful.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"  Error: Failed to download file. {e}")
            return False

    def _download_and_extract_zip(self, url: str, destination_dir: Path) -> Optional[str]:
        """Downloads a ZIP file in memory, finds the correct JAR, and extracts it."""
        print("  Detected .zip file. Attempting to find and extract plugin JAR...")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Use io.BytesIO to treat the downloaded bytes as an in-memory file
            with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
                for member_name in thezip.namelist():
                    # Heuristic to find the correct JAR file
                    if member_name.endswith('.jar') and ('paper' in member_name.lower() or 'bukkit' in member_name.lower()):
                        print(f"  Found potential plugin JAR in archive: {member_name}")
                        # Extract the single JAR file to the plugins directory
                        thezip.extract(member_name, path=destination_dir)
                        # We need to rename the file if it was in a subfolder
                        extracted_path = destination_dir / member_name
                        final_path = destination_dir / Path(member_name).name
                        if extracted_path != final_path:
                           os.rename(extracted_path, final_path)
                           # Clean up empty directories if any
                           if os.path.dirname(extracted_path) != destination_dir:
                               os.removedirs(os.path.dirname(extracted_path))

                        print(f"  Successfully extracted and installed: {final_path.name}")
                        return final_path.name

            print("  Error: Could not find a suitable .jar file in the ZIP archive.")
            return None
        except Exception as e:
            print(f"  Error: Failed to download or extract ZIP file. {e}")
            return None
