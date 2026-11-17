"""
Project 1 Financial & Budget Integration Bridge
===============================================
Bridges audience segments and comment clusters discovered in Project 3 directly
to the macroeconomic performance, ROAS, CPA, COD economics, and algorithmic
budget reallocation models from Project 1 (Pakistan Digital Advertising Budget Optimizer).
"""
import os
import pandas as pd
import numpy as np
from typing import Dict, Tuple

from engine.config import (
    DATA_RAW_DIR, COGS_PCT, COURIER_FEE, COD_RETURN_RATE,
    RETURN_LOGISTICS_FEE, DEFAULT_TOTAL_BUDGET, PLATFORM_BENCHMARKS
)

# Empirical response curve parameters fitted via SLSQP in Project 1
# Model: Revenue = alpha * ln(1 + beta * Spend)
# Calibrated to exact Project 1 SLSQP empirical benchmarks (4.37x Blended ROAS at Rs. 1M spend)
RESPONSE_CURVE_PARAMS = {
    "Google": {"alpha": 1164741.5, "beta": 1.15e-5, "aov": 3006.0, "cpc": 32.50, "cvr": 0.0543},
    "Instagram": {"alpha": 959234.1, "beta": 1.25e-5, "aov": 2250.0, "cpc": 20.74, "cvr": 0.0534},
    "Facebook": {"alpha": 556142.9, "beta": 1.05e-5, "aov": 2340.0, "cpc": 24.28, "cvr": 0.0381},
    "TikTok": {"alpha": 363667.4, "beta": 0.85e-5, "aov": 1550.0, "cpc": 9.41, "cvr": 0.0200},
    "YouTube": {"alpha": 305817.8, "beta": 0.75e-5, "aov": 2860.0, "cpc": 34.45, "cvr": 0.0241},
}

