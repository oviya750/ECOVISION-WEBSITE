from flask import Flask, render_template, jsonify, request
import pandas as pd
import os

# =========================================================
# FLASK APP
# =========================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# =========================================================
# BASE PATH
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "final data set.xlsx"
)

# =========================================================
# LOAD DATASET
# =========================================================

df = pd.DataFrame()

try:

    if not os.path.isfile(DATA_FILE):
        raise FileNotFoundError(
            f"Excel file not found:\n{DATA_FILE}"
        )

    df = pd.read_excel(DATA_FILE)

    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    print("=" * 70)
    print("ECOVISION DATASET LOADED")
    print("=" * 70)
    print("File    :", DATA_FILE)
    print("Rows    :", len(df))
    print("Columns :", len(df.columns))

    if "Country name" in df.columns:
        print(
            "Countries:",
            df["Country name"]
            .dropna()
            .astype(str)
            .str.strip()
            .nunique()
        )

    print("=" * 70)

except Exception as e:

    print("=" * 70)
    print("DATASET ERROR")
    print("=" * 70)
    print(str(e))
    print("=" * 70)


# =========================================================
# COLUMN DETECTION
# =========================================================

def find_column(names):

    if df.empty:
        return None

    # Exact match
    for name in names:
        if name in df.columns:
            return name

    # Case-insensitive match
    lower_map = {
        str(col).lower().strip(): col
        for col in df.columns
    }

    for name in names:

        key = str(name).lower().strip()

        if key in lower_map:
            return lower_map[key]

    # Partial match
    for col in df.columns:

        col_text = str(col).lower().strip()

        for name in names:

            name_text = str(name).lower().strip()

            if name_text in col_text:
                return col

    return None


# =========================================================
# DATASET COLUMNS
# =========================================================

COUNTRY_COL = find_column([
    "Country name",
    "Country",
    "Country_Name"
])

REGION_COL = find_column([
    "Region"
])

INCOME_COL = find_column([
    "Income group (2022)",
    "Income group (waste generation year)",
    "Income group"
])

YEAR_COL = find_column([
    "Year",
    "MSW generation - year reported"
])

POPULATION_COL = find_column([
    "Population in 2022",
    "Population (Millions)",
    "Population"
])

GDP_COL = find_column([
    "GDP",
    "GDP per capita",
    "GDP (US$)"
])

MSW_COL = find_column([
    "MSW generation (t/y)",
    "MSW generation - projected 2022 (t/year)",
    "MSW generation - projected 2030 (t/y)",
    "MSW generation"
])

MSW_CAPITA_COL = find_column([
    "MSW generation (kg/capita/day)",
    "MSW generation - projected 2022 (kg/cap/day)",
    "MSW generation - projected 2030 (kg/cap/day)"
])

RECYCLING_COL = find_column([
    "Recycling Rate (%)",
    "Recycling_Rate",
    "Treatment - recycling (% weight MSW generated)"
])

COLLECTION_COL = find_column([
    "Collection coverage - total (% population)",
    "Collection coverage - total (% households)",
    "Collection coverage - total (% weight MSW)"
])

OPEN_DUMP_COL = find_column([
    "Treatment - open dump (% weight MSW generated)"
])


# =========================================================
# PRINT DETECTED COLUMNS
# =========================================================

print()
print("Detected Columns")
print("-" * 70)

print("Country    :", COUNTRY_COL)
print("Region     :", REGION_COL)
print("Income     :", INCOME_COL)
print("Year       :", YEAR_COL)
print("Population :", POPULATION_COL)
print("GDP        :", GDP_COL)
print("MSW        :", MSW_COL)
print("MSW/Capita :", MSW_CAPITA_COL)
print("Recycling  :", RECYCLING_COL)
print("Collection  :", COLLECTION_COL)
print("Open Dump  :", OPEN_DUMP_COL)

print("-" * 70)
print()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def numeric_series(data, column):

    if (
        data is None
        or data.empty
        or column is None
        or column not in data.columns
    ):
        return pd.Series(dtype="float64")

    return pd.to_numeric(
        data[column],
        errors="coerce"
    )


