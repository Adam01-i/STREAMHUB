function initStreamHubPlayer(videoElId, errorElId, streamUrls) {
    const video = document.getElementById(videoElId);
    const errorBox = document.getElementById(errorElId);
    if (!video || !streamUrls || streamUrls.length === 0) return;

    let currentIndex = 0;
    let hls = null;

    function showError() {
        errorBox.classList.remove('hidden');
    }

    function hideError() {
        errorBox.classList.add('hidden');
    }

    function loadStream(index) {
        hideError();
        const url = streamUrls[index];

        if (hls) {
            hls.destroy();
            hls = null;
        }

        if (Hls.isSupported()) {
            hls = new Hls({ maxRetries: 3 });
            hls.loadSource(url);
            hls.attachMedia(video);
            hls.on(Hls.Events.ERROR, (_event, data) => {
                if (data.fatal) {
                    showError();
                }
            });
            hls.on(Hls.Events.MANIFEST_PARSED, () => {
                video.play().catch(() => {});
            });
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = url;
            video.addEventListener('error', showError, { once: true });
            video.play().catch(() => {});
        } else {
            showError();
        }
    }

    window.retryPlayback = () => loadStream(currentIndex);

    window.switchStream = () => {
        currentIndex = (currentIndex + 1) % streamUrls.length;
        loadStream(currentIndex);
    };

    loadStream(currentIndex);
}
