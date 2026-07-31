# Amsterdam Airbnb: Price, Regulation & the Tourist City

**A Data Visualization Analysis of Amsterdam's Short-Term Rental Market**

*Final Individual Project — Data Visualization, Summer 2026*

[![Made with Plotly](https://img.shields.io/badge/Made%20with-Plotly-3f4f75?logo=plotly)](https://plotly.com/)
[![Dashboard: Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Data: Inside Airbnb](https://img.shields.io/badge/Data-Inside%20Airbnb-blue)](https://insideairbnb.com/)
[![License: CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-lightgrey)](http://creativecommons.org/licenses/by/4.0/)

🔗 **[Live Dashboard](https://dvproject-ir3q4xqpiwgkhv6bhbuwqs.streamlit.app/)** · 📦 **[Source Repo](https://github.com/Prajwala15/DV_Project)**

---

## Abstract

Amsterdam occupies a distinctive position among global tourist destinations: a city
actively legislating against the pressures of its own popularity. Since 2019, the
municipality has capped short-term rentals at 30 nights per year per listing, an
attempt to preserve housing stock against tourism-driven displacement.

Using the [Inside Airbnb](https://insideairbnb.com/) dataset, this project tests
twelve analytical questions against that premise — and finds that several widely
held assumptions about the market are backwards. Professional multi-listing hosts
charge **27% less**, not more. Superhosts charge **23% less** than regular hosts.
The city-centre price premium, real by mean, **disappears entirely under the
median**. And a tenth of listings stay open well past the regulatory cap.

---

## Table of Contents

- [Key Findings](#key-findings)
- [Research Questions](#research-questions)
- [Repository Structure](#repository-structure)
- [Data](#data)
- [Methodology](#methodology)
- [Deliverables](#deliverables)
- [Running This Project Locally](#running-this-project-locally)
- [Technology Stack](#technology-stack)
- [Design Principles Applied](#design-principles-applied)
- [Limitations](#limitations)
- [License & Attribution](#license--attribution)
- [Author](#author)

---

## Key Findings

Four claims that contradict common assumptions about the market:

| Finding | What the data shows |
|---|---|
| **Professional hosts charge less, not more** | Multi-listing hosts average €272/night vs. €371 for single-listing hosts — a 27% discount, likely driven by smaller, standardised inventory rather than pricing strategy. |
| **Superhosts charge less, not more** | €285 vs. €371 for regular hosts — a 23% discount. The badge rewards consistent delivery (response rate, cancellations, ratings), not positioning. |
| **The centre price premium is a statistical artefact** | By mean, price falls cleanly from €409 (within 1 km of Dam Square) to €252 (5 km+). By **median**, the inner four km are flat at €284–308 — the mean gradient is produced by a handful of listings up to €11,412/night. |
| **The 30-night cap has soft edges** | 23% of listings sit at 1–29 bookable days/year, consistent with hosts self-limiting under the cap. But 10% stay open 335+ days — either exempt licensed B&Bs, or the cap not reaching them. |

Additional patterns: shared-room listings have nearly vanished (21 of 6,377 listings,
0.33%); citywide demand has recovered to **1.9× its 2019 level** despite a 64% COVID-era
collapse; and minimum-stay rules are a near-universal 2-night platform default rather
than a local policy lever (20 of 22 neighbourhoods).

---

## Research Questions

Twelve multi-dimensional analytical questions, each selected to relate variables,
compare groups, or track change over time or space:

| # | Question | Visualization |
|---|---|---|
| 1 | Which neighbourhoods command the biggest price premium? | Horizontal bar |
| 2 | Does hosting activity cluster around the 30-night regulatory cap? | Annotated histogram |
| 3 | How does the room-type mix vary by neighbourhood? | Stacked horizontal bar |
| 4 | Do professional (multi-listing) hosts price differently? | Grouped bar |
| 5 | How has booking demand moved over time? | Time series |
| 6 | What does the tourist season actually look like? | Monthly bar |
| 7 | Do minimum-stay rules differ across the city? | Horizontal bar |
| 8 | Do cheaper listings score worse on reviews? | Bar (zero baseline) |
| 9 | Where in the city are prices highest — mean vs. median? | Line comparison |
| 10 | Where in the city are prices highest — spatial view? | Scatter map |
| 11 | Does Superhost status carry a price premium? | Grouped bar |
| 12 | Where does the shared-room type still exist? | Horizontal bar |

---

## Repository Structure

```
DV_Project/
├── README.md
├── app.py                                 # Streamlit dashboard (single-file version)
├── requirements.txt
├── notebooks/
│   ├── 01_Data_Preparation.ipynb
│   ├── 01_Data_Preparation.html
│   ├── 02_Analytical_Questions.ipynb
│   └── 02_Analytical_Questions.html
├── data/
│   └── (downloaded at runtime — not committed, see app.py)
└── presentation/
    └── Amsterdam_Airbnb_Presentation_FINAL.pptx
```

---

## Data

| | |
|---|---|
| **Source** | [Inside Airbnb — Amsterdam](https://insideairbnb.com/amsterdam/) |
| **Snapshot date** | 15 June 2026 |
| **License** | [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) |
| **Files** | `listings.csv` (10,369 rows × 90 columns), `reviews.csv` (545,162 rows), `neighbourhoods.geojson` (22 boundaries) |
| **After cleaning** | 6,377 listings (rows dropped for missing price/neighbourhood — inactive or delisted entries) |

Raw data files are **not committed to this repository**. The app downloads directly
from Inside Airbnb's servers at runtime (see `load_data()` in `app.py`).

> Provided by Inside Airbnb for non-commercial, educational, and research use.
> Submitted as academic coursework; not used for any commercial purpose.

---

## Methodology

1. **Acquisition** — pulled programmatically from Inside Airbnb's public archive.
2. **Cleaning** — price parsed from currency string to float; listings at €0 dropped;
   `host_is_superhost` recoded from `'t'`/`'f'` to boolean; stray whitespace/quote
   characters stripped from categorical fields.
3. **Exploratory analysis** — single-variable summaries used only to orient the
   analysis, excluded from the twelve graded questions.
4. **Analytical questions** — each answered with one Plotly visualization, a zero
   baseline on every bar chart, an insight-driven title, and a written takeaway.
5. **Dashboard** — a curated, filterable subset of the twelve visuals rebuilt as an
   interactive Streamlit application.

**A note on means vs. medians:** the underlying price distribution is heavily
right-skewed (median €291, 95th percentile €728, max €11,412). Several charts report
means to match a commonly-expected reading, but Question 9 exists specifically to
show what that choice costs — the median tells a materially different story.

---

## Deliverables

| Deliverable | Link |
|---|---|
| Data Preparation notebook | [`notebooks/01_Data_Preparation.ipynb`](notebooks/01_Data_Preparation.ipynb) |
| Analytical Questions notebook | [`notebooks/02_Analytical_Questions.ipynb`](notebooks/02_Analytical_Questions.ipynb) |
| Dashboard source | [`app.py`](app.py) |
| **Live dashboard** | 🔗 [dvproject-ir3q4xqpiwgkhv6bhbuwqs.streamlit.app](https://dvproject-ir3q4xqpiwgkhv6bhbuwqs.streamlit.app/) |
| Presentation deck | [`presentation/Amsterdam_Airbnb_Presentation_FINAL.pptx`](presentation/Amsterdam_Airbnb_Presentation_FINAL.pptx) |

---

## Running This Project Locally

```bash
git clone https://github.com/Prajwala15/DV_Project
cd DV_Project
pip install -r requirements.txt
streamlit run app.py
```
The app will be available at `http://localhost:8501`.

---

## Technology Stack

- **Python** — pandas, numpy
- **Plotly** — all visualizations (course requirement; no Matplotlib/Seaborn)
- **Streamlit** — interactive dashboard, deployed on Streamlit Community Cloud
- **Jupyter** — analysis notebooks

---

## Design Principles Applied

- Zero baseline on every bar chart
- Insight-driven titles that state a finding, not just the variables plotted
- CVD-safe (Okabe–Ito) palette — muted grey for context, one highlight colour for focus
- Decluttered layouts — gridlines removed, chart-junk minimized
- Consistent visual language across the notebooks, dashboard, and presentation

---

## Limitations

- **Listed price is not paid price** — Inside Airbnb records the advertised nightly
  rate on the scrape date, excluding fees, discounts, and seasonal adjustments.
- **Availability is not occupancy** — `availability_365` counts bookable days, not
  nights sold; Question 2 evidences stated intent around the cap, not verified
  compliance.
- **Reviews under-count stays** — only a fraction of guests review, and the rate
  varies by listing type and over time; review volume is used as a demand proxy,
  reliable for shape but not for level.
- **Comparisons are uncontrolled** — the host-type and Superhost price comparisons
  (Q4, Q11) don't adjust for room type, capacity, or location; the differences are
  large and consistent, but not causal claims.
- **Single snapshot** — one scrape (15 June 2026); listings inactive that day are
  absent, accounting for most of the drop during cleaning.

---

## Future Improvements

- Stack multiple Inside Airbnb quarterly snapshots to turn cross-sectional findings
  into trends — most valuably, whether the share of hosts capping their calendars
  is rising as enforcement tightens.
- Replace the scatter map with a proper choropleth using `neighbourhoods.geojson`.
- Cross-reference with Amsterdam's official short-term rental licensing register.

---

## License & Attribution

This project's code is shared for academic purposes. The underlying data is
© Inside Airbnb, licensed under [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) —
attribution to Inside Airbnb is required for any reuse of the dataset itself.

---

## Author

**Prajwala Kasaram**
Data Visualization · Summer 2026
