async function apiFetch(url, options = {}) {
    const opts = {
        credentials: "include",
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        ...options
    };

    let res = await fetch(url, opts);

    if (res.status !== 401) return res;

    let data = {};
    try { data = await res.clone().json(); } catch {}

    if (data.error !== "TOKEN_EXPIRED" && data.error !== "SESSION_EXPIRED")
        return res;

    const refreshRes = await fetch("/api/auth/refresh", {
        method: "POST",
        credentials: "include"
    });

    if (!refreshRes.ok) {
        window.location.href = "/login";
        return refreshRes;
    }

    return await fetch(url, opts);
}

async function apiFetchJson(url, options = {}) {
    const res = await apiFetch(url, options);
    const data = await res.json().catch(() => null);
    if (!res.ok) throw { status: res.status, data };
    return data;
}
