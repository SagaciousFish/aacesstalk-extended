import asyncio

from chatlib.global_config import GlobalConfig
from py_core.utils.aac_corpus_downloader import AACCorpusDownloader

GlobalConfig.is_cli_mode = True

AACCorpusDownloader.assert_authorize()

AACCorpusDownloader.download_corpus_cli()