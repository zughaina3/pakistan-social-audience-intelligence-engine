---
title: "**Project 3: Pakistan Social Audience & Campaign Intelligence
  Engine (Clustering Based)**"
---

1.  **The real business problem**

Imagine a Lahore-based online brand (e. g. clothing, Perfume etc.) runs
**Instagram, TikTok** and **Facebook** campaigns for its **11.11** or
**12.12 collection**.

The marketing team receives thousands of comments such as:

-   "Price please?"

-   "Is this available in Karachi?"

-   "Very beautiful dress!"

-   "Price bohat zyada hai."

-   "Delivery kitne din mein hogi?"

-   "Any discount on this suit?"

-   "Ordered last week, still waiting."

-   "Inbox me details send kar dein."

The brand has engagement data, comments, campaign metrics and product
information, but it doesn\'t know which customer needs or content
patterns are hidden inside these interactions.

**Task:** Build an engine that groups similar audience behaviours,
identifies unusual patterns and converts those discoveries into
practical marketing decisions.

The goal is not merely to classify comments as positive or negative.
Project 1 can cover content analysis, while this project concentrates on
discovering audience segments and campaign opportunities.

2.  **What exactly will you build?**

A small web application that answers five marketing questions.

-   **Which content attracts attention?**

> Compare reels, product photos, influencer posts, styling videos, sale
> announcements and Eid campaigns using likes, comments, shares and
> views where publicly available.

-   **What does the audience want?**

> Group comments around price, fabric quality, sizing, delivery,
> discounts, availability and purchase interest.

-   **Which marketing patterns are unusual?**

> Identify posts whose engagement or comment patterns differ
> substantially from comparable posts, for further investigation.

-   **Which audience needs should the brand address?**

> Discover groups such as discount-focused commenters,
> delivery-concerned shoppers and customers asking about product
> availability.

-   **What should the marketing team do next?**

> Generate evidence-based recommendations for content, promotions,
> customer service and campaign testing.

3.  **The data: a concrete Pakistani example\
    **

> Start with a single product category, such as women\'s lawn suits,
> rather than trying to cover every industry.
>
> Collect or prepare approximately 2,000--5,000 public post records and
> associated comments for a class demonstration. You can extend the
> dataset if suitable data access is available.
>
> A useful starting point is to examine public posts from brands such as
> Sapphire, Khaadi, and Gul Ahmed. Use permitted access methods and
> follow each platform\'s terms; do not assume that all comments or
> analytics are publicly downloadable.

**Table A --- Social media posts**

  -----------------------------------------------------------------------
  **Field**                                   **Example**
  ------------------------------------------- ---------------------------
  post_id                                     P001

  brand                                       Brand A

  platform                                    Instagram

  campaign                                    Eid Collection

  content_type                                Reel

  product_category                            Lawn suit

  likes                                       1,250

  comments_count                              186

  shares                                      95, if available

  views                                       25,000, if available

  days_since_post                             5
  -----------------------------------------------------------------------

**Table B --- Comments**

  -----------------------------------------------------------------------
  **Field**                    **Example**
  ---------------------------- ------------------------------------------
  post_id                      P001

  comment_text                 "Price please?"

  language_type                English / Roman Urdu / Urdu

  topic                        Price inquiry

  sentiment                    Neutral

  purchase_intent              Possible inquiry
  -----------------------------------------------------------------------

The examples above are illustrative, not actual measurements from those
brands.

For a research-oriented version, keep the source URL, collection date,
data provenance and applicable reuse permissions. Separate actual
observations from generated or simulated records.

4.  **Where can you obtain data?**

-   **Pakistani fashion brand research**

A 2026 paper, Sentiment Analysis of Social Media Data for Pakistani
Fashion Brand Monitoring Using Machine Learning, describes a dataset of
10,602 observations involving 17 Pakistani fashion brands across seven
platforms. Check the paper and its accompanying materials for actual
dataset and code availability before planning to reuse it.

<https://www.thesesjournal.com/index.php/1/article/view/3247?utm_source=chatgpt.com>

-   **Pakistan\'s largest e-commerce dataset**

Open Data Pakistan lists approximately half a million historical order
records, including order status, category, payment method and customer
identifiers. This is useful for building an additional transaction-based
analysis, but it is not a social-media comments dataset. Check the
dataset\'s reuse permissions before distributing it to students.

> <https://opendata.com.pk/dataset/pakistan-largest-ecommerce-dataset?utm_source=chatgpt.com>

-   **Pakistani Fashion Catalogue**

This small open-source project provides 75 product records from five
Pakistani retailers, with product categories and PKR prices. Use it to
add product context to the marketing analysis, not as a substitute for
real audience-engagement data.

<https://huggingface.co/datasets/Osama-Ansar/pakistani-fashion-catalogue?utm_source=chatgpt.com>
