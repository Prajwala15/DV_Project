"""
Amsterdam Airbnb — Price, Regulation & the Tourist City
=======================================================
Run locally:  streamlit run app.py
Deploy:       push to a public GitHub repo, then deploy on share.streamlit.io

Data: Inside Airbnb, Amsterdam snapshot 15 June 2026 (CC BY 4.0).
Files are downloaded on first run and cached; see load_data() below.
"""
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="Amsterdam Airbnb", page_icon="🏠",
                   layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------------------------------ palette
CVD = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73",
       "red": "#D55E00", "purple": "#CC79A7", "sky": "#56B4E9"}
GREY = "#BFBFBF"
GREY_DARK = "#4D4D4D"
HL = CVD["orange"]
ROOM_COLORS = {"Entire home/apt": CVD["blue"], "Private room": CVD["orange"],
               "Hotel room": CVD["green"], "Shared room": CVD["purple"]}

BASE = ("https://data.insideairbnb.com/the-netherlands/north-holland/"
        "amsterdam/2026-06-15")
SNAPSHOT = "15 June 2026"

# ------------------------------------------------------------------ styling
st.markdown("""
<style>
  .block-container {padding-top: 2.2rem; max-width: 1400px;}
  h1, h2, h3 {font-family: Inter, Helvetica Neue, Arial, sans-serif; letter-spacing: -.01em;}
  h1 {font-size: 2.05rem !important; margin-bottom: .1rem;}
  .lede {color:#4D4D4D; font-size:1.02rem; margin:.1rem 0 1.3rem 0; max-width:62rem;}
  .finding {border-left:3px solid #E69F00; padding:.55rem 0 .55rem .9rem;
            color:#333; font-size:.95rem; margin:.4rem 0 1.1rem 0; background:#FDFAF5;}
  [data-testid="stMetricValue"] {font-size:1.55rem;}
  [data-testid="stMetricLabel"] {color:#6B6B6B;}
  footer, #MainMenu {visibility:hidden;}
</style>
""", unsafe_allow_html=True)


def finding(text):
    st.markdown(f"<div class='finding'>{text}</div>", unsafe_allow_html=True)


def style(fig, title, subtitle=None, height=460, grid="none"):
    head = f"<b>{title}</b>"
    if subtitle:
        head += f"<br><span style='font-size:12px;color:{GREY_DARK}'>{subtitle}</span>"
    fig.update_layout(
        title=dict(text=head, x=0, xanchor="left", font=dict(size=17, color="#1a1a1a")),
        font=dict(family="Inter, Helvetica Neue, Arial, sans-serif", size=12.5,
                  color=GREY_DARK),
        plot_bgcolor="white", paper_bgcolor="white", height=height,
        margin=dict(l=60, r=30, t=80 if subtitle else 62, b=50),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0))
    fig.update_xaxes(showgrid=False, zeroline=False, showline=True, linecolor="#D9D9D9")
    fig.update_yaxes(showgrid=False, zeroline=False, showline=True, linecolor="#D9D9D9")
    if grid in ("y", "both"):
        fig.update_yaxes(showgrid=True, gridcolor="#F0F0F0")
    if grid in ("x", "both"):
        fig.update_xaxes(showgrid=True, gridcolor="#F0F0F0")
    return fig