def load_project1_summaries() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the genuine summary tables generated in Project 1."""
    camp_summary_path = os.path.join(DATA_RAW_DIR, "campaign_summary.csv")
    budget_rec_path = os.path.join(DATA_RAW_DIR, "budget_recommendations.csv")
    city_alloc_path = os.path.join(DATA_RAW_DIR, "budget_city_allocation.csv")
    
    df_camp = pd.read_csv(camp_summary_path) if os.path.exists(camp_summary_path) else pd.DataFrame()
    df_budget = pd.read_csv(budget_rec_path) if os.path.exists(budget_rec_path) else pd.DataFrame()
    df_city = pd.read_csv(city_alloc_path) if os.path.exists(city_alloc_path) else pd.DataFrame()
    
    return df_camp, df_budget, df_city

def map_clusters_to_project1_economics(df_profiles: pd.DataFrame) -> pd.DataFrame:
    """
    Map each discovered audience segment/cluster to Project 1 channel economics,
    explaining the commercial mechanism behind ROAS and acquisition costs.
    """
    segment_mappings = {
        "Price-Sensitive & Budget Shoppers": {
            "mapped_campaign": "Flash_Clearance_Sale",
            "mapped_channel": "TikTok & Facebook",
            "project1_roas": "3.58x (Flash Sale) / 2.36x (TikTok)",
            "project1_cpa": "Rs. 474.40",
            "economic_rationale": "High price elasticity. Drives cheap reach (Rs. 9.41 CPC) and high volume on impulse SKUs under Rs. 2,000, but depresses AOV (Rs. 1,697)."
        },
        "Delivery-Anxious & COD Inquirers": {
            "mapped_campaign": "Regional Logistics Focus (Tier-1 vs Tier-2/3)",
            "mapped_channel": "All Channels (COD Logistics Fulfillment)",
            "project1_roas": "Tier-1: 4.25x vs Tier-3: 2.90x",
            "project1_cpa": "Logistics cost Rs. 400 per bounce",
            "economic_rationale": "Direct root cause of 12% COD return rate and Rs. 220+180 courier friction. Explains why Project 1 concentrates 87.8% spend in Karachi/Lahore."
        },
        "Premium Fabric & Quality Seekers": {
            "mapped_campaign": "Eid_Festive_Collection",
            "mapped_channel": "Google Ads & Instagram",
            "project1_roas": "5.02x (Google) / 4.74x (Eid Collection)",
            "project1_cpa": "Rs. 599.70",
            "economic_rationale": "High commercial intent. Customers seek fabric authenticity and embroidery quality, unlocking the highest basket value (AOV Rs. 3,047) and 19.4% net margin."
        },
        "High-Intent Direct Buyers (DM / Checkout)": {
            "mapped_campaign": "Retargeting_Abandoned_Cart",
            "mapped_channel": "Instagram Ads",
            "project1_roas": "6.15x (Cart Recovery) / 4.61x (IG)",
            "project1_cpa": "Rs. 388.46 (Lowest in Pakistan)",
            "economic_rationale": "Immediate checkout readiness. DM automation and cart retargeting yield the lowest acquisition cost (Rs. 367) and highest conversion rate (5.93%)."
        },
        "Bargain & Flash Sale Hunters": {
            "mapped_campaign": "Flash_Clearance_Sale",
            "mapped_channel": "TikTok & Facebook Ads",
            "project1_roas": "3.58x",
            "project1_cpa": "Rs. 474.40",
            "economic_rationale": "Responsive to limited-time bundle promotions. Converts efficiently when discount threshold exceeds 25%."
        },
        "Stock & Outlet Inquirers": {
            "mapped_campaign": "Lawn_Summer_Pret_2026",
            "mapped_channel": "Instagram & Google Shopping",
            "project1_roas": "3.53x",
            "project1_cpa": "Rs. 638.94",
            "economic_rationale": "Omnichannel demand bridging online ads with physical retail stores in Lahore and Karachi."
        },
        "Sizing & Fit Cautious Shoppers": {
            "mapped_campaign": "ToteBag_Uni_Special",
            "mapped_channel": "TikTok & Instagram Reels",
            "project1_roas": "3.04x",
            "project1_cpa": "Rs. 533.30",
            "economic_rationale": "Youth demographics requiring clear size charts and model video demonstrations to reduce checkout hesitation."
        }
    }
    
    rows = []
    for _, prof in df_profiles.iterrows():
        c_name = prof["cluster_name"]
        mapping = segment_mappings.get(c_name, {
            "mapped_campaign": "Lawn_Summer_Pret_2026",
            "mapped_channel": "Instagram Ads",
            "project1_roas": "3.53x",
            "project1_cpa": "Rs. 550.00",
            "economic_rationale": "General audience segment driving blended platform performance."
        })
        
        rows.append({
            "Cluster ID": prof["cluster_id"],
            "Segment Persona": c_name,
            "Audience Share (%)": prof["audience_share_pct"],
            "Dominant Intent": prof["dominant_intent"],
            "Mapped Project 1 Campaign": mapping["mapped_campaign"],
            "Strategic Ad Channel": mapping["mapped_channel"],
            "Channel ROAS": mapping["project1_roas"],
            "Acquisition Cost (CPA)": mapping["project1_cpa"],
            "Economic & CRO Consequence": mapping["economic_rationale"]
        })
        
    return pd.DataFrame(rows)

def simulate_budget_allocation(
    google_pct: float,
    instagram_pct: float,
    facebook_pct: float,
    tiktok_pct: float,
    youtube_pct: float,
    total_budget: float = 1000000.0,
    delivery_friction_reduction_pct: float = 0.0
) -> Dict:
    """
    Simulates ad budget reallocation across platforms using Project 1's
    diminishing marginal returns logarithmic response curves and true unit economics.
    
    Includes simulated impact of addressing delivery friction:
      Reduces the 12% COD return rate down to (12% * (1 - reduction_pct)),
      saving courier return penalties and unlocking higher net operating profit.
    """
    total_pct = google_pct + instagram_pct + facebook_pct + tiktok_pct + youtube_pct
    if total_pct <= 0:
        total_pct = 100.0
        
    pct_map = {
        "Google": google_pct / total_pct,
        "Instagram": instagram_pct / total_pct,
        "Facebook": facebook_pct / total_pct,
        "TikTok": tiktok_pct / total_pct,
        "YouTube": youtube_pct / total_pct,
    }
    
    effective_cod_rate = COD_RETURN_RATE * (1.0 - (delivery_friction_reduction_pct / 100.0))
    shipping_cost_per_order = COURIER_FEE + (effective_cod_rate * RETURN_LOGISTICS_FEE)
    
    channel_results = []
    tot_revenue = 0.0
    tot_spend = 0.0
    tot_orders = 0
    tot_true_profit = 0.0
    
    for platform, share in pct_map.items():
        spend = total_budget * share
        params = RESPONSE_CURVE_PARAMS[platform]
        
        # Logarithmic saturation response: Revenue = alpha * ln(1 + beta * Spend)
        revenue = float(params["alpha"] * np.log1p(params["beta"] * spend))
        roas = revenue / spend if spend > 0 else 0.0
        
        # Estimate orders & conversions based on AOV
        orders = int(revenue / params["aov"]) if params["aov"] > 0 else 0
        cpa = spend / orders if orders > 0 else 0.0
        
        # Delivered economics
        delivered_rev = revenue * (1.0 - effective_cod_rate)
        cogs = delivered_rev * COGS_PCT
        shipping = orders * shipping_cost_per_order
        true_net_profit = delivered_rev - cogs - shipping - spend
        
        channel_results.append({
            "Platform": platform,
            "Share (%)": round(share * 100, 1),
            "Spend (PKR)": round(spend, 2),
            "Projected Revenue (PKR)": round(revenue, 2),
            "Projected ROAS": round(roas, 2),
            "Projected CPA (PKR)": round(cpa, 2),
            "Projected Orders": orders,
            "True Net Profit (PKR)": round(true_net_profit, 2),
        })
        
        tot_revenue += revenue
        tot_spend += spend
        tot_orders += orders
        tot_true_profit += true_net_profit
        
    blended_roas = round(tot_revenue / tot_spend, 2) if tot_spend > 0 else 0.0
    blended_cpa = round(tot_spend / tot_orders, 2) if tot_orders > 0 else 0.0
    profit_margin_pct = round((tot_true_profit / tot_revenue) * 100, 1) if tot_revenue > 0 else 0.0
    
    return {
        "channel_breakdown": pd.DataFrame(channel_results),
        "total_spend": round(tot_spend, 2),
        "total_revenue": round(tot_revenue, 2),
        "blended_roas": blended_roas,
        "blended_cpa": blended_cpa,
        "total_orders": tot_orders,
        "true_net_profit": round(tot_true_profit, 2),
        "net_profit_margin_pct": profit_margin_pct,
        "effective_cod_return_rate_pct": round(effective_cod_rate * 100, 1),
    }
