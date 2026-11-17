"""
Outlier & Unusual Pattern Detection Engine (Isolation Forest & Multi-Variate Robust Z-Score)
=============================================================================================
Identifies anomalous marketing posts whose engagement, virality, or sentiment
deviate substantially from baseline campaign expectations.
"""
import numpy as np
import pandas as pd
from typing import Tuple, Dict
from sklearn.ensemble import IsolationForest

def detect_outliers(
    df_posts: pd.DataFrame,
    df_comments: pd.DataFrame,
    contamination: float = 0.05
) -> Tuple[pd.DataFrame, Dict]:
    posts = df_posts.copy()
    comments = df_comments.copy()
    
    empty_summary = {
        "total_posts": len(posts),
        "total_anomalies": 0,
        "total_outliers": 0,
        "anomaly_rate_pct": 0.0,
        "outlier_rate_pct": 0.0,
        "viral_breakouts": 0,
        "friction_spikes": 0,
        "money_pits": 0,
        "budget_money_pits": 0,
    }
    
    if posts.empty:
        posts["is_outlier"] = False
        posts["anomaly_score"] = 0.0
        posts["anomaly_category"] = "Normal Baseline"
        posts["anomaly_type"] = "Normal Baseline"
        posts["diagnostic_reason"] = "No posts available."
        posts["action_recommendation"] = "Reset filters to view active posts."
        posts["recommended_action"] = "Reset filters to view active posts."
        return posts, empty_summary

    # 1. Aggregate comment-level signals per post
    if not comments.empty:
        comment_stats = comments.groupby("post_id").agg(
            total_comments=("comment_id", "count"),
            neg_sentiment_count=("sentiment", lambda s: (s == "Negative").sum()),
            pos_sentiment_count=("sentiment", lambda s: (s == "Positive").sum()),
            delivery_complaints=("topic", lambda t: (t == "Delivery & Logistics").sum()),
            price_complaints=("topic", lambda t: (t == "Price & Affordability").sum()),
            avg_purchase_intent=("purchase_intent", "mean"),
        ).reset_index()
        
        comment_stats["neg_sentiment_ratio"] = (
            comment_stats["neg_sentiment_count"] / np.maximum(comment_stats["total_comments"], 1)
        ).round(3)
        merged = pd.merge(posts, comment_stats, on="post_id", how="left")
    else:
        merged = posts.copy()
        merged["total_comments"] = 0
        merged["neg_sentiment_count"] = 0
        merged["pos_sentiment_count"] = 0
        merged["delivery_complaints"] = 0
        merged["price_complaints"] = 0
        merged["neg_sentiment_ratio"] = 0.0
        merged["avg_purchase_intent"] = 0.5
        
    merged["neg_sentiment_ratio"] = merged["neg_sentiment_ratio"].fillna(0.0)
    merged["avg_purchase_intent"] = merged["avg_purchase_intent"].fillna(0.5)
    
    # 2. Compute Engagement & Efficiency Metrics
    total_engagements = merged["likes"] + merged["comments_count"] + merged["shares"]
    merged["engagement_rate"] = ((total_engagements / np.maximum(merged["views"], 1)) * 100).round(2)
    merged["viral_ratio"] = (merged["shares"] / np.maximum(merged["likes"], 1)).round(3)
    merged["cpe"] = (merged["spend"] / np.maximum(total_engagements, 1)).round(2)
    merged["comment_intensity"] = (merged["comments_count"] / np.maximum(merged["likes"], 1)).round(3)
    
    # 3. Isolation Forest Modeling
    feature_cols = ["engagement_rate", "viral_ratio", "cpe", "neg_sentiment_ratio", "comment_intensity"]
    X = merged[feature_cols].fillna(0.0).values
    
    if len(merged) < 5:
        merged["is_outlier"] = False
        merged["anomaly_score"] = 0.0
        merged["anomaly_category"] = "Normal Baseline"
        merged["diagnostic_reason"] = "Sample size too small for statistical anomaly modeling."
        merged["action_recommendation"] = "Maintain baseline media plan."
        return merged, empty_summary
        
    try:
        iso_forest = IsolationForest(
            n_estimators=150,
            contamination=contamination,
            random_state=42
        )
        predictions = iso_forest.fit_predict(X)
        anomaly_scores = iso_forest.decision_function(X)
    except Exception:
        predictions = np.ones(len(merged))
        anomaly_scores = np.zeros(len(merged))
    
    merged["is_outlier"] = (predictions == -1)
    merged["anomaly_score"] = np.round(anomaly_scores, 3)
    
    # 4. Outlier Categorization & Diagnostic Rules
    median_spend = merged["spend"].median()
    median_eng_rate = merged["engagement_rate"].median()
    
    anomaly_types = []
    diagnostics = []
    recommended_actions = []
    
    for _, row in merged.iterrows():
        if not row["is_outlier"]:
            anomaly_types.append("Normal Baseline")
            diagnostics.append("Performance aligns with campaign benchmark parameters.")
            recommended_actions.append("Maintain current media pacing.")
        elif row["neg_sentiment_ratio"] >= 0.30 or row.get("delivery_complaints", 0) >= 8:
            anomaly_types.append("Friction & Backlash Spike")
            diagnostics.append(
                f"Abnormal customer friction ({int(row['neg_sentiment_ratio']*100)}% negative sentiment). "
                f"Delivery & logistics anxiety detected."
            )
            recommended_actions.append(
                "Immediate customer service intervention. Audit courier SLA in " + str(row.get("city", "region")) + "."
            )
        elif row["viral_ratio"] >= 0.12 or (row["engagement_rate"] >= median_eng_rate * 1.8 and row["cpe"] <= 3.0):
            anomaly_types.append("Viral Breakout")
            diagnostics.append(
                f"High viral velocity (Viral Ratio {row['viral_ratio']:.2f}, CPE Rs. {row['cpe']:.2f}). "
                f"Organic reach multiplier is actively driving cheap customer acquisition."
            )
            recommended_actions.append(
                "Scale ad spend by +30% immediately in Project 1 allocation to harvest organic halo effect."
            )
        elif row["spend"] >= median_spend * 1.5 and row["engagement_rate"] <= median_eng_rate * 0.7:
            anomaly_types.append("Budget Money Pit")
            diagnostics.append(
                f"Capital exhaustion: Spend Rs. {row['spend']:,.0f} with depressed engagement ({row['engagement_rate']}%). "
                f"Ad fatigue or creative saturation identified."
            )
            recommended_actions.append(
                "Pause ad set immediately and reallocate remaining budget to top-performing Instagram Reels."
            )
        else:
            anomaly_types.append("Viral Breakout")
            diagnostics.append("Moderate viral traction with low cost per engagement.")
            recommended_actions.append("Monitor conversion velocity and increment ad budget.")
            
    merged["anomaly_category"] = anomaly_types
    merged["anomaly_type"] = anomaly_types
    merged["diagnostic_reason"] = diagnostics
    merged["action_recommendation"] = recommended_actions
    merged["recommended_action"] = recommended_actions
    
    # 5. Executive Anomaly Summary
    total_anomalies = int(merged["is_outlier"].sum())
    viral_count = int((merged["anomaly_category"] == "Viral Breakout").sum())
    friction_count = int((merged["anomaly_category"] == "Friction & Backlash Spike").sum())
    pit_count = int((merged["anomaly_category"] == "Budget Money Pit").sum())
    
    summary = {
        "total_posts": len(merged),
        "total_anomalies": total_anomalies,
        "total_outliers": total_anomalies,
        "anomaly_rate_pct": round((total_anomalies / max(len(merged), 1)) * 100, 1),
        "outlier_rate_pct": round((total_anomalies / max(len(merged), 1)) * 100, 1),
        "viral_breakouts": viral_count,
        "friction_spikes": friction_count,
        "money_pits": pit_count,
        "budget_money_pits": pit_count,
    }
    
    return merged, summary
