"""
Intent Classification & Sentiment Scoring Engine
================================================
Categorizes customer interactions into 7 core marketing intents and computes
sentiment polarity and purchase intent scores for Pakistani consumer comments.
"""
import re
from typing import Dict, Tuple

# Comprehensive intent keyword dictionaries calibrated to Pakistani social interactions
INTENT_KEYWORDS = {
    "Price & Affordability": [
        "price", "cost", "kitna", "kitne", "kitnay", "pesy", "paise", "qeemat", "qimat",
        "dam", "daam", "rate", "rates", "ret", "expensive", "mehnga", "mehngi", "mehnge",
        "sasta", "sasti", "saste", "budget", "pkr", "rupees", "rupay", "charges", "worth"
    ],
    "Fabric Quality & Material": [
        "fabric", "lawn", "cotton", "silk", "chiffon", "organza", "khaddar", "linen",
        "jacquard", "stuff", "kapra", "kapray", "quality", "soft", "pure", "original",
        "embroidery", "embroidered", "print", "printed", "color", "colour", "shade",
        "dupatta", "dopatta", "trouser", "shirtt", "washed", "guarantee"
    ],
    "Sizing & Fit": [
        "size", "sizes", "small", "medium", "large", "xl", "xs", "xxl", "fit", "fitting",
        "loose", "tight", "length", "chest", "waist", "inches", "measurement", "measurements",
        "chart", "plus size", "stature", "stitching", "stitched", "unstitched"
    ],
    "Delivery & Logistics": [
        "delivery", "deliver", "dilivery", "delivry", "shipping", "ship", "courier",
        "tcs", "leopard", "leopards", "trax", "callcourier", "rider", "cod", "cash on delivery",
        "transit", "days", "din", "kab", "time", "reach", "delay", "late", "waiting",
        "parcel", "tracking", "track", "received", "not received", "karachi", "lahore",
        "islamabad", "rawalpindi", "peshawar", "multan", "quetta", "charges", "free delivery"
    ],
    "Discounts & Promo Codes": [
        "discount", "discounts", "sale", "offer", "promo", "promocode", "code", "coupon",
        "voucher", "off", "percentage", "flat", "11.11", "12.12", "end of season",
        "clearance", "concession", "riayat", "choot", "deal", "bundle"
    ],
    "Availability & Stock": [
        "available", "availabl", "stock", "in stock", "out of stock", "restock", "sold out",
        "khatam", "milgya", "milega", "milayga", "milyga", "dastiyab", "branch", "outlet",
        "store", "mall", "online only", "left", "pieces"
    ],
    "High Purchase Intent": [
        "inbox", "dm", "order", "book", "buy", "purchase", "kharidna", "mangwana", "link",
        "how to order", "details", "send", "bhejo", "bhaijo", "checkout", "address",
        "whatsapp", "number", "confirm", "advance", "add to cart", "want to buy"
    ]
}

# Bilingual Sentiment Lexicons (Roman Urdu + English)
POSITIVE_WORDS = {
    "acha", "achi", "ache", "good", "great", "excellent", "best", "superb", "awesome",
    "love", "loved", "pyara", "piyara", "khubsurat", "khoobsurat", "beautiful", "zabardast",
    "shandar", "nice", "perfect", "satisfied", "happy", "mashallah", "mashaallah",
    "subhanallah", "jazakallah", "recommended", "original", "fast", "cooperative", "trusted"
}

NEGATIVE_WORDS = {
    "bad", "worst", "poor", "kharab", "bekar", "ghatiya", "fake", "fraud", "scam",
    "delayed", "late", "dhoka", "chori", "complaint", "rubbish", "horrible", "bakwas",
    "terrible", "waste", "disappointed", "angry", "mehnga", "expensive", "ruined", "faulty",
    "broken", "damaged", "wrong", "missing", "never", "hate", "unhappy", "regret"
}

def classify_intent(text: str) -> str:
    """
    Classify comment text into one of the 7 core marketing intent categories.
    Defaults to 'High Purchase Intent' if direct booking words are found,
    otherwise matches the highest density category.
    """
    if not isinstance(text, str) or not text.strip():
        return "Price & Affordability"
        
    lower_text = text.lower()
    
    # Priority check: direct checkout / booking intent
    for kw in INTENT_KEYWORDS["High Purchase Intent"]:
        if re.search(r"\b" + re.escape(kw) + r"\b", lower_text):
            return "High Purchase Intent"
            
    # Calculate match scores for all categories
    scores = {}
    for intent, kws in INTENT_KEYWORDS.items():
        score = 0
        for kw in kws:
            if re.search(r"\b" + re.escape(kw) + r"\b", lower_text):
                score += (2 if len(kw) > 4 else 1)
        scores[intent] = score
        
    best_intent = max(scores, key=scores.get)
    if scores[best_intent] > 0:
        return best_intent
        
    # Default fallbacks based on sentence characteristics
    if "?" in text or "kitna" in lower_text or "cost" in lower_text:
        return "Price & Affordability"
    return "Fabric Quality & Material"

def compute_sentiment(text: str) -> Tuple[str, float]:
    """
    Calculate sentiment polarity and continuous score (-1.0 to +1.0).
    Returns (label, score).
    """
    if not isinstance(text, str):
        return ("Neutral", 0.0)
        
    tokens = set(re.findall(r"\b\w+\b", text.lower()))
    pos_matches = len(tokens.intersection(POSITIVE_WORDS))
    neg_matches = len(tokens.intersection(NEGATIVE_WORDS))
    
    score = (pos_matches - neg_matches) / max(pos_matches + neg_matches, 1)
    
    if score >= 0.2:
        return ("Positive", round(float(score), 2))
    elif score <= -0.2:
        return ("Negative", round(float(score), 2))
    else:
        return ("Neutral", round(float(score), 2))

def compute_purchase_intent_score(text: str, intent: str, sentiment: str) -> float:
    """
    Compute a normalized purchase intent score (0.0 to 1.0)
    representing commercial buying temperature.
    """
    base_scores = {
        "High Purchase Intent": 0.85,
        "Availability & Stock": 0.70,
        "Sizing & Fit": 0.65,
        "Delivery & Logistics": 0.60,
        "Price & Affordability": 0.50,
        "Discounts & Promo Codes": 0.45,
        "Fabric Quality & Material": 0.40,
    }
    
    score = base_scores.get(intent, 0.40)
    
    # Sentiment modifier
    if sentiment == "Positive":
        score += 0.12
    elif sentiment == "Negative":
        score -= 0.20
        
    # Direct purchase keywords booster
    lower = text.lower()
    if any(k in lower for k in ["order", "buy", "inbox", "dm", "send", "book", "advance"]):
        score += 0.15
        
    return round(min(max(score, 0.05), 0.98), 2)
