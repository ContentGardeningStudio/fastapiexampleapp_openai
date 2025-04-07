import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi_limiter.depends import RateLimiter
from typing import Annotated
from openai import OpenAI

from app.schemas.user import User
from app.api.endpoints.user import functions as user_functions

from app.schemas.openai import (GrammarCorrectionText, ImageGenerated,
                                ImageGenerationText, TranslationText)

load_dotenv()

api_key = os.environ["OPENAI_API_KEY"]
# Initialize OpenAI client with your API key
client = OpenAI()


openai_module = APIRouter()


def translate_text(input_str):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert translator who translates text from english to french and only return translated text",
            },
            {"role": "user", "content": input_str},
        ],
    )

    return completion.choices[0].message.content


def grammar_corrector(input_str, language):
    prompt = {
        "en": "You are a grammar checker who correct wrong english text and only return grammarly correct text",
        "fr": "Tu es un correcteur grammaticale en français qui corrige du texte grammaticalement erroné et qui retourne le texte corrigé",
    }

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": prompt[language],
            },
            {"role": "user", "content": input_str},
        ],
    )

    return completion.choices[0].message.content


def image_generator(input_str):
    response = client.images.generate(
        prompt=input_str,
        size="1024x1024",
        n=1,
    )

    return response.data[0].url


# This line decorates 'translate' as a POST endpoint
@openai_module.post(
    "/translate/", # response_model=TranslationText, dependencies=[Depends(RateLimiter(times=1, seconds=30))]
)
async def translate(text_to_translate: TranslationText,
                    # current_user: Annotated[User, Depends(user_functions.get_current_user)]
                    ):
    # print(current_user)

    # if current_user is None:
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Call your translation function
        translated_text = translate_text(text_to_translate.text)
        result = TranslationText(text=translated_text)
        # translate_text = text_to_translate.text
        # result = TranslationText(text=translated_text)
        return {"result": result}
    except Exception as e:
        # Handle exceptions or errors during translation
        raise HTTPException(status_code=500, detail=str(e))


# This line decorates 'grammar_corrector' as a POST endpoint
@openai_module.post(
    "/correct_grammar/", response_model=GrammarCorrectionText
    # dependencies=[Depends(RateLimiter(times=1, seconds=30))]
)
async def correct_grammar(text_to_correct: GrammarCorrectionText):
    try:
        # Call your grammar text corrector function
        corrected_text = grammar_corrector(text_to_correct.text, text_to_correct.language)
        result = GrammarCorrectionText(text=corrected_text)
        return result
    except Exception as e:
        # Handle exceptions or errors during correction
        raise HTTPException(status_code=500, detail=str(e))


# This line decorates 'image_generator' as a POST endpoint
@openai_module.post(
    "/generate_image/", response_model=ImageGenerated
    # dependencies=[Depends(RateLimiter(times=1, seconds=30))]
)
async def generate_image(text_creating_image: ImageGenerationText):
    try:
        # Call your image generator function
        url_image = image_generator(text_creating_image.text)

        # print(image)
        result = ImageGenerated(url=url_image)
        return result
    except Exception as e:
        # Handle exceptions or errors during image generation
        raise HTTPException(status_code=500, detail=str(e))
