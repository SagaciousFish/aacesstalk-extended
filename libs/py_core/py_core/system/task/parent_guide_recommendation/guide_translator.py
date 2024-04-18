from py_core.system.model import ParentGuideElement
from py_core.utils.deepl_translator import DeepLTranslator


class GuideTranslator:

    def __init__(self):
        self.__deepl_translator = DeepLTranslator()

    async def translate(self, guides: list[ParentGuideElement] | ParentGuideElement) -> list[ParentGuideElement] | ParentGuideElement:
        guide_texts = [entry.guide for entry in guides] if isinstance(guides, list) else guides.guide

        ##translated_examples, translated_guides = await asyncio.gather(coroutine_translate_examples, coroutine_translate_guides)
        translated_guides = await self.__deepl_translator.translate(
            text=guide_texts,
            source_lang="EN",
            target_lang="KO",
            context="The phrases are guides for parents' communication with children with Autism Spectrum Disorder."
        )

        return [entry.with_guide_localized(guide) for guide, entry in zip(translated_guides, guides)] if isinstance(guides, list) else guides.with_guide_localized(translated_guides)
