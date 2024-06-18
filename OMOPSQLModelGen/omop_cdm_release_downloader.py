# todo
import requests
import os
import zipfile
import requests
from typing import Any
from pathlib import Path
from OMOPSQLModelGen.config import Config

config = Config()


class OMOPCDMReleaseDownloader:
    def __init__(self):
        self.downloader = ZipDownloader(
            url=config.OMOP_CDM_RELEASE_SOURCE_FILE_URL,
            target_extraction_dir=config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
        )

    def download(self):
        print(
            "Download OMOP Repository ('https://github.com/OHDSI/CommonDataModel') release from ",
            self.downloader.url,
            "to",
            self.downloader.target_extraction_dir,
        )
        self.downloader.download_and_extract(keep_source_zip=True)


class ZipDownloader:
    def __init__(
        self,
        url: str,
        target_extraction_dir: str,
        download_target_path: Path = Path("/tmp/omop_downloaded.zip"),
    ) -> None:
        self.url: str = url
        self.target_extraction_dir: Path = Path(target_extraction_dir)
        self.target_extraction_dir.mkdir(parents=True, exist_ok=True)
        self.download_target_path: Path = download_target_path

    def download_zip(self) -> None:
        response: requests.Response = requests.get(self.url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(self.download_target_path, "wb") as file:
            file.write(response.content)

    def extract_zip(self) -> None:
        with zipfile.ZipFile(self.download_target_path, "r") as zip_ref:
            zip_ref.extractall(self.target_extraction_dir)

    def clean_up(self) -> None:
        if self.download_target_path.exists():
            self.download_target_path.unlink()

    def download_and_extract(self, keep_source_zip: bool = False) -> None:
        self.download_zip()
        self.extract_zip()
        if not keep_source_zip:
            self.clean_up()
