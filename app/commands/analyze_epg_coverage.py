import asyncio
from collections import defaultdict

from app.services.iptv_org.client import IptvOrgClient
from app.services.iptv_org.parser import parse_channels

AFRICAN_COUNTRY_CODES = {
    "DZ", "AO", "BJ", "BW", "BF", "BI", "CV", "CM", "CF", "TD", "KM", "CG", "CD",
    "CI", "DJ", "EG", "GQ", "ER", "SZ", "ET", "GA", "GM", "GH", "GN", "GW", "KE",
    "LS", "LR", "LY", "MG", "MW", "ML", "MR", "MU", "MA", "MZ", "NA", "NE", "NG",
    "RW", "ST", "SN", "SC", "SL", "SO", "ZA", "SS", "SD", "TZ", "TG", "TN", "UG",
    "ZM", "ZW",
}


async def main() -> None:
    client = IptvOrgClient()
    try:
        raw_channels = await client.get_channels()
        channels = parse_channels(raw_channels)
        guides_raw = await client.get_guides()
    finally:
        await client.aclose()

    channels_by_country: dict[str, list[str]] = defaultdict(list)
    for ch in channels:
        if ch.closed is None and ch.country:
            channels_by_country[ch.country].append(ch.id)

    channel_ids_with_guide: set[str] = {g["channel"] for g in guides_raw if g.get("channel")}

    print("=================================")
    print(" COUVERTURE EPG — SÉNÉGAL & AFRIQUE")
    print("=================================")

    total_africa_channels = 0
    total_africa_with_epg = 0

    for code in sorted(AFRICAN_COUNTRY_CODES):
        ids = channels_by_country.get(code, [])
        if not ids:
            continue
        with_epg = [cid for cid in ids if cid in channel_ids_with_guide]
        total_africa_channels += len(ids)
        total_africa_with_epg += len(with_epg)
        marker = " <-- PRIORITÉ" if code == "SN" else ""
        print(f"{code}: {len(ids)} chaînes actives, {len(with_epg)} avec EPG{marker}")

    print("---------------------------------")
    print(f"TOTAL Afrique: {total_africa_channels} chaînes, {total_africa_with_epg} avec EPG "
          f"({(total_africa_with_epg / total_africa_channels * 100) if total_africa_channels else 0:.1f}%)")

    sn_ids = channels_by_country.get("SN", [])
    sn_with_epg = [cid for cid in sn_ids if cid in channel_ids_with_guide]
    print(f"SÉNÉGAL: {len(sn_ids)} chaînes actives, {len(sn_with_epg)} avec entrée EPG")
    if sn_with_epg:
        print("Chaînes sénégalaises avec EPG :", ", ".join(sn_with_epg))
    else:
        print("Aucune chaîne sénégalaise ne dispose d'une entrée EPG dans guides.json.")


if __name__ == "__main__":
    asyncio.run(main())