# ------------------------------------------------------------------ data
@st.cache_data(show_spinner="Loading the Amsterdam listing data…")
def load_data():
    """Download, clean and derive everything once. Returns immutable inputs only."""
    os.makedirs("data", exist_ok=True)
    targets = {"listings.csv.gz": f"{BASE}/data/listings.csv.gz",
               "reviews.csv.gz": f"{BASE}/data/reviews.csv.gz"}
    for fname, url in targets.items():
        path = f"data/{fname}"
        if not os.path.exists(path):
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            with open(path, "wb") as fh:
                fh.write(r.content)

    keep = ["id", "neighbourhood_cleansed", "latitude", "longitude", "room_type",
            "price", "minimum_nights", "number_of_reviews", "review_scores_rating",
            "availability_365", "host_id", "calculated_host_listings_count",
            "host_is_superhost"]
    listings = pd.read_csv("data/listings.csv.gz", low_memory=False)
    raw_rows = len(listings)

    listings["price"] = (listings["price"].astype(str)
                         .str.replace(r"[\$,]", "", regex=True)
                         .pipe(pd.to_numeric, errors="coerce"))
    listings["host_is_superhost"] = listings["host_is_superhost"].map({"t": True, "f": False})
    for col in ("room_type", "neighbourhood_cleansed"):
        listings[col] = listings[col].astype(str).str.strip().str.strip("'\"")

    listings = listings[[c for c in keep if c in listings.columns]]
    listings = listings.dropna(subset=["price", "neighbourhood_cleansed"])
    listings = listings[listings["price"] > 0].copy()

    # derived columns computed here, never mutated downstream
    listings["host_type"] = np.where(listings["calculated_host_listings_count"] > 1,
                                     "Multi-listing host", "Single-listing host")
    listings["host_badge"] = listings["host_is_superhost"].map(
        {True: "Superhost", False: "Regular host"}).fillna("Unknown")
    listings["price_band"] = pd.cut(
        listings["price"], [0, 100, 150, 200, 300, np.inf],
        labels=["<100", "100–150", "150–200", "200–300", "300+"])

    DAM = (52.3731, 4.8926)
    rl, ro = np.radians(listings.latitude), np.radians(listings.longitude)
    d0, d1 = np.radians(DAM[0]), np.radians(DAM[1])
    listings["km_from_centre"] = 2 * 6371 * np.arcsin(np.sqrt(
        np.sin((rl - d0) / 2) ** 2 + np.cos(rl) * np.cos(d0) * np.sin((ro - d1) / 2) ** 2))
    listings["ring"] = pd.cut(listings.km_from_centre, [0, 1, 2, 3, 5, 50],
                              labels=["<1 km", "1–2 km", "2–3 km", "3–5 km", "5 km +"])

    # reviews reduced to a monthly series immediately — the raw file is 545k rows
    reviews = pd.read_csv("data/reviews.csv.gz", usecols=["date"])
    reviews["date"] = pd.to_datetime(reviews["date"], errors="coerce")
    monthly = (reviews.dropna(subset=["date"]).set_index("date")
               .resample("ME").size().rename("reviews").reset_index())
    monthly = monthly.iloc[:-1]          # drop the partial final month

    return listings, monthly, raw_rows


listings, monthly, raw_rows = load_data()
HOODS = sorted(listings.neighbourhood_cleansed.unique())
ROOMS = sorted(listings.room_type.unique())
BANDS = list(listings.price_band.cat.categories)

# ------------------------------------------------------------------ state
DEFAULTS = {"f_hoods": HOODS, "f_rooms": ROOMS, "f_bands": BANDS}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


def reset_filters():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v


