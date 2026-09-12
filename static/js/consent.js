(function () {
    const CONSENT_COOKIE = 'sh_ads_consent';

    function getCookie(name) {
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? match[2] : null;
    }

    function setCookie(name, value, days) {
        const expires = new Date(Date.now() + days * 864e5).toUTCString();
        document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Lax`;
    }

    document.addEventListener('DOMContentLoaded', () => {
        if (getCookie(CONSENT_COOKIE)) return;

        const banner = document.getElementById('consent-banner');
        if (!banner) return;
        banner.classList.remove('hidden');

        const acceptBtn = document.getElementById('consent-accept');
        const rejectBtn = document.getElementById('consent-reject');

        acceptBtn.addEventListener('click', () => {
            setCookie(CONSENT_COOKIE, 'granted', 180);
            window.location.reload();
        });

        rejectBtn.addEventListener('click', () => {
            setCookie(CONSENT_COOKIE, 'rejected', 180);
            banner.classList.add('hidden');
        });
    });
})();
