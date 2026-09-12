from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.services.ads.factory import get_ad_provider

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def render_ad_slot(request: Request, placement: str) -> str:
    """Rendu d'un emplacement publicitaire, respectant le consentement.
    - Provider désactivé -> rien.
    - Provider activé mais pas de consentement -> placeholder discret, aucun script tiers chargé.
    - Consentement accordé -> HTML du provider.
    """
    provider = get_ad_provider()
    if not provider.is_enabled():
        return ""

    consent = request.cookies.get("sh_ads_consent")
    if consent != "granted":
        return (
            '<div class="ad-slot-placeholder my-6 text-center text-xs text-gray-600 '
            'border border-dashed border-ink-700 rounded-lg py-6" '
            f'data-placement="{placement}">Espace publicitaire — cookies publicitaires désactivés</div>'
        )

    html = provider.render(placement)
    if not html:
        return ""

    return f'<div class="ad-slot my-6 flex justify-center" data-placement="{placement}">{html}</div>'


def ads_enabled() -> bool:
    return get_ad_provider().is_enabled()


templates.env.globals["render_ad_slot"] = render_ad_slot
templates.env.globals["ads_enabled"] = ads_enabled