import asyncio
import base64
import csv
import math
from io import BytesIO
from os import listdir, scandir, path

from pydantic import BaseModel
from time import perf_counter

import numpy
from chatlib.global_config import GlobalConfig
from numpy import array

from py_core.config import AACessTalkConfig
from PIL import ImageOps

from py_core.utils.math import cosine_similarity
from py_core.utils.models import CardImageInfo
from chatlib.utils import env_helper
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapper, ChatCompletionFewShotMapperParams, \
    MapperInputOutputPair
from chatlib.tool.converter import generate_pydantic_converter, str_to_str_noop
from chatlib.llm.integration import GPTChatCompletionAPI, GeminiAPI, ChatGPTModel
from openai import OpenAI
import google.generativeai as genai
from PIL import Image

CATEGORY_HUMAN_READABLE_STRING_DICT = {
    "health": "Health",
    "marriage": "Marriage, childbirth, child-rearing",
    "traffic": "Traffic and transportation",
    "nation": "Nations",
    "core": "Core phrases",
    "hobby": "Enjoyment and hobby",
    "university": "University life",
    "animal": "Animals and plants",
    "others": "Others",
    "support": "Welfare, community, and social support",
    "human": "Human",
    "color": "Colors",
    "time": "Time and schedules",
    "sports": "Sports",
    "food": "Food",
    "people": "People, figures, and occupations",
    "disability": "Harms and damages caused by disabilities",
    "religion" :"Religions and spiritual activities",
    "life": "Daily life and social activities",
    "work": "Workplace and jobs",
    "home": "Home, family, relatives",
    "school": "School",
    "service": "Car caring, cell phones, wheelchairs, customer services"
}

def scan_card_images():
    with open(AACessTalkConfig.card_image_table_path, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CardImageInfo.model_fields)
        writer.writeheader()
        for dir_name in listdir(AACessTalkConfig.card_image_directory_path):
            if dir_name.startswith("card_"):
                category_name = str(dir_name[len("card_"):])
                rows = []
                for file in scandir(path.join(AACessTalkConfig.card_image_directory_path, dir_name)):
                    if file.is_file() and file.name.lower().endswith(".png"):
                        with Image.open(file.path) as image:
                            orig_width, orig_height = image.size
                            if orig_width != 512 or orig_height != 512:
                                resized = ImageOps.pad(image, size=(512, 512), method=Image.Resampling.BICUBIC)
                                print(f"resized to {resized.size}")
                                with open(file.path, 'wb') as f:
                                    resized.save(f, format="PNG")
                                    resized.close()

                            row = CardImageInfo(
                                category=category_name,
                                name_ko=file.name[:-len(".png")],
                                filename=path.join(dir_name, file.name),
                                format=image.format,
                                width=512,
                                height=512
                            )
                            rows.append(row)
                    else:
                        print("Exclude", file.path)


                print(f"{len(rows)} cards in {CATEGORY_HUMAN_READABLE_STRING_DICT[category_name]} ({category_name}).")
                writer.writerows([row.model_dump() for row in rows])


def _load_card_descriptions() -> list[CardImageInfo]:
    rows: list[CardImageInfo] = []
    with open(AACessTalkConfig.card_image_table_path, "r") as csvfile:
        reader = csv.DictReader(csvfile)

        for row_obj in reader:
            row = CardImageInfo(**row_obj)
            rows.append(row)
    print(f"loaded {len(rows)} card info list.")
    return rows


def _save_card_descriptions(rows: list[CardImageInfo]):
    with open(AACessTalkConfig.card_image_table_path, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CardImageInfo.model_fields)
        writer.writeheader()
        writer.writerows([row.model_dump() for row in rows])

def inspect_card_info_data():
    rows = _load_card_descriptions()
    for row in rows:
        if row.description is None:
            print(f"{row.id} ({row.name_ko}) has no descriptions.")

class CardNameTranslationInput(BaseModel):
    label: str
    category: str
    description: str

async def translate_card_names():

    str_to_input, input_to_str  = generate_pydantic_converter(CardNameTranslationInput, 'json')

    mapper = ChatCompletionFewShotMapper(
        GPTChatCompletionAPI(),
        instruction_generator="""
You are a helpful assistant that translates Korean card labels into English.
[Input]
{
    "label": // a Korean label of an illustration.
    "category": // A category of the illustration. May be referred to for disambiguation.
    "description": // A description for the illustration. May be referred to for disambiguation.
}
[Output]
Return an English label. When translating, consider the description of the illustration for disambiguation.
        """,
        output_str_converter=str_to_str_noop,
        str_output_converter=str_to_str_noop,
        input_str_converter=input_to_str
    )

    examples = [
        MapperInputOutputPair(
            input= CardNameTranslationInput(
                label="블록쌓기",
                category=CATEGORY_HUMAN_READABLE_STRING_DICT["hobby"],
                description="The image shows a human hand depicted as picking up or placing blocks in different colors."
            ),
            output="Stacking blocks"
            ),
        MapperInputOutputPair(
            input= CardNameTranslationInput(
                label="삼계탕",
                category=CATEGORY_HUMAN_READABLE_STRING_DICT["food"],
                description="The image shows a human hand depicted as picking up or placing blocks in different colors."
            ),
            output="Samgye-Tang (Ginseng Chicken Soup)"
        ),
    ]

    rows = _load_card_descriptions()
    for i, info in enumerate(rows):
        if info.name_en is None and info.description is not None:
            print(f"Translate {info.name_ko} of {info.category} with GPT-4...{i}/{len(rows)}")
            try:
                print(f"Processing {i}/{len(rows)}...")
                label_translated = await mapper.run(examples, CardNameTranslationInput(label=info.name_ko, category=CATEGORY_HUMAN_READABLE_STRING_DICT[info.category], description=info.description),
                                               ChatCompletionFewShotMapperParams(model=ChatGPTModel.GPT_4_0613,
                                                                                 api_params={}))
                # print("[Condensed]", description)
                # print("[Original]", row.description)
                info.name_en = label_translated
                _save_card_descriptions(rows)
            except Exception as e:
                print(e)

