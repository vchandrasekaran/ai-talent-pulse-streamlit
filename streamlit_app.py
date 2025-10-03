
import os
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

st.set_page_config(page_title="AI Talent Pulse", page_icon="🤖", layout="wide")

st.title("🤖 AI Talent Pulse — Interactive Demo")
st.caption("MVP: local CSV demo. Phase 2 will connect to Snowflake + dbt and add an AI chat copilot.")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    date_range = st.slider("Date Range (months back)", 1, 24, 6)
    region = st.selectbox("Region", ["ALL", "AMER", "EMEA", "APAC"])
    role_type = st.multiselect("Role Type", ["AI Engineer", "ML Engineer", "Data Scientist", "Prompt Engineer"], ["AI Engineer","ML Engineer"])

@st.cache_data
def load_demo():
    rng = pd.date_range(end=pd.Timestamp.today().normalize(), periods=24, freq="MS")
    regions = ["AMER","EMEA","APAC"]
    roles = ["AI Engineer","ML Engineer","Data Scientist","Prompt Engineer"]
    data = []
    for dt in rng:
        for r in regions:
            for role in roles:
                jobs = np.random.poisson(lam=200 if "Engineer" in role else 150)
                layoffs = np.random.poisson(lam=40)
                salary = np.random.normal(loc=145000, scale=15000)
                data.append([dt.date(), r, role, jobs, layoffs, salary])
    df = pd.DataFrame(data, columns=["month","region","role","jobs","layoffs","salary_mid"])
    return df

df = load_demo()

# Apply filters
cutoff = pd.Timestamp.today().normalize() - pd.DateOffset(months=date_range-1)
mask = (pd.to_datetime(df["month"]) >= cutoff)
if region != "ALL":
    mask &= (df["region"] == region)
if role_type:
    mask &= df["role"].isin(role_type)
f = df[mask].copy()

# KPIs
kpi_jobs = int(f["jobs"].sum())
kpi_layoffs = int(f["layoffs"].sum())
kpi_ratio = (kpi_jobs / max(kpi_layoffs,1))

c1,c2,c3 = st.columns(3)
c1.metric("AI Job Postings (filtered)", f"{kpi_jobs:,}")
c2.metric("AI-related Layoffs (filtered)", f"{kpi_layoffs:,}")
c3.metric("Hiring : Layoff Ratio", f"{kpi_ratio:.2f}x")

st.markdown("### Trends")
trend = (f.groupby(["month"], as_index=False)[["jobs","layoffs"]].sum())
trend_melt = trend.melt("month", value_name="count", var_name="series")
line = alt.Chart(trend_melt).mark_line(point=True).encode(
    x=alt.X("month:T", title="Month"),
    y=alt.Y("count:Q", title="Count"),
    color="series:N"
).properties(height=280)
st.altair_chart(line, use_container_width=True)

st.markdown("### Top Roles by Jobs (filtered)")
roles = (f.groupby("role", as_index=False)[["jobs","layoffs","salary_mid"]].agg({"jobs":"sum","layoffs":"sum","salary_mid":"mean"}).sort_values("jobs", ascending=False))
bar = alt.Chart(roles).mark_bar().encode(
    x=alt.X("jobs:Q", title="Jobs"),
    y=alt.Y("role:N", sort="-x", title=None),
    tooltip=["role","jobs","layoffs","salary_mid"]
).properties(height=300)
st.altair_chart(bar, use_container_width=True)

with st.expander("View data table"):
    st.dataframe(f.reset_index(drop=True))

st.markdown("---")
st.subheader("What’s next")
st.markdown("""
- 🔌 **Snowflake + dbt** connection (Facts/Dims + metrics)
- 💬 **AI chat copilot**: ask questions, get metrics + charts
- 🌎 Live feeds: postings, layoffs, skills, compensation, sentiment
""")
