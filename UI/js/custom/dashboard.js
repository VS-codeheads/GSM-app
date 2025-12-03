
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



$(function () {
    const $tbody = $("#ordersTableBody");

    function loadOrders() {
        apiGet("/getOrders")
            .then(orders => {
                $tbody.empty();

                if (!orders || orders.length === 0) {
                    $tbody.append(`
                        <tr>
                            <td colspan="4" class="text-center text-muted py-3">
                                No orders yet.
                            </td>
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
            })
            .catch(err => {
                console.error("Failed to load orders:", err);
                $tbody.html(`<tr><td colspan="4" class="text-danger">Failed to load orders.</td></tr>`);
            });
    }

    loadOrders();
    loadWeather();

    // Click an order row which opens details modal
    $(document).on("click", ".order-row", function () {
        const orderId = $(this).data("id");

        apiGet(`/getOrderDetails/${orderId}`)
            .then(items => {
                if (!items || items.length === 0) {
                    $("#detailsContent").html("<p>No details found for this order.</p>");
                } else {
                    let html = `
                        <h5>Order #${items[0].order_id}</h5>
                        <p><b>Customer:</b> ${items[0].customer_name || ""}</p>
                        <p><b>Total:</b> ${(items[0].total_price || 0).toFixed(2)}</p>
                        <hr>
                        <div class="table-responsive">
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
                                <td>${(i.item_total || 0).toFixed(2)}</td>
                            </tr>
                        `;
                    });

                    html += `</tbody></table></div>`;
                    $("#detailsContent").html(html);
                }

                // connecting the buttons
                $("#deleteOrderBtn").off("click").on("click", function () {
                    if (!confirm("Delete this order?")) return;
                    apiDelete(`/deleteOrder/${orderId}`)
                        .then(() => {
                            toast("Order deleted");
                            const modalEl = document.getElementById("orderDetailsModal");
                            const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
                            modal.hide();
                            loadOrders();
                        })
                        .catch(err => {
                            console.error(err);
                            toast("Failed to delete");
                        });
                });

                $("#editOrderBtn").off("click").on("click", function () {
                    // navigate to order page with id to editing
                    window.location.href = `order.html?id=${orderId}`;
                });

                // show modal
                const modalEl = document.getElementById("orderDetailsModal");
                const modal = new bootstrap.Modal(modalEl);
                modal.show();
            })
            .catch(err => {
                console.error("Failed fetching order details:", err);
                toast("Failed to load order details");
            });
    });
});