# ------------------------------------------------------------------ header
st.title("Amsterdam Airbnb")
st.markdown(
    "<div class='lede'>Amsterdam caps most short-term rentals at 30 nights a year to "
    "protect housing from tourism pressure. This dashboard tests what the listing data "
    "actually shows about price, hosts and that regulation — and several widely held "
    "assumptions turn out to be backwards.</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.header("Filters")
    st.caption("These apply to every tab.")
    st.multiselect("Neighbourhood", HOODS, key="f_hoods")
    st.multiselect("Room type", ROOMS, key="f_rooms")
    st.multiselect("Price band (EUR)", BANDS, key="f_bands")
    st.button("Reset filters", on_click=reset_filters, width="stretch")

    st.divider()
    with st.expander("About this data"):
        st.markdown(
            f"**Source** — Inside Airbnb, Amsterdam snapshot **{SNAPSHOT}** (CC BY 4.0).\n\n"
            f"**Cleaning** — {raw_rows:,} raw listings reduce to {len(listings):,} after "
            "dropping rows with no price or no neighbourhood. Those are inactive or "
            "delisted entries that carry no rate.\n\n"
            "**Price** — the advertised nightly rate, excluding cleaning and service "
            "fees. It is a list price, not revenue.")
    with st.expander("How to read this"):
        st.markdown(
            "**Availability is not occupancy.** `availability_365` counts bookable "
            "days, not nights sold, so it evidences intent around the cap rather than "
            "compliance with it.\n\n"
            "**Reviews are a proxy.** Only some guests review, so the seasonal curve is "
            "reliable for shape, not for level.\n\n"
            "**Medians are shown alongside means** wherever the two disagree — on this "
            "data they often do.")

f = listings[
    listings.neighbourhood_cleansed.isin(st.session_state.f_hoods)
    & listings.room_type.isin(st.session_state.f_rooms)
    & listings.price_band.isin(st.session_state.f_bands)]

if f.empty:
    st.warning("No listings match those filters — widen the selection in the sidebar.")
    st.stop()

# ------------------------------------------------------------------ metrics
c = st.columns(5)
c[0].metric("Listings", f"{len(f):,}",
            f"{len(f) / len(listings) - 1:+.0%} vs all" if len(f) != len(listings) else None)
c[1].metric("Median price", f"€{f.price.median():,.0f}")
c[2].metric("Mean price", f"€{f.price.mean():,.0f}")
c[3].metric("Neighbourhoods", f"{f.neighbourhood_cleansed.nunique()}")
c[4].metric("Superhost share", f"{f.host_is_superhost.mean():.0%}")

tabs = st.tabs(["📍  Where & how much", "🏠  Hosts & regulation",
                "📅  Seasonality", "⭐  Quality"])

# ================================================================== TAB 1
with tabs[0]:
    left, right = st.columns([1, 1])

    with left:
        stat = st.radio("Average by", ["Median", "Mean"], horizontal=True, key="hoodstat")
        agg = (f.groupby("neighbourhood_cleansed").price
               .agg("median" if stat == "Median" else "mean")
               .sort_values().reset_index())
        top = agg.iloc[-1].neighbourhood_cleansed if len(agg) else None
        fig = go.Figure(go.Bar(
            x=agg.price, y=agg.neighbourhood_cleansed, orientation="h",
            marker_color=[HL if n == top else GREY for n in agg.neighbourhood_cleansed],
            text=[f"€{v:,.0f}" for v in agg.price], textposition="outside",
            hovertemplate="%{y}<br>€%{x:,.0f}<extra></extra>"))
        fig.update_xaxes(title=f"{stat} price per night (EUR)",
                         range=[0, agg.price.max() * 1.22 if len(agg) else 1])
        fig.update_yaxes(title=None)
        style(fig, f"{stat} nightly price by neighbourhood",
              "Switch the toggle — the ranking changes with the statistic", height=600)
        st.plotly_chart(fig, width="stretch")

    with right:
        q95 = f.price.quantile(.95)
        fig = px.scatter_map(
            f, lat="latitude", lon="longitude",
            color=f.price.clip(upper=q95), color_continuous_scale="YlOrRd",
            zoom=10.6, map_style="carto-positron",
            hover_data={"price": ":,.0f", "room_type": True,
                        "neighbourhood_cleansed": True},
            labels={"color": "EUR/night"})
        fig.update_layout(height=600, margin=dict(l=0, r=0, t=62, b=0),
                          title=dict(text="<b>Every listing, coloured by price</b>",
                                     x=0, font=dict(size=17)),
                          coloraxis_colorbar=dict(title="EUR/night<br>(capped p95)",
                                                  thickness=11, len=.55))
        st.plotly_chart(fig, width="stretch")

    st.divider()
    st.subheader("Does the centre really command a premium?")
    ring = f.groupby("ring", observed=True).price.agg(["mean", "median", "size"]).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ring.ring.astype(str), y=ring["mean"], mode="lines+markers",
                             name="Mean", line=dict(color=GREY, width=2.5),
                             marker=dict(size=9, color=GREY),
                             hovertemplate="%{x}<br>mean €%{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=ring.ring.astype(str), y=ring["median"], mode="lines+markers",
                             name="Median", line=dict(color=HL, width=3),
                             marker=dict(size=10, color=HL),
                             hovertemplate="%{x}<br>median €%{y:,.0f}<extra></extra>"))
    fig.update_xaxes(title="Distance from Dam Square")
    fig.update_yaxes(title="Price per night (EUR)")
    fig.update_layout(legend=dict(orientation="h", y=1.02, x=0, yanchor="bottom"))
    style(fig, "The centre premium is an artefact of the mean",
          "By median, the inner rings are flat", height=440, grid="y")
    st.plotly_chart(fig, width="stretch")
    finding("Across the full dataset the mean falls from <b>€409</b> within 1 km of Dam "
            "Square to <b>€252</b> beyond 5 km — but the median is flat at €284–308 "
            "across the inner four rings. A handful of listings up to €11,412 a night "
            "produce the entire gradient.")

