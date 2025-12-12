// ------------------------
// WEATHER WIDGET
// ------------------------
function loadWeather() {
    const API_KEY = "6b4b1400888cfc29ec5a3d7dd73be8d6";
    const CITY = "Copenhagen";
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${CITY}&units=metric&appid=${API_KEY}`;

    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (data.cod !== 200) {
                $("#weatherContent").html("Failed to load weather.");
                return;
            }

            const temp = data.main.temp;
            const cond = data.weather[0].description;
            const icon = data.weather[0].icon;

            $("#weatherContent").html(`
                <div class="d-flex align-items-center">
                    <img src="https://openweathermap.org/img/wn/${icon}@2x.png" />
                    <div class="ms-3">
                        <h5 class="m-0">${CITY}</h5>
                        <div>${temp}°C – ${cond}</div>
                    </div>
                </div>
            `);
        })
        .catch(() => {
            $("#weatherContent").html("Weather unavailable.");
        });
}

function getProfitClass(profit) {
    if (profit > 0) return "text-success fw-bold";   // green
    if (profit < 0) return "text-danger fw-bold";   // red
    return "text-muted";                            // grey
}

let showingAll = false;
let cachedOrders = [];

// ------------------------
// RENDER ORDERS
// ------------------------
function renderOrders(orders) {
    const $tbody = $("#ordersTableBody");
    $tbody.empty();

    if (!orders || orders.length === 0) {
        $tbody.append(`
            <tr>
                <td colspan="4" class="text-center text-muted py-3">No orders yet.</td>
            </tr>
        `);
        return;
    }

    orders.forEach(o => {
        const date = new Date(o.datetime).toLocaleString();
        $tbody.append(`
            <tr data-id="${o.order_id}" class="order-row" style="cursor:pointer;">
                <td>${date}</td>
                <td>${o.order_id}</td>
                <td>${o.customer_name}</td>
                <td>${(o.total_price || 0).toFixed(2)}</td>
            </tr>
        `);
    });
}


// ------------------------
// LOAD ORDERS
// ------------------------
function loadRecentOrders() {
    apiGet("/getRecentOrders")
        .then(orders => {
            cachedOrders = orders;
            renderOrders(cachedOrders);
        });
}

function loadAllOrders() {
    apiGet("/getOrders")
        .then(orders => {
            cachedOrders = orders;
            renderOrders(cachedOrders);
        });
}

function renderSimulationResult(data) {
    if (!data) return;

    const summary = data.summary;
    const details = data.details;

    let html = `
        <div class="card p-3 mb-3 bg-light">
            <h5>Summary</h5>
            <div class="row">
                <div class="col"><b>Total Revenue:</b> ${summary.total_revenue}</div>
                <div class="col"><b>Total Cost:</b> ${summary.total_cost}</div>
            </div>
            <div class="row">
                <div class="col"><b>Total Profit:</b> ${summary.total_profit}</div>
                <div class="col"><b>Profit Margin:</b> ${summary.profit_margin_percent}%</div>
            </div>
            <div class="row">
                <div class="col"><b>Total Units Sold:</b> ${summary.total_units_sold}</div>
            </div>
        </div>
    `;

    // DETAILS TABLE
    html += `
        <h5>Breakdown By Product</h5>
        <table class="table table-bordered table-sm">
            <thead class="table-secondary">
                <tr>
                    <th>Product</th>
                    <th>Initial Stock</th>
                    <th>Sold</th>
                    <th>Remaining</th>
                    <th>Revenue</th>
                    <th>Profit</th>
                </tr>
            </thead>
            <tbody>
    `;

    details.forEach(row => {
        html += `
            <tr>
                <td>${row.product}</td>
                <td>${row.initial_stock}</td>
                <td>${row.sold_units}</td>
                <td>${row.remaining_stock}</td>
                <td>${row.revenue}</td>
                <td class="${getProfitClass(row.profit)}">${row.profit}</td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    $("#sim-result").html(html);
}


// ------------------------
// PAGE INITIALIZATION
// ------------------------
$(function () {

    loadRecentOrders();
    loadWeather();

    // --- TOGGLE BUTTON LOGIC ---
    $("#toggleOrdersBtn").click(function () {
        if (showingAll) {
            loadRecentOrders();
            $(this).text("Show All Orders");
            showingAll = false;
        } else {
            loadAllOrders();
            $(this).text("Show Recent Orders");
            showingAll = true;
        }
    });

    // --- LIVE SEARCH ---
    $("#orderSearch").on("input", function () {
        const q = $(this).val().toLowerCase();

        const filtered = cachedOrders.filter(o =>
            o.customer_name.toLowerCase().includes(q) ||
            String(o.order_id).includes(q) ||
            new Date(o.datetime).toLocaleString().toLowerCase().includes(q)
        );

        renderOrders(filtered);
    });

    // ----------------------------------------
    // REVENUE SIMULATION MODAL LOGIC
    // ----------------------------------------

    $("#revenueModal").on("shown.bs.modal", function () {
        console.log("Loading products for simulation...");

        fetch("http://127.0.0.1:5000/getProducts")
            .then(res => res.json())
            .then(products => {
                const select = document.getElementById("sim-products");
                select.innerHTML = "";

                products.forEach(p => {
                    const opt = document.createElement("option");
                    opt.value = p.product_id;
                    opt.textContent = p.name;
                    select.appendChild(opt);
                });
            });
    });

    $("#run-simulation").on("click", function () {
        const select = document.getElementById("sim-products");
        const days = parseInt(document.getElementById("sim-days").value);

        const productIds = Array.from(select.selectedOptions)
            .map(opt => parseInt(opt.value));

        if (productIds.length === 0) {
            alert("Please select at least one product.");
            return;
        }

        fetch("http://127.0.0.1:5000/api/calc/revenue", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                product_ids: productIds,
                days: days,
                seed: 123
            })
        })
            .then(res => res.json())
            .then(data => {
                renderSimulationResult(data);
            })
            .catch(err => {
                console.error("Simulation failed:", err);
                alert("Simulation failed. See console.");
            });
    });

    $("#revenueModal").on("hidden.bs.modal", function () {
        const el = document.getElementById("sim-result");
        if (el) el.blur();
    });

}); 


// ------------------------
// ORDER ROW CLICK HANDLER
// ------------------------
$(document).on("click", ".order-row", function () {
    const orderId = $(this).data("id");

    apiGet(`/getOrderDetails/${orderId}`)
        .then(items => {
            if (!items || items.length === 0) {
                $("#detailsContent").html("<p>No details found.</p>");
                return;
            }

            let html = `
                <h5>Order #${items[0].order_id}</h5>
                <p><b>Customer:</b> ${items[0].customer_name}</p>
                <p><b>Total:</b> ${items[0].total_price.toFixed(2)}</p>
                <hr>
                <table class="table table-sm table-bordered">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Qty</th>
                            <th>Unit</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            items.forEach(i => {
                html += `
                    <tr>
                        <td>${i.product_name}</td>
                        <td>${i.quantity}</td>
                        <td>${i.uom_name}</td>
                        <td>${i.item_total.toFixed(2)}</td>
                    </tr>
                `;
            });

            html += "</tbody></table>";
            $("#detailsContent").html(html);

            new bootstrap.Modal("#orderDetailsModal").show();
        });
});
