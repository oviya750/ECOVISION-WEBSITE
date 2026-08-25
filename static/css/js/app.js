const $ = (selector) =>
    document.querySelector(selector);

const $$ = (selector) =>
    [...document.querySelectorAll(selector)];


/* =========================================================
   API
========================================================= */

async function getJSON(url) {

    const response =
        await fetch(url);

    const data =
        await response.json();

    if (
        !response.ok ||
        data.success === false
    ) {

        throw new Error(
            data.message ||
            "Request failed"
        );

    }

    return data;
}


/* =========================================================
   FORMATTERS
========================================================= */

const fmt = (
    value,
    decimals = 0
) => {

    const number =
        Number(value);

    if (
        !Number.isFinite(number)
    ) {

        return "—";

    }

    return number.toLocaleString(
        "en-US",
        {
            maximumFractionDigits:
                decimals
        }
    );
};


const compact = (value) => {

    const number =
        Number(value) || 0;

    if (
        Math.abs(number) >=
        1000000000
    ) {

        return (
            number / 1000000000
        ).toFixed(2) + " B";

    }

    if (
        Math.abs(number) >=
        1000000
    ) {

        return (
            number / 1000000
        ).toFixed(2) + " M";

    }

    if (
        Math.abs(number) >=
        1000
    ) {

        return (
            number / 1000
        ).toFixed(2) + " K";

    }

    return fmt(
        number,
        2
    );
};


const money = (value) =>
    "$" + compact(value);


const pct = (value) =>
    `${fmt(value, 1)}%`;


function setText(
    id,
    value
) {

    const element =
        document.getElementById(id);

    if (element) {

        element.textContent =
            value;

    }

}


/* =========================================================
   MOBILE NAVIGATION
========================================================= */

const menuToggle =
    $("#menuToggle");

const mainNav =
    $("#mainNav");


if (menuToggle) {

    menuToggle.addEventListener(
        "click",
        () => {

            mainNav.classList.toggle(
                "open"
            );

        }
    );

}


/* =========================================================
   SELECT
========================================================= */

function fillSelect(
    element,
    values,
    firstText = "All"
) {

    if (!element) return;

    element.innerHTML = "";

    const first =
        document.createElement(
            "option"
        );

    first.value =
        firstText === "All"
            ? "All"
            : "";

    first.textContent =
        firstText;

    element.appendChild(
        first
    );

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

            element.appendChild(
                option
            );

        }
    );

}


/* =========================================================
   DASHBOARD
========================================================= */

async function initDashboard() {

    const country =
        $("#countryFilter");

    const region =
        $("#regionFilter");

    const income =
        $("#incomeFilter");

    const year =
        $("#yearFilter");

    if (
        !country ||
        !region ||
        !income ||
        !year
    ) {

        return;

    }


    try {

        const filters =
            await getJSON(
                "/api/filters"
            );


        fillSelect(
            country,
            filters.countries
        );

        fillSelect(
            region,
            filters.regions
        );

        fillSelect(
            income,
            filters.income_groups
        );

        fillSelect(
            year,
            filters.years
        );


        async function refresh() {

            const query =
                new URLSearchParams({

                    country:
                        country.value,

                    region:
                        region.value,

                    income:
                        income.value,

                    year:
                        year.value
                });


            const response =
                await getJSON(
                    "/api/dashboard?" +
                    query.toString()
                );


            const data =
                response.data;


            setText(
                "datasetRows",
                fmt(data.rows)
            );

            setText(
                "totalCountries",
                fmt(data.countries)
            );

            setText(
                "totalMSW",
                compact(data.msw)
            );

            setText(
                "averageRecycling",
                pct(data.recycling)
            );

            setText(
                "totalPopulation",
                compact(data.population)
            );

            setText(
                "averageGDP",
                money(data.gdp)
            );


            renderBars(
                "#regionBars",
                data.top_regions
            );

            renderBars(
                "#countryBars",
                data.top_countries
            );

            renderBars(
                "#incomeBars",
                data.top_income
            );

            renderRiskTable(
                "#riskTable",
                data.risk_leaders
            );

        }


        async function dependent(
            changed
        ) {

            const query =
                new URLSearchParams({

                    country:
                        country.value,

                    region:
                        region.value,

                    income:
                        income.value
                });


            const options =
                await getJSON(
                    "/api/filter-options?" +
                    query.toString()
                );


            if (
                changed === "country" &&
                country.value !== "All"
            ) {

                if (
                    options.regions.length
                ) {

                    region.value =
                        options.regions[0];

                }

                if (
                    options.income_groups.length
                ) {

                    income.value =
                        options.income_groups[0];

                }

            }


            if (
                changed === "region" &&
                region.value !== "All"
            ) {

                fillSelect(
                    income,
                    options.income_groups
                );

            }


            await refresh();

        }


        country.addEventListener(
            "change",
            () =>
                dependent("country")
        );


        region.addEventListener(
            "change",
            () =>
                dependent("region")
        );


        income.addEventListener(
            "change",
            refresh
        );


        year.addEventListener(
            "change",
            refresh
        );


        await refresh();

    }

    catch (error) {

        console.error(
            "Dashboard:",
            error
        );

    }

}


