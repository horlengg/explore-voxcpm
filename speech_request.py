

from enum import Enum
from pydantic import BaseModel

class SpeechLanguage(Enum):
    KM = "km-kh"
    EN = "en-us"

class SpeechCurrency(Enum):
    KHR = "KHR"
    USD = "USD"

    def get_label(self,language:SpeechLanguage) -> str :
        CURRENCY_DISPLAY = {
            SpeechLanguage.EN: {SpeechCurrency.USD: "dollar", SpeechCurrency.KHR: "riel"},
            SpeechLanguage.KM: {SpeechCurrency.USD: "ដុល្លា", SpeechCurrency.KHR: "រៀល"},
        }
        return CURRENCY_DISPLAY[language][self]


class SpeechVoice(Enum):
    PISETH = "piseth"
    SREYMOM = "sreymom"

    def get_reference_path(self, language: SpeechLanguage) -> str:
        return f"./reference/{language.value}/{self.value}.wav"
    
    def get_reference_prompt(self, language: SpeechLanguage) -> str:
        prompts = {
            SpeechLanguage.KM: "ទទួលបានប្រាំបីមុឺនប្រាំពាន់ពីររយរៀល",
            SpeechLanguage.EN: "Received one million two hundred five thousand riel",
        }
        return prompts.get(
            language, prompts[SpeechLanguage.EN]
        )
    def get_saved_path(self, language: SpeechLanguage,currency:SpeechCurrency,amount : str) -> str :
        return f"outputs/{language.value}/{self.value}/{amount}-{currency.value.lower()}.wav"




class SpeechRequest(BaseModel):
    language: SpeechLanguage
    currency: SpeechCurrency
    voice: SpeechVoice
    amount: str


class SpeechTextRequest(BaseModel):
    language: SpeechLanguage
    voice: SpeechVoice
    content: str