# ================================================================== TAB 2
with tabs[1]:
    left, right = st.columns(2)

    with left:
        hp = f.groupby("host_type").price.agg(["mean", "median", "size"]).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=hp.host_type, y=hp["mean"], name="Mean", marker_color=GREY,
                             text=[f"€{v:,.0f}" for v in hp["mean"]], textposition="outside"))
        fig.add_trace(go.Bar(x=hp.host_type, y=hp["median"], name="Median", marker_color=HL,
                             text=[f"€{v:,.0f}" for v in hp["median"]], textposition="outside"))
        fig.update_yaxes(title="Price per night (EUR)")
        fig.update_layout(barmode="group",
                          legend=dict(orientation="h", y=1.02, x=0, yanchor="bottom"))
        style(fig, "Professional hosts charge less, not more",
              "Multi-listing operators against single-listing households", height=440, grid="y")
        st.plotly_chart(fig, width="stretch")

    with right:
        bp = f.groupby("host_badge").price.agg(["mean", "median"]).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=bp.host_badge, y=bp["mean"], name="Mean", marker_color=GREY,
                             text=[f"€{v:,.0f}" for v in bp["mean"]], textposition="outside"))
        fig.add_trace(go.Bar(x=bp.host_badge, y=bp["median"], name="Median", marker_color=HL,
                             text=[f"€{v:,.0f}" for v in bp["median"]], textposition="outside"))
        fig.update_yaxes(title="Price per night (EUR)")
        fig.update_layout(barmode="group",
                          legend=dict(orientation="h", y=1.02, x=0, yanchor="bottom"))
        style(fig, "The Superhost badge carries a discount",
              "Badge holders compete on value rather than price", height=440, grid="y")
        st.plotly_chart(fig, width="stretch")

    finding("Multi-listing hosts average <b>€272</b> against <b>€371</b> for single-listing "
            "hosts, and Superhosts <b>€285</b> against <b>€371</b>. Neither comparison "
            "controls for property size, so read them as descriptive, not causal.")

    st.divider()
    st.subheader("Do hosts work around the 30-night cap?")
    under30 = (f.availability_365.between(1, 29)).mean()
    wide = (f.availability_365 >= 335).mean()
    fig = go.Figure(go.Histogram(x=f.availability_365, nbinsx=52, marker_color=GREY,
                                 hovertemplate="%{x} days<br>%{y} listings<extra></extra>"))
    fig.add_vrect(x0=0, x1=30, fillcolor=HL, opacity=.12, line_width=0)
    fig.update_xaxes(title="Days bookable per year", range=[0, 365])
    fig.update_yaxes(title="Listings")
    style(fig, "Most hosts close their calendar well below the cap",
          "Shaded band marks the 30-night limit", height=430, grid="y")
    st.plotly_chart(fig, width="stretch")
    finding(f"In this selection <b>{under30:.1%}</b> of listings offer 1–29 bookable days, "
            f"consistent with self-limiting under the cap, while <b>{wide:.1%}</b> stay open "
            "335+ days — licensed exemptions, or listings the rule is not reaching.")

    with st.expander("Room-type mix by neighbourhood"):
        mix = (f.groupby(["neighbourhood_cleansed", "room_type"], observed=True)
               .size().reset_index(name="n"))
        mix["share"] = mix.n / mix.groupby("neighbourhood_cleansed").n.transform("sum") * 100
        piv = mix.pivot_table(index="neighbourhood_cleansed", columns="room_type",
                              values="share").fillna(0)
        if "Entire home/apt" in piv:
            piv = piv.sort_values("Entire home/apt")
        fig = go.Figure()
        for rt in ["Entire home/apt", "Private room", "Hotel room", "Shared room"]:
            if rt in piv:
                fig.add_trace(go.Bar(y=piv.index, x=piv[rt], name=rt, orientation="h",
                                     marker_color=ROOM_COLORS[rt],
                                     hovertemplate="%{y}<br>" + rt + ": %{x:.1f}%<extra></extra>"))
        fig.update_layout(barmode="stack",
                          legend=dict(orientation="h", y=1.02, x=0, yanchor="bottom"))
        fig.update_xaxes(title="Share of listings (%)", range=[0, 100])
        fig.update_yaxes(title=None)
        style(fig, "Entire homes dominate the ring, not the centre", height=580)
        st.plotly_chart(fig, width="stretch")

