
// Simple GET request
function apiGet(url) {
    return fetch(window.API_BASE + url)
        .then(r => {
            if (!r.ok) throw new Error("API GET failure");
            return r.json();
        });
}

// POST using FormData with JSON string field "data"
function apiPost(url, payload) {
    const fd = new FormData();
    fd.append("data", JSON.stringify(payload));

    return fetch(window.API_BASE + url, {
        method: "POST",
        body: fd
    }).then(r => {
        if (!r.ok) throw new Error("API POST failure");
        return r.json();
    });
}

// DELETE request
function apiDelete(url) {
    return fetch(window.API_BASE + url, { method: "DELETE" })
        .then(r => {
            if (!r.ok) throw new Error("API DELETE failure");
            return r.json();
        });
}

// Basic alert
function toast(msg) {
    alert(msg);
}
