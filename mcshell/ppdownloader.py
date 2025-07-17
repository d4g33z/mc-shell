# In mcshell/ppdownloader.py
import requests
import os
from pathlib import Path

from mcshell.constants import *

import requests
import os
from pathlib import Path

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