/* =========================================================
   BAR CHARTS
========================================================= */

function renderBars(
    selector,
    items
) {

    const element =
        $(selector);

    if (!element) return;

    if (
        !items ||
        !items.length
    ) {

        element.innerHTML =
            `
            <div class="empty">
                No matching data available.
            </div>
            `;

        return;

    }


    const max =
        Math.max(
            ...items.map(
                item =>
                    Number(
                        item.value
                    ) || 0
            ),
            1
        );


    element.innerHTML =
        items.map(
            item => {

                const width =
                    Math.max(
                        4,
                        (
                            Number(
                                item.value
                            ) / max
                        ) * 100
                    );


                return `
                    <div class="bar-row">

                        <span
                            title="${item.name}"
                        >
                            ${item.name}
                        </span>

                        <div class="bar-track">

                            <div
                                class="bar-fill"
                                style="width:${width}%"
                            ></div>

                        </div>

                        <strong>
                            ${compact(
                                item.value
                            )}
                        </strong>

                    </div>
                `;

            }
        ).join("");

}


/* =========================================================
   RISK TABLE
========================================================= */

function renderRiskTable(
    selector,
    rows
) {

    const element =
        $(selector);

    if (!element) return;


    if (
        !rows ||
        !rows.length
    ) {

        element.innerHTML =
            `
            <tr>
                <td colspan="6">
                    No risk data available.
                </td>
            </tr>
            `;

        return;

    }


    element.innerHTML =
        rows.map(
            row => `

                <tr>

                    <td>
                        <a
                            href="/country/${encodeURIComponent(
                                row.country
                            )}"
                        >
                            ${row.country}
                        </a>
                    </td>

                    <td>
                        ${row.region}
                    </td>

                    <td>
                        ${pct(
                            row.recycling
                        )}
                    </td>

                    <td>
                        ${compact(
                            row.msw_pc
                        )}
                    </td>

                    <td
                        class="risk risk-${row.tone}"
                    >
                        ${row.risk_level}
                    </td>

                    <td>
                        ${fmt(
                            row.risk_score,
                            1
                        )}
                    </td>

                </tr>
            `
        ).join("");

}


/* =========================================================
   COUNTRIES PAGE
========================================================= */

async function initCountries() {

    const table =
        $("#countriesBody");

    if (!table) return;


    const country =
        $("#countryFilter");

    const region =
        $("#regionFilter");

    const income =
        $("#incomeFilter");

    const search =
        $("#countrySearch");


    const filters =
        await getJSON(
            "/api/filters"
        );


    fillSelect(
        country,
        filters.countries
    );

    fillSelect(
        region,
        filters.regions
    );

    fillSelect(
        income,
        filters.income_groups
    );


    async function load() {

        const query =
            new URLSearchParams({

                country:
                    country.value,

                region:
                    region.value,

                income:
                    income.value,

                search:
                    search
                        ? search.value
                        : ""
            });


        const response =
            await getJSON(
                "/api/countries?" +
                query.toString()
            );


        setText(
            "countryCount",
            fmt(response.total)
        );


        if (
            !response.rows.length
        ) {

            table.innerHTML =
                `
                <tr>
                    <td colspan="7">
                        No countries found.
                    </td>
                </tr>
                `;

            return;

        }


        table.innerHTML =
            response.rows
                .map(
                    row => `

                    <tr>

                        <td>

                            <a
                                href="/country/${encodeURIComponent(
                                    row.country
                                )}"
                            >

                                <strong>
                                    ${row.country}
                                </strong>

                            </a>

                            <div class="muted">
                                ${row.code}
                            </div>

                        </td>

                        <td>
                            ${row.region}
                        </td>

                        <td>
                            ${row.income}
                        </td>

                        <td>
                            ${compact(row.msw)}
                        </td>

                        <td>
                            ${pct(row.recycling)}
                        </td>

                        <td>
                            ${compact(row.population)}
                        </td>

                        <td
                            class="risk risk-${row.tone}"
                        >
                            ${row.risk_level}
                        </td>

                    </tr>
                `
                )
                .join("");

    }


    [
        country,
        region,
        income
    ].forEach(
        element => {

            element.addEventListener(
                "change",
                load
            );

        }
    );


    if (search) {

        search.addEventListener(
            "input",
            () => {

                clearTimeout(
                    window.ecoSearch
                );

                window.ecoSearch =
                    setTimeout(
                        load,
                        250
                    );

            }
        );

    }


    await load();

}


/* =========================================================
   COUNTRY DETAIL
========================================================= */

async function initCountry() {

    const page =
        $("#countryPage");

    if (!page) return;


    let countryName =
        page.dataset.country;


    if (!countryName) {

        const params =
            new URLSearchParams(
                location.search
            );

        countryName =
            params.get(
                "country"
            ) || "";

    }


    try {

        const response =
            await getJSON(
                "/api/country/" +
                encodeURIComponent(
                    countryName
                )
            );


        const data =
            response.data;


        setText(
            "countryName",
            data.country
        );

        setText(
            "countryMeta",
            `${data.region} • ${data.income}`
        );

        setText(
            "countryMSW",
            compact(data.msw)
        );

        setText(
            "countryRecycle",
            pct(data.recycling)
        );

        setText(
            "countryPop",
            compact(data.population)
        );

        setText(
            "countryGDP",
            money(data.gdp)
        );

        setText(
            "countryCollection",
            pct(data.collection)
        );

        setText(
            "countryDump",
            pct(data.open_dump)
        );

        setText(
            "countryScore",
            fmt(
                data.risk_score,
                1
            )
        );

        setText(
            "countryRisk",
            data.risk_level
        );

        setText(
            "countryEPR",
            data.epr
        );

        setText(
            "countryYear",
            fmt(data.year)
        );


        const ring =
            $("#scoreRing");


        if (ring) {

            ring.style.setProperty(
                "--score",
                `${data.risk_score * 3.6}deg`
            );

        }


        setText(
            "countrySummary",
            `${data.country} shows a ${data.risk_level.toLowerCase()} waste-pressure profile based on waste intensity and recycling performance.`
        );


        const recommendation =
            await getJSON(
                "/api/recommendation/" +
                encodeURIComponent(
                    countryName
                )
            );


        const actions =
            $("#countryActions");


        if (
            actions &&
            recommendation.actions
        ) {

            actions.innerHTML =
                recommendation.actions
                    .map(
                        item =>
                            `<li>${item}</li>`
                    )
                    .join("");

        }

    }

    catch (error) {

        console.error(
            "Country:",
            error
        );

    }

}


/* =========================================================
   INSIGHTS
========================================================= */

async function initInsights() {

    const page =
        $("#insightsPage");

    if (!page) return;


    try {

        const data =
            await getJSON(
                "/api/insights"
            );


        const overview =
            data.overview;


        setText(
            "insCountries",
            fmt(
                overview.countries
            )
        );

        setText(
            "insWaste",
            compact(
                overview.msw
            )
        );

        setText(
            "insRecycle",
            pct(
                overview.recycling
            )
        );

        setText(
            "insPopulation",
            compact(
                overview.population
            )
        );


        renderBars(
            "#insRegionBars",
            data.regional
        );


        renderBars(
            "#insWasteBars",
            data.top_waste
        );


        const body =
            $("#insRiskBody");


        if (body) {

            body.innerHTML =
                data.risk
                    .map(
                        row => `

                        <tr>

                            <td>
                                ${row.country}
                            </td>

                            <td>
                                ${row.region}
                            </td>

                            <td>
                                ${fmt(
                                    row.risk_score,
                                    1
                                )}
                            </td>

                            <td
                                class="risk risk-${row.tone}"
                            >
                                ${row.risk_level}
                            </td>

                        </tr>
                    `
                    )
                    .join("");

        }

    }

    catch (error) {

        console.error(
            "Insights:",
            error
        );

    }

}


/* =========================================================
   AI RECOMMENDATION
========================================================= */

async function initRecommendations() {

    const page =
        $("#recommendPage");

    if (!page) return;


    const select =
        $("#recommendCountry");


    if (!select) return;


    try {

        const filters =
            await getJSON(
                "/api/filters"
            );


        fillSelect(
            select,
            filters.countries,
            "Choose a country"
        );


        async function load() {

            if (
                !select.value ||
                select.value === "All"
            ) {

                return;

            }


            const response =
                await getJSON(
                    "/api/recommendation/" +
                    encodeURIComponent(
                        select.value
                    )
                );


            setText(
                "recCountry",
                response.country
            );

            setText(
                "recScore",
                fmt(
                    response.score,
                    1
                )
            );

            setText(
                "recRisk",
                response.risk
            );

            setText(
                "recSummary",
                response.summary
            );


            const list =
                $("#actionsList");


            if (list) {

                list.innerHTML =
                    response.actions
                        .map(
                            (
                                action,
                                index
                            ) => `

                            <div class="feature">

                                <div class="feature-icon">
                                    ${String(
                                        index + 1
                                    ).padStart(
                                        2,
                                        "0"
                                    )}
                                </div>

                                <div>
                                    ${action}
                                </div>

                            </div>
                        `
                        )
                        .join("");

            }

        }


        select.addEventListener(
            "change",
            load
        );

    }

    catch (error) {

        console.error(
            "Recommendations:",
            error
        );

    }

}


/* =========================================================
   START
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initDashboard()
            .catch(console.error);

        initCountries()
            .catch(console.error);

        initCountry()
            .catch(console.error);

        initInsights()
            .catch(console.error);

        initRecommendations()
            .catch(console.error);

    }
);