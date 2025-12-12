
const urlParams = new URLSearchParams(window.location.search || "");
const editingId = urlParams.get("id");

$(function () {
    const $items = $("#itemsInOrder");
    const $template = $("#rowTemplate .product-item").clone();
    const $grandTotal = $("#product_grand_total");

    let products = [];

    // Load products (returns Promise)
    function loadProducts() {
        return apiGet("/getProducts")
            .then(list => {
                products = list || [];
                return products;
            });
    }

    // Creating a new row for selecting product
    function createRow() {
        const $row = $template.clone();

        const $select = $row.find(".cart-product");
        $select.empty();
        $select.append("<option value=\"\">--Select--</option>");

        products.forEach(p => {
            $select.append(`
                <option data-price="${p.price_per_unit}" value="${p.product_id}">
                   ${p.name} (${p.uom_name})
                </option>
            `);
        });

        // Handlers
        $select.on("change", () => updateRow($row));
        $row.find(".product-qty").on("input", () => updateRow($row));
        $row.find(".remove-row").on("click", () => {
            $row.remove();
            updateGrandTotal();
        });

        return $row;
    }

    // Update row total
    function updateRow($row) {
        const price = parseFloat($row.find("option:selected").data("price") || 0);
        const qty = parseFloat($row.find(".product-qty").val() || 0);

        const total = qty * price;

        $row.find(".product-price").val(price.toFixed(2));
        $row.find(".product-total").val(total.toFixed(2));

        updateGrandTotal();
    }

    // Update grand total
    function updateGrandTotal() {
        let sum = 0;
        $items.find(".product-item").each(function () {
            sum += parseFloat($(this).find(".product-total").val() || 0);
        });
        $grandTotal.val(sum.toFixed(2));
    }

    // Add new row
    $("#addMoreButton").click(function (e) {
        e.preventDefault();
        $items.append(createRow());
    });

    // Save order (create or edit)
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

            if (!pid || !qty || qty <= 0) return;

            details.push({
                product_id: parseInt(pid),
                quantity: qty,
                total_price: total
            });
        });

        if (details.length === 0) {
            return toast("Add at least one item");
        }

        const payload = {
            order_id: editingId ? parseInt(editingId) : null,
            customer_name,
            total_price: parseFloat($grandTotal.val()),
            datetime: new Date().toISOString().slice(0, 19).replace("T", " "),
            order_details: details
        };

        // Prefer existing apiPost helper (common.js). If missing, fallback to fetch.
        if (typeof apiPost === "function") {
            apiPost("/addOrder", payload)
                .then(resp => {
                    toast("Order saved!");
                    window.location.href = "index.html";
                })
                .catch(err => {
                    console.error(err);
                    toast("Failed to save order");
                });
            return;
        }

        // Send as form-encoded 'data' key 
        const fd = new FormData();
        fd.append("data", JSON.stringify(payload));

        fetch("/addOrder", { method: "POST", body: fd })
            .then(r => r.json())
            .then(resp => {
                if (resp && resp.order_id) {
                    toast("Order saved!");
                    window.location.href = "index.html";
                } else {
                    console.error("Unexpected response:", resp);
                    toast("Failed to save order");
                }
            })
            .catch(err => {
                console.error(err);
                toast("Failed to save order");
            });
    });

    // Load order for editing
    function loadExistingOrder(orderId) {
        return apiGet("/getOrder/${orderId}")
            .then(order => {
                if (!order) throw new Error("Order not found");

                $("#customerName").val(order.customer_name || "");

                $items.empty();
                if (order.items && order.items.length) {
                    order.items.forEach(item => {
                        const $row = createRow();

                        // Set product, quantity, price, total
                        $row.find(".cart-product").val(item.product_id);
                        // If product price not sent from server, derive from item_total/quantity
                        const unitPrice = item.unit_price || (item.quantity ? (item.item_total / item.quantity) : 0);
                        $row.find(".product-price").val(parseFloat(unitPrice).toFixed(2));
                        $row.find(".product-qty").val(item.quantity);
                        $row.find(".product-total").val(parseFloat(item.item_total).toFixed(2));

                        // Append and ensure event handlers recalculate properly
                        $items.append($row);
                        updateRow($row);
                    });
                } else {
                    $items.append(createRow());
                }

                $grandTotal.val((order.total_price || 0).toFixed(2));
            });
    }

    // Get products first, then decide edit/create
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
