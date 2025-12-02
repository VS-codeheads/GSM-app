
$(function () {
    const $tbody = $("table tbody");
    const $modal = $("#productModal");

    // Load products into table
    function loadProducts() {
        apiGet("/getProducts")
            .then(products => {
                $tbody.empty();

                if (products.length === 0) {
                    $tbody.append(`<tr><td colspan="4" class="text-center">No products yet</td></tr>`);
                    return;
                }

                products.forEach(p => {
                    $tbody.append(`
                        <tr data-id="${p.product_id}">
                            <td>${p.name}</td>
                            <td>${p.uom_name}</td>
                            <td>${p.price_per_unit.toFixed(2)}</td>
                            <td>
                                <button class="btn btn-sm btn-danger deleteProduct">Delete</button>
                            </td>
                        </tr>
                    `);
                });
            })
            .catch(err => {
                console.error(err);
                toast("Failed to load products");
            });
    }

    // Load UOM select options
    function loadUOMs() {
        apiGet("/getUOM")
            .then(uoms => {
                const $uoms = $("#uoms");
                $uoms.empty();
                uoms.forEach(u =>
                    $uoms.append(`<option value="${u.uom_id}">${u.uom_name}</option>`)
                );
            })
            .catch(err => {
                console.error(err);
                toast("Failed to load units");
            });
    }

    // Save product
    $("#saveProduct").on("click", function () {
        const name = $("#name").val().trim();
        const uom_id = $("#uoms").val();
        const price = parseFloat($("#price").val().trim());

        if (!name || !uom_id || isNaN(price)) {
            toast("Fill all fields correctly");
            return;
        }

        const payload = {
            name,
            uom_id: parseInt(uom_id),
            price_per_unit: price
        };

        apiPost("/addProduct", payload)
            .then(() => {
                toast("Product added");
                $modal.modal("hide");
                loadProducts();
            })
            .catch(err => {
                console.error(err);
                toast("Failed to save product");
            });
    });

    // Delete product
    $(document).on("click", ".deleteProduct", function () {
        const id = $(this).closest("tr").data("id");

        if (!confirm("Delete this product?")) return;

        apiDelete(`/deleteProduct/${id}`)
            .then(() => {
                toast("Deleted");
                loadProducts();
            })
            .catch(err => {
                console.error(err);
                toast("Failed to delete");
            });
    });

    // Load UOM list when modal opens
    $modal.on("show.bs.modal", loadUOMs);

    // Initial load
    loadProducts();
});