def safe_sum(data, column):

    series = numeric_series(
        data,
        column
    )

    if series.empty:
        return 0

    return float(
        series.fillna(0).sum()
    )


def safe_mean(data, column):

    series = numeric_series(
        data,
        column
    )

    series = series.dropna()

    if series.empty:
        return 0

    return float(
        series.mean()
    )


def percentage(value):

    try:

        value = float(value)

        if pd.isna(value):
            return 0

        # Convert decimal to percentage
        if 0 <= value <= 1:
            value *= 100

        return round(value, 2)

    except Exception:
        return 0


def format_number(value):

    try:

        value = float(value)

        if pd.isna(value):
            return 0

        return round(value, 2)

    except Exception:
        return 0


# =========================================================
# DROPDOWN DATA
# =========================================================

def get_unique_values(column):

    if (
        df.empty
        or column is None
        or column not in df.columns
    ):
        return []

    values = (
        df[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = values[
        values != ""
    ]

    return sorted(
        values.unique().tolist()
    )


def get_countries():
    return get_unique_values(COUNTRY_COL)


def get_regions():
    return get_unique_values(REGION_COL)


def get_income_groups():
    return get_unique_values(INCOME_COL)


def get_years():

    if (
        df.empty
        or YEAR_COL is None
        or YEAR_COL not in df.columns
    ):
        return []

    values = pd.to_numeric(
        df[YEAR_COL],
        errors="coerce"
    ).dropna()

    if values.empty:
        return []

    return sorted(
        values.astype(int)
        .unique()
        .tolist()
    )


# =========================================================
# FILTER DATA
# =========================================================

def filtered_data():

    data = df.copy()

    country = request.args.get(
        "country",
        "All"
    ).strip()

    region = request.args.get(
        "region",
        "All"
    ).strip()

    income = request.args.get(
        "income",
        "All"
    ).strip()

    year = request.args.get(
        "year",
        "All"
    ).strip()

    # COUNTRY
    if (
        country != "All"
        and country
        and COUNTRY_COL
        and COUNTRY_COL in data.columns
    ):

        data = data[
            data[COUNTRY_COL]
            .astype(str)
            .str.strip()
            .eq(country)
        ]

    # REGION
    if (
        region != "All"
        and region
        and REGION_COL
        and REGION_COL in data.columns
    ):

        data = data[
            data[REGION_COL]
            .astype(str)
            .str.strip()
            .eq(region)
        ]

    # INCOME
    if (
        income != "All"
        and income
        and INCOME_COL
        and INCOME_COL in data.columns
    ):

        data = data[
            data[INCOME_COL]
            .astype(str)
            .str.strip()
            .eq(income)
        ]

    # YEAR
    if (
        year != "All"
        and year
        and YEAR_COL
        and YEAR_COL in data.columns
    ):

        year_number = pd.to_numeric(
            year,
            errors="coerce"
        )

        if pd.notna(year_number):

            data = data[
                pd.to_numeric(
                    data[YEAR_COL],
                    errors="coerce"
                ).eq(year_number)
            ]

    return data


# =========================================================
# COUNTRY COUNT
# =========================================================

def country_count(data):

    if (
        data.empty
        or COUNTRY_COL is None
        or COUNTRY_COL not in data.columns
    ):
        return 0

    return int(
        data[COUNTRY_COL]
        .dropna()
        .astype(str)
        .str.strip()
        .nunique()
    )


# =========================================================
# AI RISK
# =========================================================

def value_for(data, column):
    """Return a safe percentage/number value for an optional metric."""
    if column in (None, ""):
        return None
    series = numeric_series(data, column).dropna()
    if series.empty:
        return None
    return float(series.mean())


def risk_level(score):
    if score >= 70:
        return "High Risk"
    if score >= 50:
        return "Medium Risk"
    if score >= 30:
        return "Moderate"
    return "Low Risk"


def analyze_environment(data):
    recycling = percentage(value_for(data, RECYCLING_COL) or 0)
    collection = percentage(value_for(data, COLLECTION_COL) or 0)
    open_dump = percentage(value_for(data, OPEN_DUMP_COL) or 0)
    waste_pc = value_for(data, MSW_CAPITA_COL)
    landfill_col = find_column(["Treatment - landfill (% weight MSW generated)", "Landfill"])
    compost_col = find_column(["Treatment - composting (% weight MSW generated)", "Composting"])
    landfill = percentage(value_for(data, landfill_col) or 0)
    composting = percentage(value_for(data, compost_col) or 0)

    available = []
    if value_for(data, RECYCLING_COL) is not None:
        available.append(("Recycling Gap", max(0, 100 - recycling), 0.30, "Improve material recovery"))
    if value_for(data, COLLECTION_COL) is not None:
        available.append(("Collection Gap", max(0, 100 - collection), 0.20, "Expand collection access"))
    if value_for(data, OPEN_DUMP_COL) is not None:
        available.append(("Open Dump Pressure", open_dump, 0.20, "Reduce uncontrolled disposal"))
    if waste_pc is not None:
        available.append(("Waste Pressure", min(100, max(0, waste_pc * 50)), 0.20, "Reduce waste intensity"))
    if value_for(data, landfill_col) is not None:
        available.append(("Landfill Pressure", landfill, 0.10, "Diversify disposal routes"))

    weight_total = sum(item[2] for item in available) or 1
    drivers = sorted(
        [{"factor": label, "value": round(value, 1), "contribution": round(value * weight / weight_total, 1), "action": action}
         for label, value, weight, action in available],
        key=lambda item: item["contribution"], reverse=True
    )
    score = round(min(100, sum(item["contribution"] for item in drivers)), 1)
    level = risk_level(score)
    confidence = round(min(98, 45 + (len(available) / 5) * 50), 0)
    sustainability = round(max(0, min(100, 100 - score)), 1)

    if not drivers:
        diagnosis = "Environmental diagnosis is unavailable because the selected records contain no recognised waste-management indicators."
        priority = "Collect consistent waste-management data"
    elif drivers[0]["factor"] == "Recycling Gap" and recycling < 35:
        diagnosis = "The selected profile is primarily constrained by low material recovery, leaving a large recycling gap in the reported waste stream."
        priority = "Prioritize source segregation and material recovery capacity"
    elif drivers[0]["factor"] == "Collection Gap":
        diagnosis = "The selected profile shows a service-access gap: waste collection coverage is the leading pressure among available indicators."
        priority = "Expand reliable collection coverage and service accessibility"
    elif drivers[0]["factor"] == "Open Dump Pressure":
        diagnosis = "The selected profile is exposed to uncontrolled disposal pressure, which increases environmental and public-health risk."
        priority = "Replace open dumping with controlled disposal and diversion"
    elif drivers[0]["factor"] == "Landfill Pressure":
        diagnosis = "The selected profile depends heavily on landfill disposal, indicating an opportunity to divert more material into recovery and composting."
        priority = "Build diversion, composting and resource-recovery pathways"
    else:
        diagnosis = "The selected profile's leading pressure is waste intensity, suggesting that prevention and circular-economy measures should come first."
        priority = "Reduce waste intensity through prevention and producer responsibility"

    if recycling >= 65 and collection >= 80 and open_dump < 10:
        diagnosis = "The selected profile has strong core service indicators; the next opportunity is maintaining performance while advancing prevention and circularity."
        priority = "Maintain performance and advance circular-economy strategies"

    return {
        "score": score, "level": level, "sustainability": sustainability,
        "confidence": confidence, "drivers": drivers[:3],
        "all_factors": drivers, "diagnosis": diagnosis, "priority": priority,
        "implementation": [
            "Phase 1: strengthen the leading environmental gap",
            "Phase 2: scale collection, sorting or recovery capacity",
            "Phase 3: measure diversion and service improvements",
            "Phase 4: maintain gains through circular-economy policy"
        ],
        "expected_impact": "Closing the dominant reported gaps should lower environmental pressure; the magnitude depends on future measured performance.",
        "metrics": {"recycling": recycling, "collection": collection, "open_dump": open_dump, "landfill": landfill, "composting": composting, "waste_pc": waste_pc}
    }


def calculate_risk(data):
    analysis = analyze_environment(data)
    return analysis["score"], analysis["level"]


# =========================================================
# AI RECOMMENDATION
# =========================================================

def recommendation(risk_level):
    return {
        "High Risk": "Urgent action is required on the leading environmental gaps.",
        "Medium Risk": "Target the leading environmental gaps with focused infrastructure investment.",
        "Moderate": "Improve the leading service and recovery indicators while monitoring progress.",
        "Low Risk": "Maintain current performance and advance prevention and circularity."
    }.get(risk_level, "Collect more complete environmental data.")


# =========================================================
# DASHBOARD API
# =========================================================

@app.route("/api/dashboard")
def dashboard_api():

    try:

        data = filtered_data()

        # =================================================
        # KPI
        # =================================================

        total_countries = country_count(data)

        total_msw = safe_sum(
            data,
            MSW_COL
        )

        average_recycling = percentage(
            safe_mean(
                data,
                RECYCLING_COL
            )
        )

        total_population = safe_sum(
            data,
            POPULATION_COL
        )

        average_gdp = safe_mean(
            data,
            GDP_COL
        )

        average_collection = percentage(
            safe_mean(
                data,
                COLLECTION_COL
            )
        )

        risk_score, risk_level = calculate_risk(
            data
        )

        analysis = analyze_environment(data)

        ai_recommendation = recommendation(
            risk_level
        )

        # =================================================
        # REGION WASTE
        # =================================================

        region_labels = []
        region_values = []

        if (
            REGION_COL
            and MSW_COL
            and not data.empty
        ):

            temp = data.copy()

            temp["_msw"] = pd.to_numeric(
                temp[MSW_COL],
                errors="coerce"
            )

            grouped = (
                temp
                .dropna(subset=["_msw"])
                .groupby(REGION_COL)["_msw"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            region_labels = [
                str(x)
                for x in grouped.index
            ]

            region_values = [
                round(float(x), 2)
                for x in grouped.values
            ]

        # =================================================
        # TOP COUNTRIES
        # =================================================

        country_labels = []
        country_values = []

        if (
            COUNTRY_COL
            and MSW_COL
            and not data.empty
        ):

            temp = data.copy()

            temp["_msw"] = pd.to_numeric(
                temp[MSW_COL],
                errors="coerce"
            )

            grouped = (
                temp
                .dropna(subset=["_msw"])
                .groupby(COUNTRY_COL)["_msw"]
                .sum()
                .sort_values(
                    ascending=False
                )
                .head(10)
            )

            country_labels = [
                str(x)
                for x in grouped.index
            ]

            country_values = [
                round(float(x), 2)
                for x in grouped.values
            ]

        # =================================================
        # RECYCLING BY REGION
        # =================================================

        recycling_labels = []
        recycling_values = []

        if (
            REGION_COL
            and RECYCLING_COL
            and not data.empty
        ):

            temp = data.copy()

            temp["_recycling"] = pd.to_numeric(
                temp[RECYCLING_COL],
                errors="coerce"
            )

            grouped = (
                temp
                .dropna(subset=["_recycling"])
                .groupby(REGION_COL)["_recycling"]
                .mean()
                .sort_values(
                    ascending=False
                )
            )

            recycling_labels = [
                str(x)
                for x in grouped.index
            ]

            recycling_values = [
                percentage(x)
                for x in grouped.values
            ]

        # =================================================
        # SCATTER DATA
        # =================================================

        scatter = []

        if (
            COUNTRY_COL
            and MSW_COL
            and POPULATION_COL
            and not data.empty
        ):

            for _, row in data.iterrows():

                waste = pd.to_numeric(
                    row.get(MSW_COL),
                    errors="coerce"
                )

                population = pd.to_numeric(
                    row.get(POPULATION_COL),
                    errors="coerce"
                )

                if (
                    pd.notna(waste)
                    and pd.notna(population)
                ):

                    scatter.append({
                        "country": str(
                            row.get(COUNTRY_COL)
                        ),

                        "population": round(
                            float(population),
                            2
                        ),

                        "waste": round(
                            float(waste),
                            2
                        )
                    })

        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success": True,

            "kpi": {

                "countries": total_countries,

                "msw": format_number(
                    total_msw
                ),

                "recycling": format_number(
                    average_recycling
                ),

                "population": format_number(
                    total_population
                ),

                "gdp": format_number(
                    average_gdp
                ),

                "collection": format_number(
                    average_collection
                ),

                "risk_score": risk_score,

                "risk_level": risk_level,

                "recommendation": ai_recommendation,
                "sustainability": analysis["sustainability"],
                "confidence": analysis["confidence"]
            },

            "analysis": analysis,

            "data": {
                "rows": len(data),
                "countries": total_countries,
                "msw": total_msw,
                "recycling": average_recycling,
                "population": total_population,
                "gdp": average_gdp,
                "collection": average_collection,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "sustainability": analysis["sustainability"]
            },

            "charts": {

                "region_waste": {
                    "labels": region_labels,
                    "values": region_values
                },

                "top_countries": {
                    "labels": country_labels,
                    "values": country_values
                },

                "region_recycling": {
                    "labels": recycling_labels,
                    "values": recycling_values
                },

                "scatter": scatter
            }
        })

    except Exception as e:

        print("API ERROR:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/filters")
def filters_api():
    return jsonify({
        "success": True,
        "countries": get_countries(),
        "regions": get_regions(),
        "income_groups": get_income_groups(),
        "years": get_years()
    })


@app.route("/api/filter-options")
def filter_options_api():
    return filters_api()


@app.route("/api/country/<path:country>")
def country_api(country):
    if not COUNTRY_COL:
        return jsonify({"success": False, "error": "Country data unavailable"}), 404
    match = df[df[COUNTRY_COL].astype(str).str.strip().str.casefold() == country.strip().casefold()]
    if match.empty:
        return jsonify({"success": False, "error": "Country not found"}), 404
    row = match.iloc[[0]]
    analysis = analyze_environment(row)
    return jsonify({"success": True, "country": country, "analysis": analysis, "data": {
        "country": str(row.iloc[0].get(COUNTRY_COL, country)),
        "region": str(row.iloc[0].get(REGION_COL, "Unavailable")),
        "income": str(row.iloc[0].get(INCOME_COL, "Unavailable")),
        "population": value_for(row, POPULATION_COL), "gdp": value_for(row, GDP_COL),
        "msw": value_for(row, MSW_COL), "msw_pc": value_for(row, MSW_CAPITA_COL),
        "year": value_for(row, YEAR_COL)
    }})


@app.route("/api/ai-insights")
def ai_insights_api():
    return jsonify({"success": True, "analysis": analyze_environment(filtered_data())})


@app.route("/api/recommendation/<path:country>")
def recommendation_api(country):
    if not COUNTRY_COL:
        return jsonify({"success": False, "error": "Country data unavailable"}), 404
    match = df[df[COUNTRY_COL].astype(str).str.strip().str.casefold() == country.strip().casefold()]
    if match.empty:
        return jsonify({"success": False, "error": "Country not found"}), 404
    analysis = analyze_environment(match.iloc[[0]])
    return jsonify({"success": True, "country": country, "score": analysis["score"], "risk": analysis["level"], "summary": analysis["diagnosis"], "actions": [analysis["priority"]] + analysis["implementation"]})


@app.route("/api/compare")
def compare_api():
    names = [request.args.get("country_a", ""), request.args.get("country_b", "")]
    result = []
    for name in names:
        match = df[df[COUNTRY_COL].astype(str).str.strip().str.casefold() == name.strip().casefold()] if COUNTRY_COL else pd.DataFrame()
        if not match.empty:
            result.append({"country": name, "analysis": analyze_environment(match.iloc[[0]])})
    return jsonify({"success": True, "countries": result})


# =========================================================
# COUNTRIES API
# =========================================================

@app.route("/api/countries")
def countries_api():

    return jsonify({
        "countries": get_countries()
    })


@app.route("/countries")
def countries_page():
    rows = []
    if COUNTRY_COL:
        for _, row in df.iterrows():
            record = df.loc[[row.name]]
            analysis = analyze_environment(record)
            rows.append({
                "country": str(row.get(COUNTRY_COL, "Unknown")),
                "region": str(row.get(REGION_COL, "Unavailable")),
                "income": str(row.get(INCOME_COL, "Unavailable")),
                "waste": value_for(record, MSW_COL),
                "recycling": analysis["metrics"]["recycling"],
                "risk": analysis["score"],
                "risk_level": analysis["level"],
                "sustainability": analysis["sustainability"]
            })
    rows.sort(key=lambda item: item["risk"], reverse=True)
    return render_template("countries_advanced.html", countries=rows)


# =========================================================
# REGIONS API
# =========================================================

@app.route("/regions")
def regions_api():

    return jsonify({
        "regions": get_regions()
    })


# =========================================================
# INCOME GROUP API
# =========================================================

@app.route("/income-groups")
def income_groups_api():

    return jsonify({
        "income_groups": get_income_groups()
    })


# =========================================================
# YEARS API
# =========================================================

@app.route("/years")
def years_api():

    return jsonify({
        "years": get_years()
    })


# =========================================================
# DASHBOARD PAGE
# =========================================================

@app.route("/overview", endpoint="index")
def overview_page():
    return render_template("ecovision.html", countries=get_countries(), regions=get_regions(), income_groups=get_income_groups(), years=get_years())


@app.route("/insights")
def insights():
    return render_template("insights.html", countries=get_countries(), selected_country=request.args.get("country", "All Countries"), risk_score=0, risk_level="Unavailable", waste_rate=0, waste_status="Dataset view", waste_message="Use the overview filters for live analysis.", recycling_rate=0, recycling_status="Dataset view", recycling_message="Use the overview filters for live analysis.", ai_summary="Select a country in the overview to generate a personalized diagnosis.")


@app.route("/recommendation", endpoint="recommendation")
def recommendation_page():
    return render_template("recommendation.html", countries=get_countries(), selected_country=request.args.get("country", "All Countries"), recommendations=[], country_data={})


@app.route("/analytics")
def analytics():
    return render_template("ecovision.html", countries=get_countries(), regions=get_regions(), income_groups=get_income_groups(), years=get_years())


@app.route("/about")
def about():
    return render_template("about_advanced.html", dataset_rows=len(df), dataset_columns=len(df.columns))


@app.route("/contact")
def contact():
    return render_template("contact.html", countries=get_countries(), selected_country=request.args.get("country", "All Countries"))

@app.route("/dashboard")
def dashboard():

    return render_template(
        "ecovision.html",
        countries=get_countries(),
        regions=get_regions(),
        income_groups=get_income_groups(),
        years=get_years()
    )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "ecovision.html",
        countries=get_countries(),
        regions=get_regions(),
        income_groups=get_income_groups(),
        years=get_years()
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "running",

        "dataset_loaded": not df.empty,

        "rows": len(df),

        "columns": len(df.columns)

    })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("                    ECOVISION AI")
    print("=" * 70)

    print(
        "Dashboard : "
        "http://127.0.0.1:5000/"
    )

    print(
        "Dashboard : "
        "http://127.0.0.1:5000/dashboard"
    )

    print(
        "API       : "
        "http://127.0.0.1:5000/api/dashboard"
    )

    print(
        "Health    : "
        "http://127.0.0.1:5000/health"
    )

    print("=" * 70)
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )