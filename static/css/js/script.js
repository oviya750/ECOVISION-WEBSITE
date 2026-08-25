const $ = (selector) =>
    document.querySelector(selector);


// ======================================================
// FORMAT NUMBER
// ======================================================

function formatNumber(value, decimals = 0) {

    if (
        value === null ||
        value === undefined ||
        Number.isNaN(Number(value))
    ) {
        return "—";
    }

    return Number(value).toLocaleString(
        "en-IN",
        {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }
    );
}


// ======================================================
// COMPACT NUMBER
// ======================================================

function formatCompact(value) {

    if (
        value === null ||
        value === undefined ||
        Number.isNaN(Number(value))
    ) {
        return "—";
    }

    const number = Number(value);

    const absolute = Math.abs(number);

    if (absolute >= 1e12) {
        return (
            number / 1e12
        ).toFixed(2) + "T";
    }

    if (absolute >= 1e9) {
        return (
            number / 1e9
        ).toFixed(2) + "B";
    }

    if (absolute >= 1e6) {
        return (
            number / 1e6
        ).toFixed(2) + "M";
    }

    if (absolute >= 1e3) {
        return (
            number / 1e3
        ).toFixed(2) + "K";
    }

    return formatNumber(number);
}


// ======================================================
// SET TEXT
// ======================================================

function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {

        element.textContent =
            value;

    }
}


// ======================================================
// API
// ======================================================

async function getJSON(url) {

    const response =
        await fetch(url);

    const data =
        await response.json();

    if (
        !response.ok ||
        data.ok === false
    ) {

        throw new Error(
            data.error ||
            "Unable to load data"
        );

    }

    return data;
}


// ======================================================
// COUNTRY PAGE
// ======================================================

async function loadCountryPage() {

    const select =
        $("#countrySelect");

    if (!select) return;


    try {

        const filters =
            await getJSON(
                "/api/filters"
            );


        select.innerHTML = "";


        filters.countries
            .forEach(country => {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    country;

                option.textContent =
                    country;

                select.appendChild(
                    option
                );

            });


        if (
            filters.countries.length
        ) {

            if (
                filters.countries
                    .includes("Algeria")
            ) {

                select.value =
                    "Algeria";

            } else {

                select.value =
                    filters.countries[0];

            }

            await updateCountry();

        }


    } catch (error) {

        select.innerHTML =
            "<option>Unable to load countries</option>";

        const errorBox =
            $("#countryError");

        if (errorBox) {

            errorBox.textContent =
                error.message;

            errorBox.hidden =
                false;

        }

    }


    select.addEventListener(
        "change",
        updateCountry
    );
}


// ======================================================
// COUNTRY UPDATE
// ======================================================

async function updateCountry() {

    const select =
        $("#countrySelect");

    if (
        !select ||
        !select.value
    ) return;


    const loading =
        $("#countryLoading");

    if (loading) {

        loading.hidden =
            false;

    }


    try {

        const result =
            await getJSON(
                "/api/country/" +
                encodeURIComponent(
                    select.value
                )
            );


        const data =
            result.data;


        setText(
            "countryName",
            data.country
        );


        setText(
            "countryRegion",
            "Region: " +
            data.region
        );


        setText(
            "countryIncome",
            "Income: " +
            data.income_group
        );


        setText(
            "countryStatus",
            "Live data from your Excel dataset"
        );


        // MSW

        setText(
            "countryMSW",

            data.msw === null
                ? "—"
                : formatCompact(
                    data.msw
                )
        );


        // RECYCLING

        setText(
            "countryRecycling",

            data.recycling === null
                ? "—"
                :
                (
                    data.recycling * 100
                ).toFixed(1) + "%"
        );


        // POPULATION

        setText(
            "countryPopulation",

            data.population === null
                ? "—"
                :
                formatNumber(
                    data.population
                )
        );


        // GDP

        setText(
            "countryGDP",

            data.gdp === null
                ? "—"
                :
                formatCompact(
                    data.gdp
                )
        );


        // RISK SCORE

        setText(
            "riskScore",

            data.score.toFixed(1)
            +
            " / 100"
        );


        setText(
            "riskLevel",
            data.level
        );


        const level =
            $("#riskLevel");


        if (level) {

            level.className =
                "risk-level " +
                (
                    data.tone === "high"
                        ? "risk-high"

                        : data.tone === "medium"
                            ? "risk-medium"

                            : "risk-low"
                );

        }


        // PROGRESS BAR

        const bar =
            $("#riskBar");

        if (bar) {

            bar.style.width =
                Math.max(
                    0,
                    Math.min(
                        100,
                        data.score
                    )
                ) + "%";

        }


        // WHY RISK

        const reasons =
            $("#riskReasons");


        if (reasons) {

            reasons.innerHTML =
                data.reasons
                    .map(
                        reason =>
                            `<li>
                                <span>⚠</span>
                                ${reason}
                            </li>`
                    )
                    .join("");

        }


        // IMPROVEMENTS

        const improvements =
            $("#improvements");


        if (improvements) {

            improvements.innerHTML =
                data.improvements
                    .map(
                        item =>
                            `<li>
                                <span>✓</span>
                                ${item}
                            </li>`
                    )
                    .join("");

        }


    } catch (error) {

        const errorBox =
            $("#countryError");

        if (errorBox) {

            errorBox.textContent =
                error.message;

            errorBox.hidden =
                false;

        }

    } finally {

        if (loading) {

            loading.hidden =
                true;

        }

    }
}


