
from fastapi import HTTPException
from utils.number_to_khmer import number_to_khmer
from speech_request import SpeechRequest,SpeechCurrency,SpeechLanguage


def to_khmer_digits(amount: str) -> str:
    KHMER_DIGITS = str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩")
    return amount.translate(KHMER_DIGITS)

def split_usd_amount(amount: str) -> tuple[str, str]:
    if "." in amount:
        dollars, cents = amount.split(".", 1)
        cents = cents.ljust(2, "0")[:2]
    else:
        dollars, cents = amount, "00"
    return dollars, cents

def validate_trx_request(request : SpeechRequest):
    errors = []
    try:
        amount_value = float(request.amount)
    except ValueError:
        errors.append(f"amount '{request.amount}' is not a valid number.")
        raise HTTPException(status_code=422, detail=errors)  # stop early, further checks need float

    # 5. Amount must be positive
    if amount_value <= 0:
        errors.append("amount must be greater than 0.")

    # 6. KHR must not have decimals
    if request.currency == SpeechCurrency.KHR and "." in request.amount:
        errors.append("amount must not contain decimals when currency is KHR.")

    # 7. USD decimal places must not exceed 2
    if request.currency == SpeechCurrency.USD and "." in request.amount:
        _, decimals = request.amount.split(".", 1)
        if len(decimals) > 2:
            errors.append(f"amount for USD must have at most 2 decimal places, got {len(decimals)}.")

    if amount_value > 999_999_999:
        errors.append("amount exceeds maximum allowed value (999,999,999).")

    if errors:
        raise HTTPException(status_code=422, detail=errors)


def build_tts_text(request : SpeechRequest) -> str:

    if request.currency == SpeechCurrency.USD:
        dollars, cents = split_usd_amount(request.amount)
        has_cents = cents != "00"

        if request.language == SpeechLanguage.KM:
            kh_dollars = number_to_khmer(dollars)
            kh_cents = number_to_khmer(cents)
            if has_cents:
                return f"ទទួលបាន{kh_dollars}ដុល្លា{kh_cents}សេន"
            else:
                return f"ទទួលបាន{kh_dollars}ដុល្លា"
        else:
            formatted_dollars = f"{int(dollars):,}"
            if has_cents:
                return f"Received {formatted_dollars} dollar and {cents} cent"
            else:
                return f"Received {formatted_dollars} dollar"

    else:

        if request.language == SpeechLanguage.KM:
            kh_amount = number_to_khmer(request.amount)
            return f"ទទួលបាន{kh_amount}{request.currency.get_label(language=request.language)}"
        else:
            formatted_amount = f"{int(request.amount):,}"
            return f"Received {formatted_amount} {request.currency.get_label(language=request.language)}"
