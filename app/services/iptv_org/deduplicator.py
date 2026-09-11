from collections import defaultdict
from typing import TypeVar

T = TypeVar("T")


def dedupe_by_key(items: list[T], key_fn) -> tuple[list[T], int]:
    """Garde la première occurrence pour chaque clé, retourne (items_uniques, nb_doublons_supprimés)."""
    seen: set = set()
    result: list[T] = []
    duplicates = 0
    for item in items:
        key = key_fn(item)
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        result.append(item)
    return result, duplicates


def group_streams_by_channel(streams: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for stream in streams:
        if stream.get("channel"):
            grouped[stream["channel"]].append(stream)
    return grouped
