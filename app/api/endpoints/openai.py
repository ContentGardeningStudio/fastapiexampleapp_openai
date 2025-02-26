from fastapi import FastAPI, HTTPException, Depends, APIRouter
from app.schemas.openai import TranslationRequest, GrammarCorrectionRequest, ImageGenerationRequest
import os
from openai import OpenAI
from dotenv import load_dotenv
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

import redis.asyncio as redis
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_connection = redis.from_url("redis://localhost:6379", encoding="utf8")
    await FastAPILimiter.init(redis_connection)
    yield
    await FastAPILimiter.close()

load_dotenv()

api_key = os.environ["OPENAI_API_KEY"]
# Initialize OpenAI client with your API key
client = OpenAI()


openai_module = APIRouter()


def translate_text(input_str):
    completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
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
        "fr": "Tu es un correcteur grammaticale en français qui corrige du texte grammaticalement erroné et qui retourne le texte corrigé"
    }

    completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
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
@openai_module.post("/translate/")
async def translate(request: TranslationRequest):
    try:
        # Call your translation function
        translated_text = translate_text(request.input_str)
        return {"translated_text": translated_text}
    except Exception as e:
        # Handle exceptions or errors during translation
        raise HTTPException(status_code=500, detail=str(e))


# This line decorates 'grammar_corrector' as a POST endpoint
# @app.post("/correct_grammar/", dependencies=[Depends(RateLimiter(times=1, seconds=30))])
# async def correct_grammar(request: GrammarCorrectionRequest):
#     try:
#         # Call your grammar text corrector function
#         corrected_text = grammar_corrector(request.input_str, request.language)
#         return {"corrected_text": corrected_text}
#     except Exception as e:
#         # Handle exceptions or errors during correction
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# # This line decorates 'image_generator' as a POST endpoint
# @app.post("/generate_image/", dependencies=[Depends(RateLimiter(times=1, seconds=30))])
# async def generate_image(request: ImageGenerationRequest):
#     try:
#         # Call your image generator function
#         image = image_generator(request.input_str)
#
#         # print(image)
#         return {"image": image}
#     except Exception as e:
#         # Handle exceptions or errors during image generation
#         raise HTTPException(status_code=500, detail=str(e))

