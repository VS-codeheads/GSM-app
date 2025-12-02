
$(function () {
    const $items = $("#itemsInOrder");
    const $template = $(".product-box .product-item").clone();
    const $grandTotal = $("#product_grand_total");

    let products = [];

    // Load products
    function loadProducts() {
        return apiGet("/getProducts")
            .then(list => {
                products = list;
                return list;
            });
    }

    // Create a new row for selecting product
    function createRow() {
        const $row = $template.clone();

        const $select = $row.find(".cart-product");
        $select.empty();
        $select.append(`<option value="">--Select--</option>`);

        products.forEach(p => {
            $select.append(`
                <option data-price="${p.price_per_unit}" value="${p.product_id}">
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
    $("#addMoreButton").click(function () {
        $items.append(createRow());
    });

    // Save order
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

            if (!pid || qty <= 0) return;

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
            customer_name,
            grand_total: parseFloat($grandTotal.val()),
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

    // Initial load: add first row
    loadProducts().then(() => $items.append(createRow()));
});
