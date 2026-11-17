"""
Roman Urdu & English Multilingual Preprocessor
==============================================
Normalizes Pakistani consumer dialect, slang variations, phonetic spellings,
and extracts clean semantic representations for clustering & intent classification.
"""
import re
import string

# Phonetic normalization mapping for common Roman Urdu variations
PHONETIC_SLANG_MAP = {
    # Price
    "pesy": "price", "paise": "price", "qeemat": "price", "qimat": "price",
    "daam": "price", "dam": "price", "rates": "price", "rate": "price",
    "ret": "price", "prce": "price", "pkr": "price", "rupay": "price",
    
    # Adverb / Intensity
    "boht": "bohat", "bht": "bohat", "bohot": "bohat", "bhot": "bohat",
    "zyada": "bohat", "zeyada": "bohat", "ziada": "bohat", "barii": "bohat",
    
    # Courtesies & Ordering
    "plz": "please", "pls": "please", "plez": "please", "plzz": "please",
    "kindly": "please", "mehrbani": "please", "plsss": "please",
    "bhaijo": "bhejo", "bhejna": "bhejo", "bhj": "bhejo",
    "chahye": "chahiye", "chahie": "chahiye", "chaheay": "chahiye",
    "inbx": "inbox", "dm": "inbox", "msg": "message",
    
    # Delivery & Logistics
    "delivry": "delivery", "dilivery": "delivery", "dlvry": "delivery",
    "delvery": "delivery", "phonchana": "delivery", "pohanchna": "delivery",
    "deliver": "delivery", "chargis": "charges", "chrges": "charges",
    
    # Product & Fabric
    "kapra": "fabric", "kapray": "fabric", "kpry": "fabric", "stuff": "fabric",
    "jora": "suit", "suits": "suit", "dresss": "dress", "drss": "dress",
    "lawnn": "lawn", "suti": "cotton", "embroidry": "embroidery",
    
    # Quality & Value
    "achha": "acha", "achi": "acha", "ache": "acha", "accha": "acha",
    "zabrdast": "zabardast", "zbardast": "zabardast", "shandar": "zabardast",
    "pyara": "khubsurat", "piyara": "khubsurat", "khoobsurat": "khubsurat",
    "mehnga": "expensive", "mehnge": "expensive", "mehngi": "expensive",
    "sasta": "cheap", "sasti": "cheap", "saste": "cheap",
    "kharab": "bad", "bekar": "bad", "ghatiya": "bad",
    
    # Availability & Discounts
    "availabl": "available", "avlbl": "available", "milgya": "available",
    "milega": "available", "milyga": "available", "milayga": "available",
    "discnt": "discount", "disocunt": "discount", "choot": "discount",
    "riayat": "discount", "ofer": "offer", "sel": "sale",
    
    # Location
    "khi": "karachi", "lhr": "lahore", "isb": "islamabad", "pindi": "rawalpindi",
    "fsd": "faisalabad", "mul": "multan", "psh": "peshawar",
}

# Roman Urdu and Pakistani E-Commerce Stopwords
PAKISTANI_STOPWORDS = set([
    "hai", "hain", "ka", "ki", "ke", "ko", "se", "par", "pe", "me", "mein", "main",
    "ye", "yeh", "wo", "woh", "hum", "ap", "aap", "mera", "meri", "mere", "tum", "tu",
    "bhai", "baji", "yar", "yaar", "bhi", "to", "toh", "hi", "is", "us", "in", "un",
    "kar", "karo", "karein", "karta", "karti", "karte", "tha", "thi", "the", "hoga",
    "hogi", "hoge", "ho", "ab", "jab", "tab", "jo", "aur", "or", "ya", "na", "ni",
    "nahi", "nhi", "ne", "k", "g", "ji", "jee", "sb", "sab", "walay", "wali", "wala",
    "the", "a", "an", "and", "or", "is", "are", "was", "were", "to", "for", "of",
    "with", "at", "by", "from", "in", "on", "this", "that", "it", "its", "so", "be",
    "i", "you", "my", "we", "they", "them", "do", "does", "did", "have", "has", "had",
    "can", "will", "would", "could", "should", "sir", "madam", "mam"
])

def clean_text(text: str) -> str:
    """
    Standardize text: lowercases, removes emojis, punctuation,
    maps phonetic Roman Urdu variations, and removes extra spaces.
    """
    if not isinstance(text, str) or not text.strip():
        return ""
        
    text = text.lower()
    
    # Remove URLs, handles, and hashtags
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"@\w+|#\w+", "", text)
    
    # Remove punctuation & non-alphanumeric except spaces
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\d+", "", text)
    
    tokens = text.split()
    normalized_tokens = [PHONETIC_SLANG_MAP.get(token, token) for token in tokens]
    
    cleaned = " ".join(normalized_tokens)
    return cleaned.strip()

def remove_stopwords(text: str) -> str:
    """Remove Roman Urdu and English stopwords."""
    if not isinstance(text, str):
        return ""
    tokens = text.split()
    filtered = [t for t in tokens if t not in PAKISTANI_STOPWORDS and len(t) > 1]
    return " ".join(filtered)

def detect_language(text: str) -> str:
    """
    Detect whether comment is predominantly Roman Urdu, English, or Code-Mixed.
    """
    if not isinstance(text, str):
        return "English"
        
    tokens = set(re.findall(r"\b\w+\b", text.lower()))
    if not tokens:
        return "English"
        
    urdu_marker_words = {
        "hai", "hain", "ka", "ki", "ke", "ko", "se", "bohat", "kya", "kia", "kitna",
        "kitne", "bhejo", "karein", "chahiye", "sasta", "mehnga", "bhai", "baji",
        "yar", "achi", "acha", "bura", "kaisa", "kaisi", "kaise", "ap", "aap", "yeh",
        "nahi", "nhi", "karo", "aur", "pe", "mein", "hoga", "hogi", "bhi", "wala", "wali"
    }
    
    urdu_matches = len(tokens.intersection(urdu_marker_words))
    urdu_ratio = urdu_matches / max(len(tokens), 1)
    
    if urdu_ratio >= 0.35:
        return "Roman Urdu"
    elif urdu_ratio > 0.05:
        return "Code-Mixed"
    else:
        return "English"
