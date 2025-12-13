

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

let editingProductId = null;
let cachedProducts = [];

$(function () {

    const $tbody = $("table tbody");

    loadUOMs().then(loadProducts);

    // -------------------------------
    // Load Units (UOM)
    // -------------------------------
    function loadUOMs() {
        return apiGet("/getUOM").then(uoms => {
            const $uoms = $("#uoms");
            $uoms.empty();
            uoms.forEach(u => {
                $uoms.append(`<option value="${u.uom_id}">${u.uom_name}</option>`);
            });
        });
    }

    // -------------------------------
    // Render Products
    // -------------------------------
    function renderProducts(list) {
        $tbody.empty();

        list.forEach(p => {
            $tbody.append(`
                <tr>
                    <td>${p.name}</td>
                    <td>${p.uom_name}</td>
                    <td>${p.price_per_unit.toFixed(2)}</td>
                    <td>${p.quantity}</td>
                    <td>
                        <button class="btn btn-warning btn-sm edit-btn" data-id="${p.product_id}">Edit</button>
                        <button class="btn btn-danger btn-sm delete-btn" data-id="${p.product_id}">Delete</button>
                    </td>
                </tr>
            `);
        });
    }

    // -------------------------------
    // Load Products
    // -------------------------------
    function loadProducts() {
        apiGet("/getProducts").then(products => {
            cachedProducts = products;
            renderProducts(products);
        });
    }

    // -------------------------------
    // SEARCH BAR
    // -------------------------------
    $("#productSearch").on("input", function () {
        const q = $(this).val().toLowerCase();

        const filtered = cachedProducts.filter(p =>
            p.name.toLowerCase().includes(q) ||
            p.uom_name.toLowerCase().includes(q) ||
            String(p.price_per_unit).includes(q) ||
            String(p.quantity).includes(q)
        );

        renderProducts(filtered);
    });

    // -------------------------------
    // OPEN EDIT MODAL
    // -------------------------------
    $(document).on("click", ".edit-btn", function () {
        editingProductId = $(this).data("id");

        apiGet("/getProducts").then(products => {
            const product = products.find(p => p.product_id == editingProductId);

            $("#name").val(product.name);
            $("#price").val(product.price_per_unit);
            $("#uoms").val(product.uom_id);
            $("#qty").val(product.quantity);

            $(".modal-title").text("Edit Product");
            $("#saveProduct").text("Update");

            new bootstrap.Modal("#productModal").show();
        });
    });

    // -------------------------------
    // SAVE PRODUCT (ADD or EDIT)
    // -------------------------------
    $("#saveProduct").click(function () {

        const payload = {
            product_id: editingProductId,
            name: $("#name").val(),
            uom_id: $("#uoms").val(),
            price_per_unit: parseFloat($("#price").val()),
            quantity: parseInt($("#qty").val())
        };

        if (!payload.name || !payload.price_per_unit || isNaN(payload.quantity)) {
            alert("Fill all fields");
            return;
        }

        const url = editingProductId ? "/updateProduct" : "/addProduct";

        apiPost(url, payload)
            .then(() => {
                bootstrap.Modal.getInstance("#productModal").hide();
                editingProductId = null;
                loadProducts();
            })
            .catch(err => console.error(err));
    });

    // -------------------------------
    // DELETE PRODUCT
    // -------------------------------
    $(document).on("click", ".delete-btn", function () {
        const id = $(this).data("id");

        if (!confirm("Delete this product?")) return;

        apiDelete(`/deleteProduct/${id}`)
            .then(() => loadProducts())
            .catch(err => console.error(err));
    });
});