// ======================================================
// DASHBOARD
// ======================================================

async function loadDashboard() {

    const country =
        $("#dashCountry");

    const region =
        $("#dashRegion");

    const income =
        $("#dashIncome");


    if (
        !country ||
        !region ||
        !income
    ) return;


    try {

        const filters =
            await getJSON(
                "/api/filters"
            );


        function fill(
            select,
            values,
            label
        ) {

            select.innerHTML =
                `<option value="All">
                    ${label}
                </option>`;


            values.forEach(
                value => {

                    const option =
                        document.createElement(
                            "option"
                        );

                    option.value =
                        value;

                    option.textContent =
                        value;

                    select.appendChild(
                        option
                    );

                }
            );

        }


        fill(
            country,
            filters.countries,
            "All Countries"
        );


        fill(
            region,
            filters.regions,
            "All Regions"
        );


        fill(
            income,
            filters.income_groups,
            "All Income Groups"
        );


        async function refresh() {

            const params =
                new URLSearchParams({

                    country:
                        country.value,

                    region:
                        region.value,

                    income:
                        income.value

                });


            try {

                const data =
                    await getJSON(
                        "/api/data?" +
                        params.toString()
                    );


                setText(
                    "dashCountries",
                    formatNumber(
                        data.countries
                    )
                );


                setText(
                    "dashMSW",

                    data.msw === null
                        ? "—"
                        :
                        formatCompact(
                            data.msw
                        )
                );


                setText(
                    "dashRecycling",

                    data.recycling === null
                        ? "—"
                        :
                        (
                            data.recycling * 100
                        ).toFixed(1)
                        + "%"
                );


                setText(
                    "dashPopulation",

                    data.population === null
                        ? "—"
                        :
                        formatNumber(
                            data.population
                        )
                );


                setText(
                    "dashGDP",

                    data.gdp === null
                        ? "—"
                        :
                        formatCompact(
                            data.gdp
                        )
                );


                setText(
                    "dashRows",
                    formatNumber(
                        data.rows
                    )
                );


            } catch (error) {

                const errorBox =
                    $("#dashError");

                if (errorBox) {

                    errorBox.style.display =
                        "block";

                    errorBox.textContent =
                        error.message;

                }

            }

        }


        country.addEventListener(
            "change",
            refresh
        );

        region.addEventListener(
            "change",
            refresh
        );

        income.addEventListener(
            "change",
            refresh
        );


        await refresh();

    } catch (error) {

        setText(
            "dashError",
            error.message
        );

    }
}


// ======================================================
// AI CHARACTER
// ======================================================

function initAI() {

    const character =
        $("#aiCharacter");

    const bubble =
        $("#aiBubble");


    if (
        !character ||
        !bubble
    ) return;


    character.addEventListener(
        "click",
        () => {

            bubble.classList.toggle(
                "show"
            );

        }
    );

}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadCountryPage();

        loadDashboard();

        initAI();

    }
);