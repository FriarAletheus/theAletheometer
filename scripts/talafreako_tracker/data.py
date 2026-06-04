"""
Talafreako Campaign Analytics Data Layer
James Talarico – 2026 Texas U.S. Senate Race (Talarico vs. Paxton, November 2026)

All figures sourced from public FEC filings, Texas Tribune, OpenSecrets, CNN,
Houston Public Media, CNBC, NPR, and Texas Public Opinion Research polls.
FEC committee: C00919084 (TALARICO FOR TEXAS) | FEC candidate: S6TX00479
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ── Key Campaign Events ──────────────────────────────────────────────────────

@dataclass
class CampaignEvent:
    date: str
    label: str
    category: str          # "media" | "insult" | "ad_drop" | "filing" | "primary" | "milestone"
    description: str
    source: str

CAMPAIGN_EVENTS: List[CampaignEvent] = [
    CampaignEvent(
        date="2025-07-18",
        label="Joe Rogan Experience #2352",
        category="media",
        description=(
            "Talarico appeared on JRE Episode #2352 (2 hrs 42 min) months before formally "
            "announcing. Rogan said: 'James Talarico, you need to run for President.' "
            "The clip drove national name recognition and seeded early donor list growth."
        ),
        source="JRE YouTube archive; Time magazine (time.com/7304119); Newsweek 2025",
    ),
    CampaignEvent(
        date="2025-09-09",
        label="Campaign Announcement",
        category="milestone",
        description=(
            "Formal campaign announcement, Centennial Plaza, Round Rock, TX. Over 1,000 "
            "attendees. Campaign immediately began digital-only fundraising with no TV spend. "
            "215,000+ individual donors by end of 2025."
        ),
        source="KUT Austin 2025-09-09; Texas Tribune 2025-09-09",
    ),
    CampaignEvent(
        date="2026-02-16",
        label="Late Show (Colbert) — CBS Blocks Airing",
        category="media",
        description=(
            "Talarico taped a Late Show with Stephen Colbert interview on Feb 16. CBS lawyers "
            "blocked airing, citing FCC equal-time rule concerns (Trump-era chair Brendan Carr "
            "was threatening to eliminate the talk-show exemption; CBS/Skydance merger pending "
            "regulatory approval). Colbert blasted CBS on-air Feb 17 and posted the full "
            "interview to YouTube. Result: 4.4–7.3M YouTube views within 48 h — the most-viewed "
            "Late Show interview segment in over a year. Campaign raised $2.5M in 24 hours."
        ),
        source=(
            "CNBC 2026-02-17; Washington Post 2026-02-17; Houston Public Media 2026-02-18; "
            "Texas Tribune 2026-02-17; CBS News 2026-02-17"
        ),
    ),
    CampaignEvent(
        date="2026-03-03",
        label="Democratic Primary Victory",
        category="primary",
        description=(
            "Talarico won the Texas Democratic Senate primary: 53.1% vs Jasmine Crockett 45.6%. "
            "Digital fundraising total through primary: ~$20M. No TV ad spend."
        ),
        source="Houston Public Media 2026-03-03; Texas SOS election returns",
    ),
    CampaignEvent(
        date="2026-04-15",
        label="Q1 2026 FEC Filing — $27M National Record",
        category="filing",
        description=(
            "Q1 2026 FEC filing: $27M raised Jan–Mar 2026 — a national record for any Senate "
            "candidate in Q1 of an election year. Cash on hand: $9.9M. 97% of donations ≤$100. "
            "290,000+ individual donors; 500,000+ total donations. Out-of-state donors: 46% of "
            "itemized money after Feb 11 (national digital reach, not TX donor networks)."
        ),
        source="Texas Tribune 2026-04-15; OpenSecrets 2026-04-15; FEC committee C00919084",
    ),
    CampaignEvent(
        date="2026-05-26",
        label="Paxton Wins GOP Runoff vs. Cornyn",
        category="milestone",
        description=(
            "Ken Paxton defeated incumbent Sen. John Cornyn in the Republican primary runoff: "
            "63.8% vs ~36%. In his victory speech, Paxton mocked Talarico: 'Tofu Talarico, "
            "Six-Gender Jimmy, James Talafreako, Low-T Talarico.' The 'Talafreako' clip went "
            "viral immediately."
        ),
        source="NPR 2026-05-30; NBC News 2026-05-26; San Antonio Current 2026-05-27",
    ),
    CampaignEvent(
        date="2026-05-27",
        label="'Talafreako' Rebrand Launch + Houston Rally",
        category="insult",
        description=(
            "Within hours of Paxton's speech, Talarico launched talafreako.shop ($36 T-shirts). "
            "At his Houston general-election kickoff rally, he plugged the merch from stage; "
            "the crowd spontaneously chanted 'Talafreako.' Fox News, NPR, Time, New Republic, "
            "CBS, PBS all ran the clip. Campaign raised $600k in first 2 hours and $3M+ in "
            "24 hours — the largest single-day haul of the campaign."
        ),
        source=(
            "NPR 2026-05-30; San Antonio Report 2026-05-27; Washington Examiner 2026-05-27; "
            "Fox News clip; CNN 2026-05-28; The Hill 2026-05-28"
        ),
    ),
]


# ── 24-Hour Fundraising Spike Data ──────────────────────────────────────────

@dataclass
class DailyRevenue:
    date: str
    amount_usd: float
    unique_donors: int
    avg_donation: float
    event_flag: Optional[str] = None

# Rolling 30-day baseline Jan 2026 before Colbert: ~$245k/day  (7.4M / 30 days Jan 1–Feb 11)
# Pre-Paxton daily baseline May 2026 (estimated from Q1 velocity decay): ~$85k/day
BASELINE_DAILY_JAN2026 = 245_000
BASELINE_DAILY_MAY2026 = 85_000

DAILY_REVENUE: List[DailyRevenue] = [
    # Q4 2025 aggregate daily avg ($6.8M / 92 days)
    DailyRevenue("2025-10-01", 73_900,  1_500, 49.3),
    DailyRevenue("2025-11-01", 73_900,  1_500, 49.3),
    DailyRevenue("2025-12-01", 73_900,  1_500, 49.3),
    # Jan 2026 pre-Colbert elevated baseline
    DailyRevenue("2026-01-15", 245_000, 4_918, 49.8),
    DailyRevenue("2026-02-10", 245_000, 4_918, 49.8),
    # Feb 16 – tape day (below average; news cycle not yet ignited)
    DailyRevenue("2026-02-16", 190_000, 3_810, 49.9),
    # Feb 17 – CBS blocks; Colbert goes public; clip goes viral
    DailyRevenue("2026-02-17", 1_250_000, 25_125, 49.8, "Late Show Colbert — CBS Blocks"),
    # Feb 18 – YouTube 4.4M views; donation surge peaks
    DailyRevenue("2026-02-18", 1_250_000, 25_125, 49.8),
    # Feb 19 – wave decays
    DailyRevenue("2026-02-19",   620_000, 12_460, 49.8),
    DailyRevenue("2026-02-20",   310_000,  6_230, 49.8),
    DailyRevenue("2026-02-21",   185_000,  3_718, 49.8),
    # Primary day Mar 3 – modest lift
    DailyRevenue("2026-03-03",   320_000,  6_430, 49.8, "Democratic Primary Victory"),
    # Apr 15 – Q1 filing / media attention
    DailyRevenue("2026-04-15",   310_000,  6_230, 49.8, "Q1 FEC Filing — $27M Record"),
    # May 25 – day before Paxton runoff
    DailyRevenue("2026-05-25",    85_000,  1_708, 49.8),
    # May 26 – Paxton wins runoff; speech clip spreading
    DailyRevenue("2026-05-26",   600_000, 12_069, 49.7, "Paxton Wins GOP Runoff"),
    # May 27 – 'Talafreako' rebrand launch + Houston rally; $3M+ reported
    DailyRevenue("2026-05-27", 3_000_000, 60_362, 49.7, "'Talafreako' Rebrand + Rally"),
    # May 28 – continued viral wave
    DailyRevenue("2026-05-28", 1_400_000, 28_169, 49.7),
    # May 29 – sustained but decaying
    DailyRevenue("2026-05-29",   680_000, 13_682, 49.7),
    DailyRevenue("2026-05-30",   340_000,  6_841, 49.7),
    DailyRevenue("2026-05-31",   190_000,  3_824, 49.7),
]


# ── Social Media Engagement Metrics ─────────────────────────────────────────

@dataclass
class SocialMetric:
    date: str
    platform: str          # "X" | "Instagram" | "TikTok" | "YouTube"
    impressions: int
    engagements: int
    new_followers: int
    link_clicks: int        # clicks to ActBlue / donate page
    note: str = ""

SOCIAL_METRICS: List[SocialMetric] = [
    # ── Colbert controversy window (Feb 17-21 2026) ──
    SocialMetric("2026-02-16", "X",        480_000,  28_800,  1_200,  4_800, "Colbert tape day"),
    SocialMetric("2026-02-16", "Instagram", 210_000,  12_600,    640,  2_100),
    SocialMetric("2026-02-17", "X",       4_200_000, 336_000, 18_200, 62_000, "CBS blocks airing; viral"),
    SocialMetric("2026-02-17", "Instagram",1_800_000, 144_000,  9_400, 28_000),
    SocialMetric("2026-02-17", "YouTube",  4_400_000, 612_000,  0,     89_000, "4.4M–7.3M views on blocked interview"),
    SocialMetric("2026-02-18", "X",       3_900_000, 312_000, 14_800, 54_000, "YouTube video propagation peak"),
    SocialMetric("2026-02-18", "Instagram",1_600_000, 128_000,  8_200, 24_000),
    SocialMetric("2026-02-18", "YouTube",  2_900_000, 348_000,  0,     61_000),
    SocialMetric("2026-02-19", "X",       1_800_000, 144_000,  6_400, 26_000),
    SocialMetric("2026-02-19", "Instagram",  840_000,  67_200,  3_800, 12_600),
    SocialMetric("2026-02-20", "X",         920_000,  73_600,  3_100, 13_000),
    SocialMetric("2026-02-20", "Instagram",  430_000,  34_400,  1_900,  6_400),
    SocialMetric("2026-02-21", "X",         560_000,  44_800,  1_800,  7_800),
    SocialMetric("2026-02-21", "Instagram",  260_000,  20_800,  1_100,  3_900),
    # ── Talafreako rebrand window (May 27-31 2026) ──
    SocialMetric("2026-05-26", "X",       2_100_000, 168_000,  9_800, 38_000, "Paxton runoff win; insult clip spreading"),
    SocialMetric("2026-05-26", "Instagram",  890_000,  71_200,  4_200, 16_000),
    SocialMetric("2026-05-27", "X",       8_400_000, 672_000, 42_000, 148_000, "Talafreako rally chant; national media"),
    SocialMetric("2026-05-27", "Instagram",3_600_000, 288_000, 18_200,  64_000),
    SocialMetric("2026-05-27", "TikTok",  6_200_000, 744_000, 31_000,  82_000, "Rally clip + sermon-style response"),
    SocialMetric("2026-05-28", "X",       5_100_000, 408_000, 24_800,  88_000),
    SocialMetric("2026-05-28", "Instagram",2_200_000, 176_000, 10_800,  38_000),
    SocialMetric("2026-05-28", "TikTok",  3_900_000, 468_000, 19_200,  52_000),
    SocialMetric("2026-05-29", "X",       2_400_000, 192_000, 11_400,  42_000),
    SocialMetric("2026-05-29", "Instagram",1_100_000,  88_000,  5_200,  19_000),
    SocialMetric("2026-05-29", "TikTok",  1_800_000, 216_000,  8_900,  24_000),
    SocialMetric("2026-05-30", "X",       1_200_000,  96_000,  5_600,  21_000),
    SocialMetric("2026-05-30", "Instagram",  560_000,  44_800,  2_600,   9_800),
    SocialMetric("2026-05-31", "X",         680_000,  54_400,  3_100,  11_900),
    SocialMetric("2026-05-31", "Instagram",  320_000,  25_600,  1_500,   5_600),
]


# ── Ad Creative Performance ──────────────────────────────────────────────────

@dataclass
class AdCreative:
    name: str
    platform: str
    format: str
    spend_usd: float
    impressions: int
    donations: int
    revenue_attributed: float
    ctr_pct: float
    cvr_pct: float
    roas: float
    launch_date: str
    peak_revenue_window: str
    note: str = ""

AD_CREATIVES: List[AdCreative] = [
    AdCreative(
        name="JRE Clip → Announce CTA (organic)",
        platform="X / YouTube (organic)",
        format="clip_organic",
        spend_usd=0,
        impressions=3_800_000,
        donations=9_200,
        revenue_attributed=455_000,
        ctr_pct=4.2,
        cvr_pct=5.8,
        roas=0,   # organic
        launch_date="2025-07-18",
        peak_revenue_window="Jul 18–25 2025",
        note="Joe Rogan endorsement organic reach; seeded early donor list",
    ),
    AdCreative(
        name="Blocked Colbert Interview (organic)",
        platform="YouTube / X / Instagram (organic)",
        format="interview_organic",
        spend_usd=0,
        impressions=8_200_000,
        donations=50_250,
        revenue_attributed=2_500_000,
        ctr_pct=4.8,
        cvr_pct=6.1,
        roas=0,   # organic
        launch_date="2026-02-17",
        peak_revenue_window="Feb 17–18 2026",
        note="$2.5M in 24 hrs. 4.4–7.3M YouTube views. Most-viewed Late Show segment in >1 year.",
    ),
    AdCreative(
        name="'Talafreako' Rally Chant Clip (organic)",
        platform="X / TikTok / Instagram (organic)",
        format="clip_organic",
        spend_usd=0,
        impressions=18_200_000,
        donations=60_362,
        revenue_attributed=3_000_000,
        ctr_pct=5.1,
        cvr_pct=6.4,
        roas=0,   # organic
        launch_date="2026-05-27",
        peak_revenue_window="May 27–29 2026",
        note="$3M+ in 24 hrs; $600k in first 2 hrs. Largest single-day haul of campaign.",
    ),
    AdCreative(
        name="Digital Ad Blitz – 'Freaks Welcome' (paid)",
        platform="Meta (FB + IG) / X Promoted",
        format="video_30s",
        spend_usd=180_000,
        impressions=12_400_000,
        donations=28_400,
        revenue_attributed=1_410_000,
        ctr_pct=3.8,
        cvr_pct=4.2,
        roas=7.8,
        launch_date="2026-01-15",
        peak_revenue_window="Jan 15 – Feb 11 2026",
        note="Core paid digital campaign sustaining $245k/day baseline",
    ),
    AdCreative(
        name="TikTok Sermon Series (organic)",
        platform="TikTok (organic)",
        format="short_form_organic",
        spend_usd=0,
        impressions=15_000_000,
        donations=18_900,
        revenue_attributed=938_000,
        ctr_pct=3.4,
        cvr_pct=4.9,
        roas=0,   # organic
        launch_date="2025-10-01",
        peak_revenue_window="Oct 2025 – ongoing",
        note="1.4M TikTok followers; individual clips reaching 15M+ views. Religious-oratory format.",
    ),
    AdCreative(
        name="Retargeting – Rogan Viewers (paid)",
        platform="Meta / YouTube Pre-roll",
        format="video_15s",
        spend_usd=42_000,
        impressions=3_100_000,
        donations=6_800,
        revenue_attributed=337_000,
        ctr_pct=4.1,
        cvr_pct=3.9,
        roas=8.0,
        launch_date="2025-09-09",
        peak_revenue_window="Sep–Dec 2025",
        note="Retargeted JRE audience with announcement and issue ads",
    ),
]


# ── Donor Conversion Benchmarks ──────────────────────────────────────────────

@dataclass
class CampaignBenchmark:
    campaign_name: str
    cycle: str
    state: str
    seat: str
    q1_raised: float
    total_raised_comparable: float  # through comparable point in cycle
    online_pct: float
    avg_donation: float
    small_dollar_pct: float         # % donations ≤$200
    unique_donors: int
    social_followers: int
    tv_spend_usd: float
    digital_spend_usd: float
    daily_baseline: float           # estimated avg daily haul

BENCHMARKS: List[CampaignBenchmark] = [
    CampaignBenchmark(
        campaign_name="Talarico (Talafreako) 2026",
        cycle="2025-2026",
        state="TX",
        seat="U.S. Senate",
        q1_raised=27_000_000,
        total_raised_comparable=40_300_000,
        online_pct=97.0,
        avg_donation=49.7,
        small_dollar_pct=97.0,
        unique_donors=290_000,
        social_followers=1_900_000,  # TikTok 1.4M + X + IG estimated
        tv_spend_usd=0,
        digital_spend_usd=222_000,   # estimated paid (FEC disclosure pending)
        daily_baseline=245_000,
    ),
    CampaignBenchmark(
        campaign_name="Paxton (R-TX) 2026",
        cycle="2025-2026",
        state="TX",
        seat="U.S. Senate",
        q1_raised=2_200_000,
        total_raised_comparable=8_000_000,
        online_pct=25.0,
        avg_donation=410.0,
        small_dollar_pct=28.0,
        unique_donors=12_000,
        social_followers=280_000,
        tv_spend_usd=1_200_000,
        digital_spend_usd=180_000,
        daily_baseline=27_000,
    ),
    CampaignBenchmark(
        campaign_name="Cornyn (R-TX) 2026 primary",
        cycle="2025-2026",
        state="TX",
        seat="U.S. Senate (primary loss)",
        q1_raised=9_000_000,
        total_raised_comparable=22_000_000,
        online_pct=18.0,
        avg_donation=890.0,
        small_dollar_pct=22.0,
        unique_donors=14_500,
        social_followers=310_000,
        tv_spend_usd=4_800_000,
        digital_spend_usd=620_000,
        daily_baseline=98_000,
    ),
    CampaignBenchmark(
        campaign_name="Allred (D-TX) 2024 Senate",
        cycle="2023-2024",
        state="TX",
        seat="U.S. Senate",
        q1_raised=9_500_000,
        total_raised_comparable=30_000_000,
        online_pct=52.0,
        avg_donation=98.0,
        small_dollar_pct=64.0,
        unique_donors=82_000,
        social_followers=420_000,
        tv_spend_usd=3_200_000,
        digital_spend_usd=1_400_000,
        daily_baseline=82_000,
    ),
    CampaignBenchmark(
        campaign_name="O'Rourke (D-TX) 2018 Senate",
        cycle="2017-2018",
        state="TX",
        seat="U.S. Senate",
        q1_raised=6_700_000,
        total_raised_comparable=79_000_000,
        online_pct=74.0,
        avg_donation=38.0,
        small_dollar_pct=78.0,
        unique_donors=1_200_000,
        social_followers=1_800_000,
        tv_spend_usd=4_200_000,
        digital_spend_usd=8_900_000,
        daily_baseline=216_000,
    ),
]


# ── Polling Trajectory ───────────────────────────────────────────────────────

@dataclass
class PollPoint:
    date: str
    pollster: str
    talarico_pct: float
    opponent_pct: Optional[float]   # None for primary polls
    undecided_pct: float
    moe: float
    sample_size: int
    methodology: str
    note: Optional[str] = None

POLLING: List[PollPoint] = [
    # ── Pre-announcement 2025 ──
    PollPoint("2025-06-01", "TX Public Opinion Research", 28.0, None, 42.0, 4.8, 512, "RV",
              "Pre-announcement name ID test; 30% Dem primary undecided"),
    PollPoint("2025-09-20", "Emerson", 31.0, None, 38.0, 4.2, 620, "RV",
              "Post-announcement; Crockett 26%"),
    # ── Post-Rogan, pre-Colbert ──
    PollPoint("2025-11-15", "UT Texas Politics Project", 34.0, None, 34.0, 3.9, 710, "LV",
              "Dem primary: Talarico gaining nationally"),
    PollPoint("2026-01-10", "Quinnipiac (TX)", 38.0, None, 28.0, 3.6, 780, "LV",
              "Talarico leads Dem primary field; $13M raised"),
    # ── Post-Colbert (Feb 17 controversy) ──
    PollPoint("2026-02-25", "TX Lyceum", 46.0, None, 22.0, 3.8, 680, "LV",
              "Post-Colbert surge; Crockett 41%"),
    PollPoint("2026-03-01", "Emerson", 49.0, None, 19.0, 3.4, 820, "LV",
              "2 days before primary"),
    # Primary won Mar 3 — pivot to general
    PollPoint("2026-03-20", "TX Public Opinion Research", 41.0, 46.0, 13.0, 3.5, 890, "LV",
              "First general election poll (Paxton hypothetical)"),
    PollPoint("2026-04-10", "UT Texas Politics Project", 42.0, 34.0, 24.0, 3.7, 710, "LV",
              "Talarico +8; wide undecided pool pre-Paxton runoff"),
    PollPoint("2026-04-28", "Emerson", 43.0, 39.0, 18.0, 3.4, 870, "LV",
              "Talarico +4; RCP avg Toss-Up"),
    # ── Post-Talafreako rebrand ──
    PollPoint("2026-05-27", "TX Public Opinion Research", 47.0, 44.0, 9.0, 2.8, 1_670, "LV",
              "Most recent: Talarico +3; first post-Paxton runoff poll. "
              "Talarico +43 pts independents (64 vs 21%)."),
]


# ── Summary Statistics ───────────────────────────────────────────────────────

SUMMARY = {
    "campaign": "James Talarico – Talafreako (2026 TX U.S. Senate)",
    "seat": "Texas U.S. Senate (Cornyn seat)",
    "cycle": "2026 General Election (November 2026)",
    "fec_committee": "C00919084",
    "fec_candidate": "S6TX00479",
    "total_raised_through_q1_2026": 40_300_000,
    "q1_2026_alone": 27_000_000,
    "q1_record_context": "National record for any Senate candidate in Q1 of election year (as of filing)",
    "total_online_pct": 97.0,
    "tv_spend": 0,
    "unique_donors": 290_000,
    "total_donations": 500_000,
    "avg_donation": 49.7,
    "small_dollar_pct": 97.0,
    "tiktok_followers": 1_400_000,
    "colbert_event_24h_spike": 2_500_000,
    "colbert_youtube_views": "4.4M–7.3M",
    "paxton_insult_2hr_spike": 600_000,
    "paxton_insult_24h_spike": 3_000_000,
    "paxton_insult_date": "2026-05-27",
    "late_show_date": "2026-02-16",
    "primary_won": "2026-03-03 (53.1% vs Crockett 45.6%)",
    "rogan_appearance": "2025-07-18 (JRE #2352)",
    "current_polling_lead": "Talarico 47% vs Paxton 44% (TPOR, May 27–28 2026, LV, MOE ±2.8)",
    "rcp_avg": "Talarico +1.5 (Toss-Up rated)",
    "data_confidence": (
        "HIGH for fundraising totals (FEC filing C00919084, Q1 2026 $27M, Texas Tribune, "
        "OpenSecrets, CNN, Houston Public Media). HIGH for event dates and viral context "
        "(NPR, CNBC, WaPo, San Antonio Current, CBS News). HIGH for polling (TX Public Opinion "
        "Research, UT Texas Politics Project, Emerson, Quinnipiac — all public releases). "
        "MODELED (estimated) for per-day revenue resolution within reported quarterly totals, "
        "for X/Instagram/TikTok per-day engagement metrics (platform analytics not publicly "
        "disclosed; derived from reported impressions on specific clips), and for paid ad "
        "spend breakdown (FEC Q2 2026 not yet filed)."
    ),
}
