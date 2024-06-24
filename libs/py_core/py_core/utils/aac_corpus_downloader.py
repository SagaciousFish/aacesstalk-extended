from typing import Any
from chatlib.utils.integration import IntegrationService, APIAuthorizationVariableSpec
import gdown
from os import path
import shutil
import questionary
from zipfile import ZipFile

from py_core.config import AACessTalkConfig

class AACCorpusDownloader(IntegrationService):

    __gdrive_file_id_spec = APIAuthorizationVariableSpec(variable_type='gdrive_file_id', human_readable_type_name="Google Drive file ID")

    @classmethod
    def provider_name(cls) -> str:
        return "AAC card image corpus"

    @classmethod
    def get_auth_variable_specs(cls) -> list[APIAuthorizationVariableSpec]:
        return [cls.__gdrive_file_id_spec]

    @classmethod
    def _authorize_impl(cls, variables: dict[APIAuthorizationVariableSpec, Any]) -> bool:
        return True
    
    @classmethod
    def download_corpus_cli(cls):
        cls.assert_authorize()

        if path.exists(AACessTalkConfig.card_image_directory_path):
            confirm = questionary.confirm("Card corpus already exists in the local system. Do you want to remove it and download the corpus again?").ask()
            if confirm:
                shutil.rmtree(AACessTalkConfig.card_image_directory_path)
            else:
                return

        download_zip_path = path.join(AACessTalkConfig.dataset_dir_path, "temp_cards.zip")
        #print(download_zip_path)
        file_id = cls.get_auth_variable_for_spec(cls.__gdrive_file_id_spec)
        gdown.download(id=file_id, output=download_zip_path)
        print("Unzipping downloaded corpus...")
        with ZipFile(download_zip_path, 'r') as z:
            infolist = z.infolist()
            for member in infolist:
                member.filename = member.filename.encode("cp437").decode('utf8', 'ignore')
            
                z.extract(member, AACessTalkConfig.card_image_directory_path)

        macos_artifact_path = path.join(AACessTalkConfig.card_image_directory_path, "__MACOSX")
        if path.exists(macos_artifact_path):
            shutil.rmtree(macos_artifact_path)

        print("Corpus was successfully installed.")