def generate_card_descriptions_all(openai_client: OpenAI):
    rows = _load_card_descriptions()

    for i, row in enumerate(rows):
        if row.description is not None and ("sorry") in row.description:
            print(f"{i}/{len(rows)} row contains 'I'm sorry': {row.description}")
        if row.description is None or len(row.description) == 0:
            try:
                print(f"Processing {i}/{len(rows)} complete...")
                description = generate_card_description_gpt4(row, openai_client)
                row.description = description
                row.description_src = "gpt4"

            except Exception as e:
                gemini_description = generate_card_description_gemini(row)
                if gemini_description is not None and len(gemini_description) > 0:
                    row.description = gemini_description
                    row.description_src = "gemini"
            finally:
                _save_card_descriptions(rows)


def _get_image(info: CardImageInfo) -> Image:
    print(info)
    image_path = path.join(AACessTalkConfig.card_image_directory_path, info.filename)

    image = Image.open(image_path).convert("RGBA")
    new_image = Image.new("RGBA", (image.width, image.height), "WHITE")
    new_image.paste(image, (0, 0), mask=image.convert("RGBA"))

    return new_image.convert("RGB")


def generate_card_description_gemini(info: CardImageInfo) -> str | None:
    print(f"Generate description for {info.name_ko} of {info.category} with Gemini Pro Vision...")

    t_start = perf_counter()

    model = genai.GenerativeModel('gemini-pro-vision')

    prompt = f"This is an illustration of a visual aid symbolizing \"{info.name_en or info.name_ko}\" in the \"{CATEGORY_HUMAN_READABLE_STRING_DICT[info.category]}\" category. Please briefly describe the visual contents in this illustration so that we can use your description for visual search."

    response = model.generate_content(
        safety_settings=[
            {
                "category": category,
                "threshold": "BLOCK_NONE"
            } for category in
            ["HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_HARASSMENT",
             "HARM_CATEGORY_DANGEROUS_CONTENT"]
        ],
        contents=[prompt, _get_image(info)]
    )

    t_end = perf_counter()

    print(f"Gemini-Pro captioning took {t_end - t_start} sec.")

    try:
        text = response.text
        return text
    except ValueError:
        print(response.prompt_feedback)
        return None


def generate_card_description_gpt4(info: CardImageInfo, client: OpenAI) -> str:
    print(f"Generate description for {info.name_ko} of {info.category} with GPT-4V...")

    t_start = perf_counter()

    image = _get_image(info)
    buffered = BytesIO()
    image.save(buffered, format="JPEG")

    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf8')

    prompt = f"This is an illustration of a visual aid symbolizing \"{info.name_ko}\" in the \"{CATEGORY_HUMAN_READABLE_STRING_DICT[info.category]}\" category. Please briefly describe the visual contents in this illustration so that we can use your description for visual search."

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )

    t_end = perf_counter()

    print(f"GPT-4v captioning took {t_end - t_start} sec.")

    return response.choices[0].message.content



def fix_refused_requests(threshold: float, client: OpenAI):
    model = AACessTalkConfig.embedding_model

    rows = _load_card_descriptions()
    suspicious_rows = [row for row in rows if row.description is not None and (
            ("sorry" in row.description) or ("cannot" in row.description) or ("assistance" in row.description))]

    print(f"{len(suspicious_rows)} rows are suspicious.")

    embeddings = client.embeddings.create(input=[row.description.replace("\n", " ") for row in suspicious_rows],
                                          model=model)
    embeddings = [datum.embedding for datum in embeddings.data]

    print(f"{len(embeddings)} embeddings generated.")

    rejection_text = "I'm sorry, I cannot provide assistance with that request."

    rejection_embedding = client.embeddings.create(input=[rejection_text], model=model).data[0].embedding

    similarities = [(cosine_similarity(emb, rejection_embedding)) for emb in embeddings]
    print(similarities)
    pairs: list[tuple[CardImageInfo, float]] = [(row, sim) for row, sim in zip(suspicious_rows, similarities)]
    pairs.sort(key=lambda elm: elm[1], reverse=True)

    for pair in pairs:
        print(f"Similarity: {pair[1]} Description: {pair[0].description}")

        if pair[1] > threshold:
            try:
                gemini_desc = generate_card_description_gemini(pair[0])
                print(gemini_desc)
                pair[0].description = gemini_desc
                pair[0].description_src = 'gemini'
                _save_card_descriptions(rows)
            except Exception as e:
                print(e)
                pass


