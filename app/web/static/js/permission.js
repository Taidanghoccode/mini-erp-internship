
(function () {
    function getPermissions() {
        try {
            const raw = localStorage.getItem("permissions");
            if (!raw) return [];
            const parsed = JSON.parse(raw);
            return Array.isArray(parsed) ? parsed : [];
        } catch (e) {
            console.warn("Cannot parse permissions from localStorage", e);
            return [];
        }
    }

    function hasPermission(code) {
        if (!code) return true; 
        const perms = getPermissions();
        return perms.includes(code);
    }

    function hasAnyPermission(codes) {
        if (!codes) return true;
        let list = codes;

        if (typeof codes === "string") {
            list = codes.split(",").map(s => s.trim()).filter(Boolean);
        }

        if (!Array.isArray(list) || list.length === 0) return true;

        const perms = getPermissions();
        return list.some(code => perms.includes(code));
    }

    function applyPermissionUI(root) {
        const rootEl = root || document;
        const perms = getPermissions();

        rootEl.querySelectorAll("[data-permission]").forEach(el => {
            const required = el.getAttribute("data-permission");
            if (!required) return;

            if (!perms.includes(required)) {
                el.style.display = "none";
            }
        });

        rootEl.querySelectorAll("[data-permission-any]").forEach(el => {
            const attr = el.getAttribute("data-permission-any") || "";
            const codes = attr.split(",").map(s => s.trim()).filter(Boolean);

            if (codes.length === 0) return;

            const ok = codes.some(code => perms.includes(code));
            if (!ok) {
                el.style.display = "none";
            }
        });
    }

    window.PermissionHelper = {
        getPermissions,
        hasPermission,
        hasAnyPermission,
        applyPermissionUI
    };

    window.hasPermission = hasPermission;
    window.hasAnyPermission = hasAnyPermission;
    window.applyPermissionUI = applyPermissionUI;

    document.addEventListener("DOMContentLoaded", function () {
        applyPermissionUI();
    });
})();