# ================================================================== TAB 3
with tabs[2]:
    st.subheader("Demand over time")
    st.caption("Review volume is a proxy for completed stays. The series covers the whole "
               "city and does not respond to the listing filters.")

    yr = st.slider("Year range", int(monthly.date.dt.year.min()),
                   int(monthly.date.dt.year.max()),
                   (2015, int(monthly.date.dt.year.max())), key="yrs")
    m = monthly[monthly.date.dt.year.between(*yr)]

    fig = go.Figure(go.Scatter(x=m.date, y=m.reviews, mode="lines",
                               line=dict(color=CVD["blue"], width=2),
                               hovertemplate="%{x|%b %Y}<br>%{y:,} reviews<extra></extra>"))
    if yr[0] <= 2021:
        fig.add_vrect(x0="2020-03-01", x1="2021-06-30", fillcolor=GREY, opacity=.22,
                      line_width=0)
    fig.update_yaxes(title="Reviews per month", rangemode="tozero")
    fig.update_xaxes(title=None)
    style(fig, "Demand collapsed in 2020 and came back nearly twice as strong",
          "Shaded band marks the pandemic period", height=440, grid="y")
    st.plotly_chart(fig, width="stretch")

    left, right = st.columns([1.3, 1])
    with left:
        recent = monthly[monthly.date.dt.year.between(2022, 2025)]
        by_month = recent.groupby(recent.date.dt.month).reviews.mean()
        names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        fig = go.Figure(go.Bar(
            x=names, y=by_month.reindex(range(1, 13)).values,
            marker_color=[HL if i in (4, 5) else GREY for i in range(1, 13)],
            hovertemplate="%{x}<br>%{y:,.0f} reviews<extra></extra>"))
        fig.update_yaxes(title="Mean reviews per month, 2022–2025")
        style(fig, "A seven-month plateau, not a summer spike", height=420, grid="y")
        st.plotly_chart(fig, width="stretch")
    with right:
        yearly = monthly.groupby(monthly.date.dt.year).reviews.sum()
        tbl = yearly.loc[2018:].rename("Reviews").reset_index()
        tbl.columns = ["Year", "Reviews"]
        st.markdown("**Annual totals**")
        st.dataframe(tbl, hide_index=True, width="stretch", height=380)

    finding("2019 closed at 47,014 reviews and 2020 at 17,074 — a 64% collapse. By 2025 "
            "the figure was <b>89,421</b>, 1.9× the pre-pandemic level. The cap constrains "
            "individual listings without constraining aggregate demand.")