async def generate_short_descriptions_all():
    mapper = ChatCompletionFewShotMapper.make_str_mapper(
        GPTChatCompletionAPI(),
        instruction_generator="""
You are a helpful assistant that extracts a gist of image description that the user provided.
[Input]
The user will provide an image description, which may be clumsy and include unnecessary small talks.
[Output]
Condense the description by focusing only on the description of visual elements in the image.
Drop assistant messages like "I'm sorry" and style descriptions such as "The design is simple and iconic, using minimal colors and flat design principles."
        """
    )

    examples = [
        MapperInputOutputPair(
            input="The illustration shows a stylized stack of currency notes in green, with the number ""10000"" visible on the top note, indicating the value. Above the stack of notes is text in Korean, ""장애인연금,"" which translates to ""Disability Pension."" The overall image represents a financial support or pension provided to individuals with disabilities. The design is simple and iconic, using minimal colors and flat design principles.",
            output="A stylized stack of currency notes in green, with the number ""10000"" visible on the top note, indicating the value. Above the stack of notes is text in Korean, ""장애인연금,"" which translates to ""Disability Pension."" The overall image represents a financial support or pension provided to individuals with disabilities."
        ),
        MapperInputOutputPair(
            input="I'm sorry, but I cannot provide information on the identity of the individual in the image. However, I can describe the visual elements without identifying them. The image shows a person smiling broadly. The individual has short black hair and appears to be wearing a dark purple or blue suit with a tie. The background is blurry, making it difficult to discern details, suggesting the focus is entirely on the person in the foreground. The lighting in the photo highlights the person's face, emphasizing their joyful expression.",
            output="A person smiling broadly, with joyful expression. The individual has short black hair and appears to be wearing a dark purple or blue suit with a tie."
        )
    ]

    rows = _load_card_descriptions()
    for i, row in enumerate(rows):
        if row.description is not None and row.description_brief is None:
            try:
                print(f"Processing {i}/{len(rows)}...")
                description = await mapper.run(examples, row.description,
                                               ChatCompletionFewShotMapperParams(model=ChatGPTModel.GPT_4_0613,
                                                                                 api_params={}))
                # print("[Condensed]", description)
                # print("[Original]", row.description)
                row.description_brief = description
                _save_card_descriptions(rows)
            except Exception as e:
                print(e)

    for i, row in enumerate(rows):
        if row.description is not None and row.description_brief is not None:
            desc_words = row.description.split(" ")
            desc_brief_words = row.description_brief.split(" ")

            print(
                f"{i}/{len(rows)} description word count reduced from {len(desc_words)} to {len(desc_brief_words)} ({len(desc_brief_words) / len(desc_words) * 100}%)")

def cache_description_embeddings_all(client: OpenAI):
    rows = _load_card_descriptions()
    chunk_size = 2048
    name_embeddings = []
    description_brief_embeddings = []
    for chunk_i in range(0, len(rows), chunk_size):
        chunked_rows = rows[chunk_i : chunk_i + chunk_size]
        desc_brief_emb_result = client.embeddings.create(input=[row.description_brief.replace("\n", " ") for row in chunked_rows],
                                            model=AACessTalkConfig.embedding_model,
                                            dimensions=AACessTalkConfig.embedding_dimensions
                                        )
        description_brief_embeddings.extend([datum.embedding for datum in desc_brief_emb_result.data])

        name_emb_result = client.embeddings.create(input=[row.name_en for row in chunked_rows],
                                                         model=AACessTalkConfig.embedding_model,
                                                         dimensions=AACessTalkConfig.embedding_dimensions
                                                         )

        name_embeddings.extend([datum.embedding for datum in name_emb_result.data])

    with open(AACessTalkConfig.card_image_embeddings_path, 'wb') as f:
        numpy.savez_compressed(f, ids=[row.id for row in rows],
                               emb_name=array(name_embeddings),
                               emb_desc=array(description_brief_embeddings))
        print("Serialized embeddings to file.")


if __name__ == "__main__":
    if not path.exists(AACessTalkConfig.card_image_table_path):
        scan_card_images()

    GlobalConfig.is_cli_mode = True

    GPTChatCompletionAPI.assert_authorize()
    GeminiAPI.assert_authorize()

    openai_client = OpenAI(api_key=env_helper.get_env_variable("OPEN_A_I_API_KEY"))
    genai.configure(api_key=env_helper.get_env_variable("GOOGLE_API_KEY"))

    # scan_card_images()
    inspect_card_info_data()
    #generate_card_descriptions_all(openai_client)
    #fix_refused_requests(threshold=0.4, client=openai_client)
    #asyncio.run(generate_short_descriptions_all())
    # asyncio.run(translate_card_names())
    cache_description_embeddings_all(openai_client)
