from pydantic import BaseModel


# Create class with pydantic BaseModel
class TranslationRequest(BaseModel):
    input_str: str


class GrammarCorrectionRequest(BaseModel):
    input_str: str
    language: str


class ImageGenerationRequest(BaseModel):
    input_str: str