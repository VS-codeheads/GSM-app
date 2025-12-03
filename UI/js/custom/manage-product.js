let editingProductId = null;

$(function () {

    const $tbody = $("table tbody");

    // First load UOMs, then products
    loadUOMs().then(loadProducts);

    // Load UOM list
    function loadUOMs() {
        return apiGet("/getUOM")
            .then(uoms => {
                const $uoms = $("#uoms");
                $uoms.empty();

                uoms.forEach(u => {
                    $uoms.append(`<option value="${u.uom_id}">${u.uom_name}</option>`);
                });
            });
    }

    // Load products into table
    function loadProducts() {
        apiGet("/getProducts").then(products => {
            $tbody.empty();

            products.forEach(p => {
                $tbody.append(`
                    <tr>
                        <td>${p.name}</td>
                        <td>${p.uom_name}</td>
                        <td>${p.price_per_unit.toFixed(2)}</td>
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
    // OPEN ADD MODAL
    // -------------------------------
    $("[data-bs-target='#productModal']").on("click", function () {
        editingProductId = null;

        $("#name").val("");
        $("#price").val("");
        $("#uoms").val("");

        $(".modal-title").text("Add Product");
        $("#saveProduct").text("Save");
    });


    // -------------------------------
    // OPEN EDIT MODAL
    // -------------------------------
    $(document).on("click", ".edit-btn", function () {
        editingProductId = $(this).data("id");

        apiGet(`/getProducts`).then(products => {
            const product = products.find(p => p.product_id == editingProductId);

            $("#name").val(product.name);
            $("#price").val(product.price_per_unit);
            $("#uoms").val(product.uom_id);

            $(".modal-title").text("Edit Product");
            $("#saveProduct").text("Update");

            const modal = new bootstrap.Modal(document.getElementById("productModal"));
            modal.show();
        });
    });


    // -------------------------------
    // SAVE (ADD OR EDIT)
    // -------------------------------
    $("#saveProduct").click(function () {

        const payload = {
            product_id: editingProductId,
            name: $("#name").val(),
            uom_id: $("#uoms").val(),
            price_per_unit: parseFloat($("#price").val())
        };

        if (!payload.name || !payload.price_per_unit || !payload.uom_id) {
            alert("Fill all fields");
            return;
        }

        const url = editingProductId ? "/updateProduct" : "/addProduct";

        apiPost(url, payload)
            .then(() => {
                $("#productModal").modal("hide");
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
