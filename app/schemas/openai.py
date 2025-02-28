from pydantic import BaseModel, HttpUrl


# Create class with pydantic BaseModel
class TranslationText(BaseModel):
    text: str


class GrammarCorrectionText(BaseModel):
    text: str
    language: str


class ImageGenerationText(BaseModel):
    text: str


class ImageGenerated(BaseModel):
    url: HttpUrl