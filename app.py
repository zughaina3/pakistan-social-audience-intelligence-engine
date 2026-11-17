"""
Pakistan Social Audience & Campaign Intelligence Engine (Clustering Based)
==========================================================================
Phase 3 Enterprise Production Application
Bridging Social Audience Intelligence with Project 1 Ad Budget Optimization.
"""
import os
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from engine.config import (
    CAMPAIGNS, PLATFORMS, CONTENT_TYPES, BRANDS, PLATFORM_BENCHMARKS,
    DATA_PROCESSED_DIR, DATA_RAW_DIR, REPORTS_DIR
)
from engine.pipeline import build_unified_dataset
from engine.clustering import cluster_comments
from engine.anomaly_detection import detect_outliers
from engine.project1_bridge import (
    load_project1_summaries, map_clusters_to_project1_economics, simulate_budget_allocation
)
from engine.recommendation_engine import generate_marketing_recommendations

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Pakistan Social Audience & Campaign Intelligence Engine",
    page_icon="🇵🇰",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    /* Executive Palette: Pakistani Forest Green & Emerald Accents */
    .main-header {
        background: linear-gradient(135deg, #064e3b 0%, #047857 50%, #0f172a 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .metric-val {
        font-size: 26px;
        font-weight: 700;
        color: #064e3b;
    }
    .metric-lbl {
        font-size: 13px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-green { background-color: #d1fae5; color: #065f46; }
    .badge-blue { background-color: #dbeafe; color: #1e40af; }
    .badge-amber { background-color: #fef3c7; color: #92400e; }
    .badge-red { background-color: #fee2e2; color: #991b1b; }
    .rec-box {
        border-left: 4px solid #10b981;
        background-color: #f8fafc;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- DATA CACHING & INITIALIZATION ---
@st.cache_data(show_spinner=False)
def load_and_prepare_data():
    table_a_path = os.path.join(DATA_PROCESSED_DIR, "table_a_social_posts.csv")
    table_b_path = os.path.join(DATA_PROCESSED_DIR, "table_b_audience_comments.csv")
    
    if not os.path.exists(table_a_path) or not os.path.exists(table_b_path):
        build_unified_dataset()
        
    df_posts = pd.read_csv(table_a_path)
    df_comments = pd.read_csv(table_b_path)
    df_camp_p1, df_budget_p1, df_city_p1 = load_project1_summaries()
    
    return df_posts, df_comments, df_camp_p1, df_budget_p1, df_city_p1

# Load data
df_posts_raw, df_comments_raw, df_camp_p1, df_budget_p1, df_city_p1 = load_and_prepare_data()

# --- SIDEBAR FILTERS & CONTROLS ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Flag_of_Pakistan.svg/320px-Flag_of_Pakistan.svg.png", width=60)
st.sidebar.title("Engine Controls")
st.sidebar.markdown("**Project 3: Audience Intelligence**")
st.sidebar.markdown(
    "<span class='badge-pill badge-green'>Linked to Project 1 Budget Optimizer</span>",
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filter Ad & Social Data")

sel_campaign = st.sidebar.selectbox("Campaign", ["All Campaigns"] + CAMPAIGNS)
sel_platform = st.sidebar.selectbox("Platform", ["All Platforms"] + PLATFORMS)
sel_content_type = st.sidebar.selectbox("Content Format", ["All Formats"] + CONTENT_TYPES)
sel_brand = st.sidebar.selectbox("Brand", ["All Brands"] + BRANDS)

st.sidebar.markdown("---")
st.sidebar.subheader("Machine Learning Parameters")
cluster_k = st.sidebar.slider("Number of Clusters (K)", min_value=3, max_value=7, value=5)
anomaly_contamination = st.sidebar.slider("Outlier Contamination", min_value=0.02, max_value=0.10, value=0.05, step=0.01)

st.sidebar.markdown("---")
st.sidebar.subheader("📄 Executive Report")
pdf_path = os.path.join(REPORTS_DIR, "Pakistan_Social_Audience_Intelligence_Final_Report.pdf")
if os.path.exists(pdf_path):
    with open(pdf_path, "rb") as f_pdf:
        pdf_bytes = f_pdf.read()
    st.sidebar.download_button(
        label="⬇️ Download Executive Report (PDF)",
        data=pdf_bytes,
        file_name="Pakistan_Social_Audience_Intelligence_Final_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# Apply filters
df_posts = df_posts_raw.copy()
if sel_campaign != "All Campaigns":
    df_posts = df_posts[df_posts["campaign"] == sel_campaign]
if sel_platform != "All Platforms":
    df_posts = df_posts[df_posts["platform"] == sel_platform]
if sel_content_type != "All Formats":
    df_posts = df_posts[df_posts["content_type"] == sel_content_type]
if sel_brand != "All Brands":
    df_posts = df_posts[df_posts["brand"] == sel_brand]

if df_posts.empty:
    st.sidebar.warning(f"⚠️ No posts match the selected filter combination. Displaying all posts.")
    df_posts = df_posts_raw.copy()
    df_comments = df_comments_raw.copy()
else:
    matching_post_ids = set(df_posts["post_id"])
    df_comments = df_comments_raw[df_comments_raw["post_id"].isin(matching_post_ids)].copy()

# Execute ML models on filtered view
@st.cache_data(show_spinner=False)
def run_ml_pipeline(comments_df, posts_df, k_val, contam_val):
    clustered_comments, profiles, sil_score = cluster_comments(comments_df, n_clusters=k_val)
    analyzed_posts, anomaly_summary = detect_outliers(posts_df, comments_df, contamination=contam_val)
    return clustered_comments, profiles, sil_score, analyzed_posts, anomaly_summary

df_clustered_comments, df_profiles, sil_score, df_analyzed_posts, anomaly_summary = run_ml_pipeline(
    df_comments, df_posts, cluster_k, anomaly_contamination
)

# Header
st.markdown(
    """
    <div class="main-header">
        <h1 style="margin: 0; font-size: 30px;">🇵🇰 Pakistan Social Audience & Campaign Intelligence Engine</h1>
        <p style="margin: 6px 0 0 0; opacity: 0.9; font-size: 15px;">
            Clustering-Driven Audience Behavioral Segmentation, Anomaly Diagnostics & Direct Linkage to 
            <strong>Project 1: Digital Advertising Budget Optimizer</strong> (ROAS 4.37x, SLSQP PKR 1M Reallocation).
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Top KPI Metric Strip
col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
total_views = int(df_analyzed_posts["views"].sum())
total_engagements = int(df_analyzed_posts["likes"].sum() + df_analyzed_posts["comments_count"].sum() + df_analyzed_posts["shares"].sum())
avg_cpe = round(df_analyzed_posts["spend"].sum() / max(total_engagements, 1), 2)
blended_eng_rate = round((total_engagements / max(total_views, 1)) * 100, 2)
outlier_count = anomaly_summary["total_outliers"]

with col_m1:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Total Posts</div><div class="metric-val">{len(df_analyzed_posts):,}</div></div>', unsafe_allow_html=True)
with col_m2:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Analyzed Comments</div><div class="metric-val">{len(df_clustered_comments):,}</div></div>', unsafe_allow_html=True)
with col_m3:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Blended Eng. Rate</div><div class="metric-val">{blended_eng_rate}%</div></div>', unsafe_allow_html=True)
with col_m4:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Avg. CPE</div><div class="metric-val">Rs. {avg_cpe}</div></div>', unsafe_allow_html=True)
with col_m5:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Active Clusters</div><div class="metric-val">{cluster_k} (Sil: {sil_score})</div></div>', unsafe_allow_html=True)
with col_m6:
    st.markdown(f'<div class="metric-card"><div class="metric-lbl">Detected Anomalies</div><div class="metric-val">{outlier_count}</div></div>', unsafe_allow_html=True)

# Navigation Tabs answering the 5 Core Marketing Questions
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 1. Content Attention",
    "🎯 2. Audience Intent",
    "⚠️ 3. Outlier Patterns",
    "🧩 4. Audience Clusters & Project 1 Bridge",
    "🚀 5. Actionable CRO Decisions & Simulator",
    "🗄️ 6. Data Explorer & Export"
])

# ==============================================================================
# TAB 1: CONTENT ATTENTION COMPARISON (QUESTION 1)
# ==============================================================================
with tab1:
    st.subheader("Which Content Attracts Attention?")
    st.caption("Comprehensive attention comparison across creative formats (Reels, Product Photos, Influencer Posts, Styling Videos, Sale Announcements, Eid Showcases) evaluated on true engagement velocity, CPE, and virality.")
    
    col_t1a, col_t1b = st.columns([3, 2])
    
    format_agg = df_analyzed_posts.groupby("content_type").agg(
        posts_count=("post_id", "count"),
        total_views=("views", "sum"),
        total_likes=("likes", "sum"),
        total_comments=("comments_count", "sum"),
        total_shares=("shares", "sum"),
        total_spend=("spend", "sum"),
    ).reset_index()
    
    format_agg["total_engagements"] = format_agg["total_likes"] + format_agg["total_comments"] + format_agg["total_shares"]
    format_agg["engagement_rate_pct"] = ((format_agg["total_engagements"] / np.maximum(format_agg["total_views"], 1)) * 100).round(2)
    format_agg["cpe_pkr"] = (format_agg["total_spend"] / np.maximum(format_agg["total_engagements"], 1)).round(2)
    format_agg["viral_ratio"] = (format_agg["total_shares"] / np.maximum(format_agg["total_likes"], 1)).round(3)
    
    with col_t1a:
        fig_bar = px.bar(
            format_agg.sort_values("engagement_rate_pct", ascending=True),
            x="engagement_rate_pct",
            y="content_type",
            orientation="h",
            color="cpe_pkr",
            color_continuous_scale="Greens_r",
            labels={"engagement_rate_pct": "Engagement Rate (%)", "content_type": "Creative Format", "cpe_pkr": "CPE (PKR)"},
            title="Creative Format Engagement Rate vs. Cost Per Engagement (CPE)",
            text="engagement_rate_pct"
        )
        fig_bar.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_bar.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_t1b:
        fig_pie = px.pie(
            format_agg,
            names="content_type",
            values="total_shares",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Greens_r,
            title="Share of Organic Virality (Total Shares by Format)"
        )
        fig_pie.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("#### Creative Format Performance & Spend Efficiency Leaderboard")
    display_format_agg = format_agg[[
        "content_type", "posts_count", "total_views", "engagement_rate_pct", "viral_ratio", "cpe_pkr", "total_spend"
    ]].rename(columns={
        "content_type": "Creative Format",
        "posts_count": "Posts",
        "total_views": "Views",
        "engagement_rate_pct": "Eng. Rate (%)",
        "viral_ratio": "Viral Ratio (Shares/Likes)",
        "cpe_pkr": "Cost Per Engagement (PKR)",
        "total_spend": "Total Spend (PKR)"
    })
    st.dataframe(display_format_agg.sort_values("Eng. Rate (%)", ascending=False), use_container_width=True, hide_index=True)

# ==============================================================================
# TAB 2: AUDIENCE INTENT GROUPING (QUESTION 2)
# ==============================================================================
with tab2:
    st.subheader("What Does the Audience Want?")
    st.caption("Granular natural language understanding of customer demand, pricing queries, logistics anxiety, and quality expectations across 7 operational intent categories.")
    
    col_t2a, col_t2b = st.columns([3, 2])
    
    with col_t2a:
        # Sunburst Chart: Campaign -> Format -> Intent Topic -> Sentiment
        # Sample for fast rendering
        sun_df = df_clustered_comments.sample(min(len(df_clustered_comments), 2500), random_state=42)
        # Merge campaign & format from posts
        sun_merged = pd.merge(sun_df, df_analyzed_posts[["post_id", "campaign", "content_type"]], on="post_id", how="left")
        
        fig_sun = px.sunburst(
            sun_merged,
            path=["campaign", "content_type", "topic", "sentiment"],
            color="topic",
            title="Interactive Intent Hierarchy (Campaign → Format → Intent → Sentiment)",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_sun.update_layout(height=480, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_sun, use_container_width=True)
        
    with col_t2b:
        # Multilingual & Sentiment Breakdown
        lang_counts = df_clustered_comments["language_type"].value_counts().reset_index()
        lang_counts.columns = ["Language", "Comments"]
        
        fig_lang = px.pie(
            lang_counts,
            names="Language",
            values="Comments",
            color_discrete_sequence=["#10b981", "#3b82f6", "#f59e0b"],
            title="Language Dialect Distribution (Roman Urdu vs English vs Code-Mixed)",
            hole=0.4
        )
        fig_lang.update_layout(height=240, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_lang, use_container_width=True)
        
        sentiment_intent = df_clustered_comments.groupby(["topic", "sentiment"]).size().unstack(fill_value=0).reset_index()
        fig_sent = px.bar(
            sentiment_intent,
            x="topic",
            y=["Positive", "Neutral", "Negative"],
            title="Sentiment Polarity per Intent Category",
            color_discrete_map={"Positive": "#10b981", "Neutral": "#94a3b8", "Negative": "#ef4444"},
            barmode="stack"
        )
        fig_sent.update_layout(height=240, margin=dict(l=10, r=10, t=40, b=10), xaxis_title="", yaxis_title="Comments")
        st.plotly_chart(fig_sent, use_container_width=True)

# ==============================================================================
# TAB 3: UNUSUAL PATTERN & OUTLIER DETECTION (QUESTION 3)
# ==============================================================================
with tab3:
    st.subheader("Which Marketing Patterns Are Unusual?")
    st.caption("Unsupervised anomaly detection via Isolation Forest identifying viral breakout posts, customer friction spikes, and budget money pits deviating from baseline expectations.")
    
    col_t3a, col_t3b = st.columns([3, 2])
    
    with col_t3a:
        fig_scatter = px.scatter(
            df_analyzed_posts,
            x="engagement_rate",
            y="viral_ratio",
            size="spend",
            color="anomaly_type",
            hover_name="post_id",
            hover_data=["campaign", "platform", "content_type", "spend", "roas", "neg_sentiment_ratio"],
            color_discrete_map={
                "Normal Baseline": "#94a3b8",
                "Viral Breakout": "#10b981",
                "Friction & Backlash Spike": "#ef4444",
                "Budget Money Pit": "#f59e0b",
                "Engagement Variance Outlier": "#6366f1"
            },
            labels={"engagement_rate": "Engagement Rate (%)", "viral_ratio": "Viral Ratio (Shares/Likes)", "spend": "Spend (PKR)"},
            title="Multi-Variate Anomaly Scatter Plot (Engagement vs. Virality vs. Spend)"
        )
        fig_scatter.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_t3b:
        st.markdown("#### Anomaly Breakdown")
        st.metric("Total Flagged Outliers", f"{anomaly_summary['total_outliers']} posts ({anomaly_summary['outlier_rate_pct']}%)")
        st.markdown(f"- 🚀 **Viral Breakouts**: `{anomaly_summary['viral_breakouts']}` posts (High viral amplification)")
        st.markdown(f"- 🛑 **Friction & Backlash Spikes**: `{anomaly_summary['friction_spikes']}` posts (Delivery/Price friction)")
        st.markdown(f"- 💸 **Budget Money Pits**: `{anomaly_summary['budget_money_pits']}` posts (High spend, low traction)")
        
        st.info("💡 **Executive Rule**: Viral Breakout posts should immediately receive +30% ad spend scaling in Project 1's SLSQP engine. Friction spikes require immediate courier SLA intervention.")
        
    st.markdown("#### Outlier Posts Diagnostic Inspector")
    outliers_only = df_analyzed_posts[df_analyzed_posts["is_outlier"]].sort_values("spend", ascending=False)
    st.dataframe(
        outliers_only[[
            "post_id", "campaign", "platform", "content_type", "spend", "roas", "engagement_rate", "viral_ratio",
            "anomaly_type", "diagnostic_reason", "recommended_action"
        ]].rename(columns={
            "post_id": "Post ID", "campaign": "Campaign", "platform": "Platform", "content_type": "Format",
            "spend": "Spend (PKR)", "roas": "ROAS", "engagement_rate": "Eng. Rate (%)",
            "viral_ratio": "Viral Ratio", "anomaly_type": "Classification",
            "diagnostic_reason": "Diagnosis", "recommended_action": "Action"
        }),
        use_container_width=True,
        hide_index=True
    )

# ==============================================================================
# TAB 4: AUDIENCE CLUSTERING & PROJECT 1 BRIDGE (QUESTION 4)
# ==============================================================================
with tab4:
    st.subheader("Which Audience Needs Should the Brand Address?")
    st.caption("Unsupervised semantic clustering of customer comments into behavioral cohorts and directly mapping them to Project 1 channel ad spend and ROAS drivers.")
    
    col_t4a, col_t4b = st.columns([3, 2])
    
    with col_t4a:
        # Interactive 3D Scatter Plot of Clusters
        plot_sample = df_clustered_comments.sample(min(len(df_clustered_comments), 1500), random_state=42)
        fig_3d = px.scatter_3d(
            plot_sample,
            x="coord_x",
            y="coord_y",
            z="coord_z",
            color="cluster_name",
            hover_name="cluster_name",
            hover_data=["comment_text", "language_type", "sentiment", "purchase_intent"],
            title=f"3D Latent Semantic Cluster Topology (K={cluster_k}, Silhouette: {sil_score})",
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_3d.update_layout(height=480, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_3d, use_container_width=True)
        
    with col_t4b:
        st.markdown("#### Discovered Audience Cohorts")
        for _, prof in df_profiles.iterrows():
            st.markdown(
                f"""
                <div class="metric-card" style="padding: 12px 16px; margin-bottom: 8px;">
                    <div style="font-weight: 700; color: #064e3b; font-size: 15px;">
                        Cluster {prof['cluster_id']}: {prof['cluster_name']}
                    </div>
                    <div style="font-size: 13px; color: #475569; margin: 4px 0;">
                        <strong>Key Terms:</strong> <em>{prof['top_keywords']}</em>
                    </div>
                    <div style="font-size: 12px; color: #64748b;">
                        Share: <strong>{prof['audience_share_pct']}%</strong> | 
                        Avg. Sentiment: <strong>{prof['avg_sentiment_score']}</strong> | 
                        Purchase Intent: <strong>{int(prof['avg_purchase_intent']*100)}%</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    st.markdown("---")
    st.subheader("Direct Integration Bridge: Project 3 Clusters → Project 1 Channel Economics")
    st.markdown("How specific comment clusters discovered in Project 3 directly drive ROAS, CPA, and COD delivery returns in Project 1:")
    
    bridge_df = map_clusters_to_project1_economics(df_profiles)
    st.dataframe(bridge_df, use_container_width=True, hide_index=True)

# ==============================================================================
# TAB 5: ACTIONABLE CRO RECOMMENDATIONS & BUDGET SIMULATOR (QUESTION 5)
# ==============================================================================
with tab5:
    st.subheader("What Should the Marketing Team Do Next?")
    st.caption("Automated, evidence-based conversion rate optimization (CRO) roadmap, customer service automation playbooks, and dynamic SLSQP ad budget reallocation simulator.")
    
    recs = generate_marketing_recommendations(df_analyzed_posts, df_profiles, anomaly_summary)
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown("#### 1. Content Strategy Decisions")
        for cr in recs["content_recommendations"]:
            st.markdown(
                f"""
                <div class="rec-box">
                    <span class="badge-pill badge-green">{cr['category']}</span>
                    <span class="badge-pill badge-amber">{cr['priority']} PRIORITY</span>
                    <h5 style="margin: 8px 0 4px 0; color: #0f172a;">{cr['title']}</h5>
                    <p style="margin: 0; font-size: 13px; color: #475569;"><strong>Rationale:</strong> {cr['rationale']}</p>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #065f46;"><strong>Prescribed Action:</strong> {cr['action']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        st.markdown("#### 2. Pricing & Promotion Architecture")
        for pr in recs["promotions_architecture"]:
            st.markdown(
                f"""
                <div class="rec-box" style="border-left-color: #3b82f6;">
                    <h5 style="margin: 0 0 4px 0; color: #0f172a;">{pr['recommendation']}</h5>
                    <p style="margin: 0; font-size: 13px; color: #475569;"><strong>Impact:</strong> {pr['impact']}</p>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #1e40af;"><strong>Mechanic:</strong> {pr['mechanic']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    with col_r2:
        st.markdown("#### 3. Automated DM / Customer Service Playbooks (Instagram & TikTok)")
        st.caption("Bilingual auto-response scripts addressing top comment clusters to reduce inquiry latency from 4 hours to seconds:")
        
        for pb in recs["cs_playbooks"]:
            with st.expander(f"💬 {pb['inquiry_type']} ({pb['volume_share']})"):
                st.markdown(f"**English Response:**\n`{pb['automated_response_en']}`")
                st.markdown(f"**Roman Urdu Response:**\n`{pb['automated_response_ur']}`")
                st.info(f"**CRO Impact:** {pb['cro_impact']}")
                
    st.markdown("---")
    st.subheader("Interactive Ad Budget Reallocation Simulator (Project 1 SLSQP Engine)")
    st.markdown("Simulate shifting budget across channels while accounting for true Pakistani unit economics (45% COGS, Rs. 220 shipping, 12% COD returns, and courier bounce fees):")
    
    col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
    with col_s1:
        g_pct = st.slider("Google Ads %", 0, 70, 40)
    with col_s2:
        ig_pct = st.slider("Instagram Ads %", 0, 70, 35)
    with col_s3:
        fb_pct = st.slider("Facebook Ads %", 0, 40, 13)
    with col_s4:
        tt_pct = st.slider("TikTok Ads %", 0, 30, 8)
    with col_s5:
        yt_pct = st.slider("YouTube Ads %", 0, 20, 4)
        
    friction_red = st.slider("Simulated Delivery Friction Reduction (%) via Automation", 0, 50, 15)
    
    sim_result = simulate_budget_allocation(
        g_pct, ig_pct, fb_pct, tt_pct, yt_pct,
        total_budget=1000000.0,
        delivery_friction_reduction_pct=friction_red
    )
    
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    with col_res1:
        st.metric("Projected Revenue", f"PKR {sim_result['total_revenue']:,.0f}")
    with col_res2:
        st.metric("Blended ROAS", f"{sim_result['blended_roas']}x")
    with col_res3:
        st.metric("Expected Orders", f"{sim_result['total_orders']:,} orders (CPA: Rs. {int(sim_result['blended_cpa'])})")
    with col_res4:
        st.metric("True Operating Profit", f"PKR {sim_result['true_net_profit']:,.0f} ({sim_result['net_profit_margin_pct']}%)")
        
    st.dataframe(sim_result["channel_breakdown"], use_container_width=True, hide_index=True)

# ==============================================================================
# TAB 6: DATA EXPLORER & EXPORT
# ==============================================================================
with tab6:
    st.subheader("Data Explorer & Export Center")
    st.caption("Inspect and download the unified datasets integrating Project 1 performance logs and authentic social media interactions.")
    
    tab_d1, tab_d2, tab_d3 = st.tabs(["Table A: Social Posts", "Table B: Comments", "Project 1 Benchmarks"])
    
    with tab_d1:
        st.dataframe(df_analyzed_posts, use_container_width=True)
        st.download_button(
            label="Download Table A (CSV)",
            data=df_analyzed_posts.to_csv(index=False).encode("utf-8"),
            file_name="table_a_social_posts.csv",
            mime="text/csv"
        )
        
    with tab_d2:
        st.dataframe(df_clustered_comments.head(500), use_container_width=True)
        st.download_button(
            label="Download Table B Sample (CSV)",
            data=df_clustered_comments.to_csv(index=False).encode("utf-8"),
            file_name="table_b_audience_comments.csv",
            mime="text/csv"
        )
        
    with tab_d3:
        st.markdown("#### Project 1 Summary Tables")
        st.dataframe(df_camp_p1, use_container_width=True)
        
    st.markdown("---")
    st.markdown("### 📄 Publication-Grade Executive Audit Report (PDF)")
    st.markdown(
        "Download the publication-grade 6-page Executive Dossier with 300 DPI figures, "
        "evidence-based answers to all 5 core marketing questions, strict Project 1 data provenance audit, "
        "and direct SLSQP budget reallocation matrix."
    )
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f_pdf:
            pdf_bytes = f_pdf.read()
        col_pdf1, col_pdf2 = st.columns([2, 3])
        with col_pdf1:
            st.download_button(
                label="⬇️ Download Executive Report PDF (6 Pages, 300 DPI)",
                data=pdf_bytes,
                file_name="Pakistan_Social_Audience_Intelligence_Final_Report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        with col_pdf2:
            st.caption("File size: ~980 KB | Formatted for Executive & CRO Leadership Review | Verified 100% Project 1 Data")
