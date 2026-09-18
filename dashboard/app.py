"""Streamlit dashboard for the completed Hillstrom email experiment."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.ticker import FuncFormatter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

TREATMENT_ORDER = ["No E-Mail", "Mens E-Mail", "Womens E-Mail"]
TREATMENT_COLORS = {
    "No E-Mail": "#7A8288",
    "Mens E-Mail": "#1F5A7A",
    "Womens E-Mail": "#A35D45",
}


st.set_page_config(
    page_title="Hillstrom Email Experiment",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def load_required_csv(filename: str) -> pd.DataFrame:
    """Load a validated output and fail clearly if it is unavailable."""
    path = TABLES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Required validated output is missing: {path}")
    return pd.read_csv(path)


def format_currency(value: float, signed: bool = False) -> str:
    prefix = "-" if value < 0 else "+" if signed else ""
    return f"{prefix}" + "$" + f"{abs(value):,.2f}"


def format_percentage(value: float) -> str:
    return f"{value * 100:.2f}%"


def format_percentage_points(value: float) -> str:
    prefix = "+" if value >= 0 else ""
    return f"{prefix}{value:.2f} pp"


def treatment_bar_chart(
    values: pd.Series, title: str, y_label: str, percentage: bool = False
) -> plt.Figure:
    """Create a consistently ordered treatment comparison chart."""
    ordered_values = values.reindex(TREATMENT_ORDER)
    fig, ax = plt.subplots(figsize=(8.5, 4.3))
    bars = ax.bar(
        ordered_values.index,
        ordered_values.values,
        color=[TREATMENT_COLORS[treatment] for treatment in ordered_values.index],
        width=0.62,
    )
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", pad=14)
    ax.set_ylabel(y_label)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D9DEE3", linewidth=0.8)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, ordered_values.values):
        label = format_percentage(value) if percentage else format_currency(value)
        ax.annotate(
            label,
            (bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            fontsize=10,
        )
    fig.tight_layout()
    return fig


def funnel_rate_chart(descriptive_data: pd.DataFrame) -> plt.Figure:
    """Create aligned, assigned-customer funnel rate comparisons."""
    metrics = ["Visit Rate", "Conversion Rate", "Positive-Spend Rate"]
    labels = ["Visit", "Conversion", "Positive spend"]
    x_positions = list(range(len(metrics)))
    offsets = [-0.25, 0, 0.25]

    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    for treatment, offset in zip(TREATMENT_ORDER, offsets):
        values = descriptive_data.loc[treatment, metrics].astype(float).values
        positions = [position + offset for position in x_positions]
        bars = ax.bar(
            positions,
            values,
            width=0.23,
            label=treatment,
            color=TREATMENT_COLORS[treatment],
        )
        for bar, value in zip(bars, values):
            ax.annotate(
                f"{value:.2f}%",
                (bar.get_x() + bar.get_width() / 2, value),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                fontsize=8,
            )
    ax.set_xticks(x_positions, labels)
    ax.set_ylabel("Rate among assigned customers")
    ax.set_title("Email treatments increased movement through the customer journey", loc="left", fontsize=13, fontweight="bold", pad=14)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D9DEE3", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    fig.tight_layout()
    return fig


def get_effect(primary_effects: pd.DataFrame, outcome: str, treatment: str) -> pd.Series:
    """Return one validated treatment-versus-control result."""
    result = primary_effects.loc[
        (primary_effects["Outcome"] == outcome)
        & (primary_effects["Treatment"] == treatment)
        & (primary_effects["Control"] == "No E-Mail")
    ]
    if result.empty:
        raise ValueError(f"Missing {outcome} result for {treatment} versus No E-Mail.")
    return result.iloc[0]


def ordered_segment_levels(segment_variable: str, levels: list[str]) -> list[str]:
    """Return logical display ordering without ranking effects by magnitude."""
    preferred_orders = {
        "channel": ["Multichannel", "Phone", "Web"],
        "zip_code": ["Rural", "Surburban", "Urban"],
        "newbie": ["0", "1"],
        "mens": ["0", "1"],
        "womens": ["0", "1"],
        "history_segment": [
            "1) $0 - $100",
            "2) $100 - $200",
            "3) $200 - $350",
            "4) $350 - $500",
            "5) $500 - $750",
            "6) $750 - $1,000",
            "7) $1,000 +",
        ],
    }
    preferred = preferred_orders[segment_variable]
    return [level for level in preferred if level in levels]


def format_subgroup_effect(value: float, outcome: str) -> str:
    """Format validated subgroup effects using their natural outcome units."""
    if outcome == "Spend":
        return f"{format_currency(value, signed=True)}/customer"
    return format_percentage_points(value * 100)


def format_subgroup_metric(value: float, outcome: str) -> str:
    """Format treatment and control subgroup metrics."""
    if outcome == "Spend":
        return format_currency(value)
    return format_percentage(value)


def segment_effect_chart(filtered_data: pd.DataFrame, outcome: str) -> plt.Figure:
    """Create a horizontal CI chart for the selected validated subgroup results."""
    plot_data = filtered_data.iloc[::-1].reset_index(drop=True)
    positions = list(range(len(plot_data)))
    effects = plot_data["Absolute Effect"].astype(float).values
    lower_errors = effects - plot_data["CI Lower"].astype(float).values
    upper_errors = plot_data["CI Upper"].astype(float).values - effects

    fig_height = max(3.5, 0.65 * len(plot_data) + 1.4)
    fig, ax = plt.subplots(figsize=(8.5, fig_height))
    ax.errorbar(
        effects,
        positions,
        xerr=[lower_errors, upper_errors],
        fmt="o",
        color=TREATMENT_COLORS[filtered_data["Treatment"].iloc[0]],
        ecolor="#65727D",
        capsize=3,
        markersize=6,
    )
    ax.axvline(0, color="#7A8288", linewidth=1, linestyle="--")
    ax.set_yticks(positions, plot_data["Segment Level"])
    ax.set_xlabel("Treatment-control effect ($/customer)" if outcome == "Spend" else "Treatment-control effect (percentage points)")
    ax.set_title("Estimated subgroup effects with 95% confidence intervals", loc="left", fontsize=13, fontweight="bold", pad=14)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color="#D9DEE3", linewidth=0.8)
    ax.set_axisbelow(True)
    if outcome != "Spend":
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value * 100:.1f} pp"))
    fig.tight_layout()
    return fig


def format_p_value(value: float) -> str:
    """Use concise notation for interaction and permutation p-values."""
    if value < 0.001:
        return f"{value:.2e}"
    return f"{value:.4f}"


try:
    executive_kpis = load_required_csv("executive_kpi_summary.csv")
    primary_effects = load_required_csv("primary_treatment_effects.csv")
    descriptive_summary = load_required_csv("experiment_descriptive_summary.csv")
    validation_summary = load_required_csv("experiment_validation_summary.csv")
    power_mde_summary = load_required_csv("power_mde_summary.csv")
    segment_treatment_effects = load_required_csv("segment_treatment_effects.csv")
    interaction_tests = load_required_csv("interaction_tests.csv")
    robustness_summary = load_required_csv("robustness_analysis_summary.csv")
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(f"The dashboard cannot load its required validated outputs. {error}")
    st.stop()


descriptive_summary = descriptive_summary.set_index("Treatment Group").reindex(TREATMENT_ORDER)
validation_summary = validation_summary.set_index("Framework Element")["Pre-specified Decision / Finding"]
mens_kpis = executive_kpis.loc[executive_kpis["treatment"] == "Mens E-Mail"].iloc[0]
womens_kpis = executive_kpis.loc[executive_kpis["treatment"] == "Womens E-Mail"].iloc[0]
mens_spend = get_effect(primary_effects, "Spend", "Mens E-Mail")
womens_spend = get_effect(primary_effects, "Spend", "Womens E-Mail")
conversion_planning_requirement = power_mde_summary.loc[
    (power_mde_summary["Outcome"] == "Conversion")
    & (power_mde_summary["Target Absolute Effect (pp)"] == 0.1)
    & (power_mde_summary["Power"] == 0.8)
].iloc[0]


st.title("Hillstrom Email Experiment")
st.subheader("A/B Testing, Experimentation & Causal Analysis")
st.write("Evaluating the impact of targeted email campaigns on customer visits, conversions, and spend.")
context_columns = st.columns(3)
context_columns[0].metric("Observations", "64,000")
context_columns[1].metric("Experimental arms", "3")
context_columns[2].metric("Primary metric", "Mean spend per assigned customer")

st.divider()
st.header("Experiment Overview")
overview_left, overview_right = st.columns([1, 1.4])
with overview_left:
    st.markdown("**Control**  \nNo E-Mail")
    st.markdown("**Treatments**  \nMens E-Mail  \nWomens E-Mail")
with overview_right:
    st.markdown("**Primary outcome**  \nMean spend per assigned customer")
    st.markdown("**Secondary outcomes**  \nConversion rate  \nVisit rate")
    st.markdown("**Assigned sample sizes**  \nNo E-Mail: 21,306 | Mens E-Mail: 21,307 | Womens E-Mail: 21,387")

st.header("Executive Summary")
st.write(
    "Both email treatments produced positive estimated effects versus No E-Mail across spend, "
    "conversion, and visits. Mean spend per assigned customer is the primary project outcome. "
    "Mens E-Mail produced the larger observed point estimates, although Mens versus Womens was "
    "not the primary confirmatory comparison. Profitability cannot yet be calculated because "
    "campaign cost and contribution margin are unavailable."
)

st.header("Executive KPI Cards")
mens_column, womens_column = st.columns(2)
with mens_column:
    st.subheader("Mens E-Mail vs No E-Mail")
    card_columns = st.columns(3)
    card_columns[0].metric("Incremental spend", f"{format_currency(mens_kpis['incremental_spend'], signed=True)}/customer")
    card_columns[1].metric("Conversion effect", format_percentage_points(mens_kpis["conversion_effect_pp"]))
    card_columns[2].metric("Visit effect", format_percentage_points(mens_kpis["visit_effect_pp"]))
with womens_column:
    st.subheader("Womens E-Mail vs No E-Mail")
    card_columns = st.columns(3)
    card_columns[0].metric("Incremental spend", f"{format_currency(womens_kpis['incremental_spend'], signed=True)}/customer")
    card_columns[1].metric("Conversion effect", format_percentage_points(womens_kpis["conversion_effect_pp"]))
    card_columns[2].metric("Visit effect", format_percentage_points(womens_kpis["visit_effect_pp"]))

st.header("Impact per 1,000 Assigned Customers")
st.caption("Experiment-scaled estimates, not future profit forecasts.")
impact_columns = st.columns(2)
for column, label, kpis in [
    (impact_columns[0], "Mens E-Mail", mens_kpis),
    (impact_columns[1], "Womens E-Mail", womens_kpis),
]:
    with column:
        st.subheader(label)
        measures = st.columns(3)
        measures[0].metric("Expected spend", format_currency(kpis["incremental_spend_per_1000"], signed=True))
        measures[1].metric("Conversions", f"+{kpis['incremental_conversions_per_1000']:.2f}")
        measures[2].metric("Visits", f"+{kpis['incremental_visits_per_1000']:.2f}")

st.header("Primary Outcome: Spend")
spend_figure = treatment_bar_chart(
    descriptive_summary["Mean Spend"],
    "Both email treatments increased average spend versus No E-Mail",
    "Mean spend per assigned customer",
)
st.pyplot(spend_figure, width="stretch")
plt.close(spend_figure)

spend_effect_columns = st.columns(2)
for column, label, effect in [
    (spend_effect_columns[0], "Mens E-Mail", mens_spend),
    (spend_effect_columns[1], "Womens E-Mail", womens_spend),
]:
    with column:
        st.subheader(f"{label} vs No E-Mail")
        st.metric("Estimated spend effect", f"{format_currency(effect['Absolute Effect'], signed=True)}/customer")
        st.write(
            f"95% CI: {format_currency(effect['CI Lower'], signed=True)} to "
            f"{format_currency(effect['CI Upper'], signed=True)} per customer"
        )

validated_spend_figure = FIGURES_DIR / "spend_treatment_effects.png"
if validated_spend_figure.exists():
    st.image(validated_spend_figure, caption="Validated treatment-effect estimates for mean spend.")

st.header("Conversion")
conversion_figure = treatment_bar_chart(
    descriptive_summary["Conversion Rate"] / 100,
    "Email treatments increased conversion rates versus No E-Mail",
    "Conversion rate",
    percentage=True,
)
st.pyplot(conversion_figure, width="stretch")
plt.close(conversion_figure)
st.write(
    f"Mens E-Mail: {format_percentage_points(mens_kpis['conversion_effect_pp'])} versus No E-Mail. "
    f"Womens E-Mail: {format_percentage_points(womens_kpis['conversion_effect_pp'])} versus No E-Mail."
)

st.header("Visit")
visit_figure = treatment_bar_chart(
    descriptive_summary["Visit Rate"] / 100,
    "Email treatments increased visit rates versus No E-Mail",
    "Visit rate",
    percentage=True,
)
st.pyplot(visit_figure, width="stretch")
plt.close(visit_figure)
st.write(
    f"Mens E-Mail: {format_percentage_points(mens_kpis['visit_effect_pp'])} versus No E-Mail. "
    f"Womens E-Mail: {format_percentage_points(womens_kpis['visit_effect_pp'])} versus No E-Mail."
)

st.divider()
st.header("Customer Funnel")
st.caption("All main rates use assigned customers as the denominator.")
funnel_figure = funnel_rate_chart(descriptive_summary)
st.pyplot(funnel_figure, width="stretch")
plt.close(funnel_figure)

funnel_display = descriptive_summary[
    ["Sample Size", "Visit Rate", "Conversion Rate", "Positive-Spend Rate"]
].copy()
funnel_display.columns = [
    "Assigned customers",
    "Visit rate",
    "Conversion rate",
    "Positive-spend rate",
]
for column in ["Visit rate", "Conversion rate", "Positive-spend rate"]:
    funnel_display[column] = funnel_display[column].map(lambda value: f"{value:.2f}%")
st.dataframe(funnel_display, width="stretch")
st.caption(
    "Visit Rate = visitors / assigned customers. Conversion Rate = conversions / assigned customers. "
    "Positive-Spend Rate = customers with spend greater than zero / assigned customers."
)
st.write(
    "Both email treatments increased movement through the customer journey relative to No E-Mail, "
    "particularly at the visit stage. The observed increase in average spend appears more related "
    "to higher purchase frequency than to dramatically larger transaction values among purchasers."
)

st.subheader("Spend Decomposition")
positive_spender_spend = pd.DataFrame(
    {
        "Positive-spend rate": ["0.57%", "1.25%", "0.88%"],
        "Mean spend among positive spenders": ["$114.00", "$113.53", "$121.89"],
    },
    index=TREATMENT_ORDER,
)
st.dataframe(positive_spender_spend, width="stretch")
st.caption(
    "Conditional spend among purchasers is descriptive because purchase status is a post-treatment "
    "variable; it is not a separate causal treatment effect."
)

st.header("Experiment Reliability")
st.caption("Source: Stage 04 experiment validation")
reliability_scorecard = pd.DataFrame(
    [
        ["Treatment allocation", "No evidence of SRM", validation_summary["SRM result"]],
        ["Baseline balance", "Closely balanced", validation_summary["Baseline balance"]],
        ["Missing data", "None detected", "No missingness detected in the validation checks."],
        ["Outcome logic", "No invalid relationships detected", "Validation checks found no invalid outcome relationships."],
        ["Customer identity verification", "Unavailable", "No customer ID is present in the source data."],
        ["Temporal monitoring", "Unavailable", "No timestamp is present in the source data."],
        ["Outcome window", "Not documented", "The source data does not document an outcome window."],
    ],
    columns=["Diagnostic", "Status", "Evidence"],
)
st.dataframe(reliability_scorecard, width="stretch", hide_index=True)
st.write(
    "The allocation and observable baseline diagnostics support the credibility of the randomized "
    "comparison, but do not independently prove perfect randomization."
)

baseline_figure = FIGURES_DIR / "baseline_balance_smd.png"
if baseline_figure.exists():
    st.image(baseline_figure, caption="Observed baseline balance, including the 0.10 SMD reference heuristic.")

with st.expander("How experiment health was evaluated"):
    st.write(
        "Sample Ratio Mismatch (SRM) checks whether observed group sizes are inconsistent with the "
        "assumed allocation. Standardized mean differences (SMDs) summarize observable baseline "
        "imbalance; the largest observed absolute SMD was 0.0164, below the 0.10 reference heuristic."
    )

st.header("Experiment Sensitivity")
st.caption("Source: Stage 06 power and MDE analysis")
sensitivity_columns = st.columns(2)
with sensitivity_columns[0]:
    st.subheader("Conversion")
    st.metric("Control baseline", "0.5726%")
    st.metric("80% MDE", "+0.223 pp")
    st.metric("90% MDE", "+0.261 pp")
with sensitivity_columns[1]:
    st.subheader("Visit")
    st.metric("Control baseline", "10.6167%")
    st.metric("80% MDE", "+0.850 pp")
    st.metric("90% MDE", "+0.987 pp")

st.write(
    "At the actual sample size, the experiment had enough sensitivity to detect effects around "
    "the magnitude observed in Stage 05. Much smaller conversion improvements would require "
    "substantially larger samples. For example, detecting approximately +0.10 percentage points "
    f"in conversion at 80% power would require roughly {int(conversion_planning_requirement['Required Sample Size Per Group']):,} "
    "customers per group under the planning assumptions."
)
st.info(
    "Statistical significance asks whether an observed effect is supported by the experiment's "
    "uncertainty. Practical significance asks whether the magnitude is large enough to matter "
    "economically. Profitability cannot be determined without campaign cost and contribution margin."
)

with st.expander("How MDE should be interpreted"):
    st.write(
        "Minimum Detectable Effect (MDE) is the smallest absolute effect the design could detect "
        "under its specified alpha, power, baseline, and sample-size assumptions. It is a planning "
        "quantity, not post-hoc observed power."
    )
    conversion_mde_figure = FIGURES_DIR / "conversion_mde_curve.png"
    visit_mde_figure = FIGURES_DIR / "visit_mde_curve.png"
    if conversion_mde_figure.exists():
        st.image(conversion_mde_figure, caption="Conversion power across absolute effect sizes.")
    if visit_mde_figure.exists():
        st.image(visit_mde_figure, caption="Visit power across absolute effect sizes.")

with st.expander("Metric glossary"):
    st.markdown(
        "**Mean Spend per Assigned Customer:** total spend / assigned customers.  \n"
        "**Visit Rate:** visitors / assigned customers.  \n"
        "**Conversion Rate:** conversions / assigned customers.  \n"
        "**Positive-Spend Rate:** customers with spend greater than zero / assigned customers.  \n"
        "**Absolute Effect:** treatment metric - control metric.  \n"
        "**Relative Lift:** absolute effect / control metric.  \n"
        "**Percentage-Point Effect:** absolute difference between rates.  \n"
        "**95% Confidence Interval:** uncertainty range for an estimate under the stated inferential method.  \n"
        "**SMD:** standardized mean difference used for observable baseline balance.  \n"
        "**SRM:** Sample Ratio Mismatch diagnostic.  \n"
        "**MDE:** Minimum Detectable Effect under specified planning assumptions.  \n"
        "**FDR:** False Discovery Rate adjustment used for exploratory interaction testing."
    )

st.divider()
st.header("Exploratory Segment Analysis")
st.caption("Stage 07: Exploratory heterogeneity analysis")
st.info(
    "Subgroup findings are exploratory and hypothesis-generating. They should not be interpreted "
    "as validated targeting rules."
)
st.write(
    "A total of 114 subgroup comparisons were explored. Thirteen interaction tests had raw p < 0.05, "
    "and six remained notable after Benjamini-Hochberg FDR adjustment."
)

selector_columns = st.columns(3)
with selector_columns[0]:
    selected_treatment = st.selectbox("Treatment", ["Mens E-Mail", "Womens E-Mail"])
with selector_columns[1]:
    selected_outcome = st.selectbox("Outcome", ["Spend", "Conversion", "Visit"])
with selector_columns[2]:
    selected_segment = st.selectbox(
        "Segment dimension",
        ["channel", "zip_code", "newbie", "history_segment", "mens", "womens"],
    )

filtered_segments = segment_treatment_effects.loc[
    (segment_treatment_effects["Treatment"] == selected_treatment)
    & (segment_treatment_effects["Outcome"] == selected_outcome)
    & (segment_treatment_effects["Segment Variable"] == selected_segment)
].copy()

if filtered_segments.empty:
    st.info("No validated subgroup results are available for this selection.")
else:
    segment_order = ordered_segment_levels(
        selected_segment, filtered_segments["Segment Level"].astype(str).tolist()
    )
    filtered_segments["Segment Level"] = pd.Categorical(
        filtered_segments["Segment Level"], categories=segment_order, ordered=True
    )
    filtered_segments = filtered_segments.sort_values("Segment Level")

    if (
        (filtered_segments["Treatment N"] < 1000).any()
        or (filtered_segments["Control N"] < 1000).any()
        or (filtered_segments["Sparse Event Flag"].astype(str) == "True").any()
    ):
        st.warning(
            "Interpret cautiously: one or more subgroup cells have limited sample size or sparse conversion events."
        )

    segment_figure = segment_effect_chart(filtered_segments, selected_outcome)
    st.pyplot(segment_figure, width="stretch")
    plt.close(segment_figure)

    segment_display = pd.DataFrame(
        {
            "Segment level": filtered_segments["Segment Level"].astype(str),
            "Treatment N": filtered_segments["Treatment N"].map("{:,.0f}".format),
            "Control N": filtered_segments["Control N"].map("{:,.0f}".format),
            "Treatment metric": filtered_segments["Treatment Metric"].map(
                lambda value: format_subgroup_metric(value, selected_outcome)
            ),
            "Control metric": filtered_segments["Control Metric"].map(
                lambda value: format_subgroup_metric(value, selected_outcome)
            ),
            "Absolute effect": filtered_segments["Absolute Effect"].map(
                lambda value: format_subgroup_effect(value, selected_outcome)
            ),
            "95% CI": [
                f"{format_subgroup_effect(lower, selected_outcome)} to "
                f"{format_subgroup_effect(upper, selected_outcome)}"
                for lower, upper in zip(filtered_segments["CI Lower"], filtered_segments["CI Upper"])
            ],
            "Relative lift": filtered_segments["Relative Lift"].map(
                lambda value: f"{value * 100:+.1f}%"
            ),
            "Sparse event flag": filtered_segments["Sparse Event Flag"],
        }
    )
    st.dataframe(segment_display, width="stretch", hide_index=True)
    st.caption(
        "Absolute effect is the primary subgroup measure. Relative effects can appear large when "
        "the control metric is very small, especially for rare conversion outcomes."
    )

st.write(
    "Subgroup effects are broadly directionally consistent with the positive overall experiment "
    "effects, while magnitude varies across customer characteristics. Several interaction signals "
    "survived exploratory FDR adjustment, but some large point estimates occur in small or sparse "
    "subgroups. Prospective experiments should validate these hypotheses before targeting decisions."
)

with st.expander("Treatment × Segment Interaction Tests"):
    interaction_display = interaction_tests[
        [
            "Outcome",
            "Treatment",
            "Segment Variable",
            "Raw P-Value",
            "FDR Adjusted P-Value",
            "Interpretation",
        ]
    ].copy()
    interaction_display["Raw P-Value"] = interaction_display["Raw P-Value"].map(format_p_value)
    interaction_display["FDR Adjusted P-Value"] = interaction_display["FDR Adjusted P-Value"].map(format_p_value)
    interaction_display["Interpretation"] = interaction_tests.apply(
        lambda row: "Signal for prospective validation"
        if row["FDR Adjusted P-Value"] < 0.05
        else row["Interpretation"],
        axis=1,
    )
    st.dataframe(interaction_display, width="stretch", hide_index=True)
    st.markdown(
        "**Signals for prospective validation:** Womens E-Mail × mens for visit; Womens E-Mail × womens "
        "for visit; Womens E-Mail × newbie for visit; Mens E-Mail × newbie for visit; Womens E-Mail × "
        "newbie for conversion; Womens E-Mail × zip_code for visit."
    )

with st.expander("View full Stage 07 subgroup forest plots"):
    for filename, caption in [
        ("segment_spend_forest.png", "Stage 07 subgroup spend effects."),
        ("segment_conversion_forest.png", "Stage 07 subgroup conversion effects."),
        ("segment_visit_forest.png", "Stage 07 subgroup visit effects."),
    ]:
        figure_path = FIGURES_DIR / filename
        if figure_path.exists():
            st.image(figure_path, caption=caption)

st.header("Robustness Checks")
st.caption("Stage 08: Robustness/supporting analysis")
st.write(
    "Stage 05 is the primary analysis. The checks below evaluate whether its conclusions materially "
    "change under reasonable alternative analytical specifications."
)

spend_robustness = robustness_summary.loc[robustness_summary["Outcome"] == "Spend"].copy()
spend_robustness["Exclude top 20 global spend observations"] = [
    0.637502,
    0.378822,
]
spend_robustness_display = pd.DataFrame(
    {
        "Treatment": spend_robustness["Treatment"],
        "Primary full sample": spend_robustness["Primary Estimate"].map(
            lambda value: f"{format_currency(value, signed=True)}/customer"
        ),
        "Covariate-adjusted": spend_robustness["Adjusted Estimate"].map(
            lambda value: f"{format_currency(value, signed=True)}/customer"
        ),
        "Exclude top 20 global spend observations": spend_robustness[
            "Exclude top 20 global spend observations"
        ].map(lambda value: f"{format_currency(value, signed=True)}/customer"),
    }
)
st.subheader("Spend sensitivity")
st.dataframe(spend_robustness_display, width="stretch", hide_index=True)
st.write(
    "Covariate adjustment produced very similar spend estimates, supporting stability of the primary "
    "treatment effects. Estimated spend effects attenuate somewhat when the largest transactions are "
    "excluded, particularly for Mens E-Mail, but remain directionally positive."
)

adjusted_spend_figure = FIGURES_DIR / "adjusted_vs_unadjusted_spend.png"
if adjusted_spend_figure.exists():
    st.image(adjusted_spend_figure, caption="Stage 05 primary and Stage 08 adjusted spend estimates.")

permutation_display = spend_robustness[["Treatment", "Permutation P-Value"]].copy()
permutation_display["Permutation P-Value"] = permutation_display["Permutation P-Value"].map(format_p_value)
st.caption("Spend permutation sensitivity")
st.dataframe(permutation_display, width="stretch", hide_index=True)
st.write(
    "Permutation-based inference produced the same qualitative conclusion as the primary Stage 05 analysis."
)

robustness_scorecard = pd.DataFrame(
    [
        ["Covariate adjustment", "Stable", "Adjusted estimates are similar to Stage 05 primary estimates."],
        ["Permutation inference", "Consistent", "Spend permutation p-values support the same qualitative conclusion."],
        ["Extreme-value sensitivity", "Some attenuation, direction stable", "Large purchases contribute somewhat to estimated spend magnitude."],
        ["Binary adjusted effects", "Directionally consistent", "Adjusted conversion and visit effects remain positive."],
    ],
    columns=["Check", "Finding", "Interpretation"],
)
st.dataframe(robustness_scorecard, width="stretch", hide_index=True)

with st.expander("Adjusted binary-outcome estimates"):
    binary_robustness = robustness_summary.loc[
        robustness_summary["Outcome"].isin(["Conversion", "Visit"])
    ].copy()
    binary_display = pd.DataFrame(
        {
            "Outcome": binary_robustness["Outcome"],
            "Treatment": binary_robustness["Treatment"],
            "Stage 05 primary effect": binary_robustness["Primary Estimate"].map(
                lambda value: format_percentage_points(value * 100)
            ),
            "Stage 08 adjusted effect": binary_robustness["Adjusted Estimate"].map(
                lambda value: format_percentage_points(value * 100)
            ),
        }
    )
    st.dataframe(binary_display, width="stretch", hide_index=True)
    adjusted_binary_figure = FIGURES_DIR / "adjusted_vs_unadjusted_binary.png"
    if adjusted_binary_figure.exists():
        st.image(adjusted_binary_figure, caption="Stage 05 primary and Stage 08 adjusted binary-outcome effects.")

st.write(
    "No major qualitative reversal occurred across bootstrap uncertainty, conventional mean inference, "
    "covariate-adjusted models, permutation inference, and extreme-value diagnostics. Extreme purchases "
    "do contribute somewhat to the magnitude of the spend estimate."
)

st.divider()
st.header("From Experiment Lift to Business Decision")
st.write(
    "Both email treatments increased measured customer activity and expected spend versus No E-Mail. "
    "Whether either campaign should be deployed depends on whether incremental economic value exceeds "
    "incremental campaign cost."
)
st.info(
    "Incremental Profit per Assigned Customer = Incremental Spend × Contribution Margin "
    "- Incremental Campaign Cost per Assigned Customer"
)
st.subheader("Break-even framework")
business_columns = st.columns(2)
with business_columns[0]:
    st.markdown(
        f"**Mens E-Mail**  \nIncremental contribution before campaign cost = "
        f"{mens_kpis['incremental_spend']:.4f} × M"
    )
with business_columns[1]:
    st.markdown(
        f"**Womens E-Mail**  \nIncremental contribution before campaign cost = "
        f"{womens_kpis['incremental_spend']:.4f} × M"
    )
st.caption(
    "M is actual contribution margin. Net incremental contribution = incremental spend × M - campaign cost. "
    "Contribution margin, campaign cost, fulfillment or variable cost, customer lifetime value, and future "
    "audience size are not available, so this dashboard does not calculate ROI."
)

st.header("Methodology")
st.caption("The project follows a staged workflow from source understanding to stakeholder communication.")
st.markdown(
    "Data Understanding → Data Integrity & Cleaning → Exploratory Analysis → Experiment Validation → "
    "Primary Treatment-Effect Analysis → Power & MDE → Exploratory Heterogeneity → Robustness Analysis → "
    "SQL Reporting Layer → Dashboard"
)
st.caption(
    "Technology stack: Python, Pandas, NumPy, SciPy, Statsmodels, Matplotlib, PostgreSQL-compatible SQL, "
    "Streamlit, Jupyter, and pytest."
)

methodology_hierarchy = pd.DataFrame(
    [
        ["Stage 05", "Primary confirmatory analysis", "Treatment effects versus No E-Mail"],
        ["Stage 06", "Experiment sensitivity / planning analysis", "Power and minimum detectable effects"],
        ["Stage 07", "Exploratory heterogeneity analysis", "Subgroup effects and interaction tests"],
        ["Stage 08", "Robustness / supporting analysis", "Alternative specifications and sensitivity checks"],
    ],
    columns=["Stage", "Role", "Scope"],
)
st.dataframe(methodology_hierarchy, width="stretch", hide_index=True)

with st.expander("Analytical Architecture"):
    st.markdown(
        "Raw / Processed Data  \n"
        "↓  \n"
        "SQL Analytical Layer  \n"
        "↓  \n"
        "Validated KPI Outputs  \n"
        "↓  \n"
        "Python Statistical Analysis  \n"
        "↓  \n"
        "Validated Reporting Outputs  \n"
        "↓  \n"
        "Streamlit Dashboard"
    )
    architecture_columns = st.columns(3)
    with architecture_columns[0]:
        st.markdown(
            "**SQL**  \nSchema, profiling, data-quality checks, experiment population, health inputs, "
            "funnel metrics, KPI aggregation, segment reporting, and reusable analytical views."
        )
    with architecture_columns[1]:
        st.markdown(
            "**Python**  \nStatistical inference, bootstrap confidence intervals, validation, power/MDE, "
            "regression adjustment, interaction testing, robustness checks, and visualization."
        )
    with architecture_columns[2]:
        st.markdown(
            "**Streamlit**  \nStakeholder communication and interactive exploration of validated outputs."
        )
    st.markdown(
        "**PostgreSQL-compatible SQL workflow:** 01 Schema → 02 Profiling → 03 Data Quality → "
        "04 Experiment Population → 05 Experiment Health → 06 Funnel → 07 Experiment Metrics → "
        "08 Segment Analysis → 09 Analytical Views."
    )
    st.caption(
        "The SQL logic was validated against Python aggregations because PostgreSQL was not installed locally "
        "when the SQL layer was built. The dashboard does not claim direct local database execution."
    )

st.header("Limitations")
st.caption("These constraints shape how the results should be interpreted and applied.")
with st.expander("Data, design, and business limitations"):
    st.markdown(
        "1. **Customer identity:** No explicit customer identifier is available, so unique experimental units "
        "cannot be independently verified.  \n"
        "2. **Duplicate rows:** Identical rows were retained because identical observed records do not prove "
        "duplicated customers.  \n"
        "3. **Time:** No experiment timestamp exists, preventing temporal monitoring and trend analysis.  \n"
        "4. **Allocation:** The equal one-third treatment ratio was inferred rather than verified from original "
        "experiment documentation.  \n"
        "5. **Outcome window:** The exact measurement window is not documented in the dataset.  \n"
        "6. **Original experiment protocol:** Original preregistration, hypotheses, and primary endpoint are "
        "not available.  \n"
        "7. **Spend distribution:** Spend is highly zero-inflated and right-skewed.  \n"
        "8. **Heterogeneity:** Subgroup findings are exploratory and require prospective validation.  \n"
        "9. **Business economics:** Campaign cost, margin, customer lifetime value, and future audience size are "
        "unavailable.  \n"
        "10. **External validity:** Results from this experiment do not guarantee identical effects in future "
        "campaigns or populations."
    )
