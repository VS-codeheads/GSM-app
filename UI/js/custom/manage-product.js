let editingProductId = null;

$(function () {

    const $tbody = $("table tbody");

    loadUOMs().then(loadProducts);

    // -------------------------------
    // Load Units
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
    // Load Products Into Table
    // -------------------------------
    function loadProducts() {
        apiGet("/getProducts").then(products => {
            $tbody.empty();

            products.forEach(p => {
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
        });
    }

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

            const modal = new bootstrap.Modal(document.getElementById("productModal"));
            modal.show();
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
                const modalEl = document.getElementById("productModal");
                const modal = bootstrap.Modal.getInstance(modalEl);
                modal.hide();

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
