"""
Configuration constants, economic benchmarks, and category taxonomies.
Calibrated directly against Project 1 (Pakistan Digital Advertising Budget Optimizer).
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Commercial Unit Economics (from Project 1)
COGS_PCT = 0.45                   # 45% production & fabric cost of delivered goods
COURIER_FEE = 220.0               # Standard forward courier tariff (PKR)
COD_RETURN_RATE = 0.12            # 12% Cash-on-Delivery doorstep refusal rate
RETURN_LOGISTICS_FEE = 180.0      # Reverse logistics RTO surcharge (PKR)
DEFAULT_TOTAL_BUDGET = 1000000.0  # PKR 1,000,000 optimization baseline

# Five Campaigns from Project 1
CAMPAIGNS = [
    "Lawn_Summer_Pret_2026",
    "Eid_Festive_Collection",
    "Retargeting_Abandoned_Cart",
    "ToteBag_Uni_Special",
    "Flash_Clearance_Sale",
]

# Marketing Channels & Historical Project 1 Benchmarks
PLATFORMS = ["Google", "Instagram", "Facebook", "TikTok", "YouTube"]

PLATFORM_BENCHMARKS = {
    "Google": {"roas": 5.02, "cpa": 599.70, "cpc": 32.50, "cvr": 5.43, "share_pct": 40.0, "role": "High-Intent Search Engine"},
    "Instagram": {"roas": 4.61, "cpa": 388.46, "cpc": 20.74, "cvr": 5.34, "share_pct": 35.0, "role": "Lowest CPA Direct Response"},
    "Facebook": {"roas": 3.68, "cpa": 637.25, "cpc": 24.28, "cvr": 3.81, "share_pct": 13.0, "role": "Cart Recovery Retargeting"},
    "TikTok": {"roas": 2.36, "cpa": 470.59, "cpc": 9.41, "cvr": 2.00, "share_pct": 8.0, "role": "Cheap Youth Top-of-Funnel"},
    "YouTube": {"roas": 2.01, "cpa": 1428.57, "cpc": 34.45, "cvr": 2.41, "share_pct": 4.0, "role": "Brand Recall & Unboxing"},
}

# Regional Logistics Corridors
CITY_TIERS = {
    "Tier-1 Fulfillment Hubs": ["Karachi", "Lahore", "Islamabad", "Rawalpindi"],  # 87.8% spend concentration
    "Tier-2 Industrial Hubs": ["Faisalabad", "Multan", "Sialkot"],                 # 9.3% spend
    "Tier-3 Emerging Corridors": ["Peshawar", "Gujranwala", "Quetta"],             # 2.9% spend
}

# Content Formats for Attention Comparison (Question 1)
CONTENT_TYPES = [
    "Reel",
    "Product Photo",
    "Influencer Post",
    "Styling Video",
    "Sale Announcement",
    "Eid Collection Showcase",
]

# The 7 Core Intent Categories (Question 2 & Question 4)
INTENT_CATEGORIES = [
    "Price & Affordability",
    "Fabric Quality & Material",
    "Sizing & Fit",
    "Delivery & Logistics",
    "Discounts & Promo Codes",
    "Availability & Stock",
    "High Purchase Intent",
]

# Brand Names (Pakistani Retail & Pret Landscape)
BRANDS = ["Khaadi", "Sapphire", "Gul Ahmed", "Outfitters", "Breakout", "Engine", "Limelight"]
