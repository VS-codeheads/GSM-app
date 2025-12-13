

// -------------------------------
// API HELPERS
// -------------------------------
function apiGet(path) {
    return fetch(`${window.API_BASE}${path}`).then(res => res.json());
}

function apiPost(path, body) {
    return fetch(`${window.API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    }).then(res => res.json());
}

function apiDelete(path) {
    return fetch(`${window.API_BASE}${path}`, { method: "DELETE" })
        .then(res => res.json());
}

const urlParams = new URLSearchParams(window.location.search || "");
const editingId = urlParams.get("id");

$(function () {

    const $items = $("#itemsInOrder");
    const $template = $("#rowTemplate .product-item").clone();
    const $grandTotal = $("#product_grand_total");

    let products = [];

    // ----------------------------------------
    // LOAD PRODUCTS
    // ----------------------------------------
    function loadProducts() {
        return apiGet("/getProducts")
            .then(list => {
                products = list || [];
                return products;
            });
    }

    // ----------------------------------------
    // CREATE A PRODUCT ROW
    // ----------------------------------------
    function createRow() {
        const $row = $template.clone();

        const $select = $row.find(".cart-product");
        $select.empty();
        $select.append("<option value=\"\">--Select--</option>");

        products.forEach(p => {
            $select.append(`
                <option value="${p.product_id}" data-price="${p.price_per_unit}">
                    ${p.name} (${p.uom_name})
                </option>
            `);
        });

        $select.on("change", () => updateRow($row));
        $row.find(".product-qty").on("input", () => updateRow($row));
        $row.find(".remove-row").on("click", () => {
            $row.remove();
            updateGrandTotal();
        });

        return $row;
    }

    // ----------------------------------------
    // UPDATE ROW TOTAL
    // ----------------------------------------
    function updateRow($row) {
        const price = parseFloat($row.find("option:selected").data("price") || 0);
        const qty = parseFloat($row.find(".product-qty").val() || 0);

        const total = qty * price;

        $row.find(".product-price").val(price.toFixed(2));
        $row.find(".product-total").val(total.toFixed(2));

        updateGrandTotal();
    }

    // ----------------------------------------
    // UPDATE GRAND TOTAL
    // ----------------------------------------
    function updateGrandTotal() {
        let sum = 0;

        $items.find(".product-item").each(function () {
            sum += parseFloat($(this).find(".product-total").val() || 0);
        });

        $grandTotal.val(sum.toFixed(2));
    }

    // ----------------------------------------
    // ADD NEW ROW
    // ----------------------------------------
    $("#addMoreButton").click(function (e) {
        e.preventDefault();
        $items.append(createRow());
    });

    // ----------------------------------------
    // SAVE ORDER
    // ----------------------------------------
    $("#saveOrder").click(function () {

        const customer_name = $("#customerName").val().trim();

        if (!customer_name) {
            return toast("Enter customer name");
        }

        const details = [];

        $items.find(".product-item").each(function () {

            const pid = $(this).find(".cart-product").val();
            const qty = parseFloat($(this).find(".product-qty").val());
            const total = parseFloat($(this).find(".product-total").val());

            if (!pid || qty <= 0 || isNaN(qty)) return;

            details.push({
                product_id: parseInt(pid),
                quantity: qty,
                total_price: total
            });
        });

        if (details.length === 0) {
            return toast("Add at least one valid item");
        }

        const payload = {
            order_id: editingId ? parseInt(editingId) : null,
            customer_name,
            total_price: parseFloat($grandTotal.val()),
            datetime: new Date().toISOString().slice(0, 19).replace("T", " "),
            order_details: details
        };

        apiPost("/addOrder", payload)
            .then(resp => {
                toast("Order saved!");
                window.location.href = "index.html";
            })
            .catch(err => {
                console.error(err);
                toast("Failed to save order");
            });
    });

    // ----------------------------------------
    // LOAD EXISTING ORDER 
    // ----------------------------------------
    function loadExistingOrder(orderId) {
        return apiGet(`/getOrder/${orderId}`)
            .then(order => {

                if (!order) throw new Error("Order not found");

                $("#customerName").val(order.customer_name || "");

                $items.empty();

                if (order.items && order.items.length) {
                    order.items.forEach(item => {
                        const $row = createRow();

                        // Set selected product
                        $row.find(".cart-product").val(item.product_id);

                        // Derive unit price if backend didn’t provide it
                        const unitPrice = item.unit_price
                            || (item.quantity > 0 ? item.item_total / item.quantity : 0);

                        $row.find(".product-price").val(unitPrice.toFixed(2));
                        $row.find(".product-qty").val(item.quantity);
                        $row.find(".product-total").val(parseFloat(item.item_total).toFixed(2));

                        $items.append($row);
                        updateRow($row);
                    });
                } else {
                    $items.append(createRow());
                }

                $grandTotal.val((order.total_price || 0).toFixed(2));
            });
    }

    // ----------------------------------------
    // INITIAL PAGE LOAD
    // ----------------------------------------
    loadProducts()
        .then(() => {
            if (editingId) {
                return loadExistingOrder(editingId);
            } else {
                $items.append(createRow());
            }
        })
        .catch(err => {
            console.error("Failed to load products:", err);
            toast("Failed to load products");
        });

});
