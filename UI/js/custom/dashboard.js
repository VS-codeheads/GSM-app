
$(function () {
    const $tbody = $("table tbody");

    apiGet("/getProducts")
        .then(products => {
            $tbody.empty();
            $tbody.append(`
                <tr>
                    <td colspan="4">
                        <b>${products.length}</b> products available.
                        Use "Manage Products" or "New Order".
                    </td>
                </tr>
            `);
        })
        .catch(err => {
            console.error(err);
            $tbody.append(`<tr><td colspan="4">Failed to load data</td></tr>`);
        });
});
