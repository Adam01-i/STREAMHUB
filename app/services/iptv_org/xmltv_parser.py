from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET


def _parse_xmltv_time(value: str) -> datetime:
    """Format iptv-org/XMLTV: '20260911180000 +0000'."""
    date_part, _, offset = value.strip().partition(" ")
    dt = datetime.strptime(date_part, "%Y%m%d%H%M%S")
    if offset:
        sign = 1 if offset[0] == "+" else -1
        hours = int(offset[1:3])
        minutes = int(offset[3:5])
        dt = dt.replace(tzinfo=timezone(sign * timedelta(hours=hours, minutes=minutes)))
    else:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def parse_xmltv(xml_bytes: bytes, channel_id: str) -> list[dict]:
    """Extrait uniquement les programmes appartenant à channel_id (le fichier peut contenir plusieurs chaînes)."""
    root = ET.fromstring(xml_bytes)
    programs: list[dict] = []

    for programme in root.findall("programme"):
        if programme.get("channel") != channel_id:
            continue

        title_el = programme.find("title")
        desc_el = programme.find("desc")
        category_el = programme.find("category")
        icon_el = programme.find("icon")

        try:
            start = _parse_xmltv_time(programme.get("start", ""))
            stop = _parse_xmltv_time(programme.get("stop", ""))
        except ValueError:
            continue

        programs.append(
            {
                "title": (title_el.text or "Sans titre") if title_el is not None else "Sans titre",
                "description": desc_el.text if desc_el is not None else None,
                "category": category_el.text if category_el is not None else None,
                "start_time": start,
                "end_time": stop,
                "image_url": icon_el.get("src") if icon_el is not None else None,
            }
        )
    return programs