# ================================================================== TAB 4
with tabs[3]:
    st.subheader("Does price buy quality?")
    band = (f.dropna(subset=["review_scores_rating"])
            .groupby("price_band", observed=True).review_scores_rating
            .agg(["mean", "size"]).reset_index())
    band = band[band["size"] >= 5]

    if band.empty:
        st.info("Too few rated listings in this selection.")
    else:
        fig = go.Figure(go.Bar(
            x=band.price_band.astype(str), y=band["mean"],
            marker_color=[GREY] * (len(band) - 1) + [HL],
            text=[f"{v:.2f}" for v in band["mean"]], textposition="outside",
            customdata=band[["size"]],
            hovertemplate="%{x}<br>%{y:.3f} mean score<br>%{customdata[0]:,} listings<extra></extra>"))
        lo, hi = band["mean"].min(), band["mean"].max()
        fig.update_yaxes(title="Mean review score", range=[lo - .12, hi + .07])
        fig.update_xaxes(title="Price band (EUR per night)")
        style(fig, "Scores climb with price — the effect is real but small",
              "Note the truncated axis: the full scale runs 1–5", height=440, grid="y")
        st.plotly_chart(fig, width="stretch")

        spread = hi - lo
        finding(f"Across the full dataset the mean rating rises monotonically from 4.62 to "
                f"4.88. In this selection the whole range spans <b>{spread:.2f} points</b> "
                "on a five-point scale — price predicts quality, and barely matters.")

    with st.expander("Minimum-stay requirements by neighbourhood"):
        mn = (f.groupby("neighbourhood_cleansed").minimum_nights.median()
              .sort_values().reset_index())
        fig = go.Figure(go.Bar(x=mn.minimum_nights, y=mn.neighbourhood_cleansed,
                               orientation="h", marker_color=GREY,
                               text=[f"{v:.0f}" for v in mn.minimum_nights],
                               textposition="outside",
                               hovertemplate="%{y}<br>median %{x:.0f} nights<extra></extra>"))
        fig.update_xaxes(title="Median minimum nights",
                         range=[0, max(3.2, mn.minimum_nights.max() * 1.3)])
        fig.update_yaxes(title=None)
        style(fig, "Minimum-stay rules are effectively uniform citywide",
              "A platform default, not a local decision", height=560)
        st.plotly_chart(fig, width="stretch")

    with st.expander("Where do shared rooms still exist?"):
        shared = (listings[listings.room_type == "Shared room"]
                  .groupby("neighbourhood_cleansed").size()
                  .sort_values().reset_index(name="n"))
        if shared.empty:
            st.info("No shared-room listings.")
        else:
            fig = go.Figure(go.Bar(x=shared.n, y=shared.neighbourhood_cleansed,
                                   orientation="h", marker_color=HL,
                                   text=shared.n, textposition="outside",
                                   hovertemplate="%{y}<br>%{x} listings<extra></extra>"))
            fig.update_xaxes(title="Shared-room listings",
                             range=[0, shared.n.max() * 1.3])
            fig.update_yaxes(title=None)
            style(fig, f"Only {shared.n.sum()} shared rooms remain citywide",
                  "Unfiltered — the budget end of the market has effectively gone",
                  height=360)
            st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------------ footer
st.divider()
foot = st.columns([2, 1])
foot[0].caption(
    "Built with Plotly and Streamlit · Data: Inside Airbnb (CC BY 4.0), insideairbnb.com/amsterdam · "
    "Palette: Okabe–Ito, colour-vision-deficiency safe")
foot[1].caption(
    f"**Data vintage** · Inside Airbnb snapshot, {SNAPSHOT}  \n"
    f"**Loaded** · {len(listings):,} listings · {monthly.reviews.sum():,} reviews")
