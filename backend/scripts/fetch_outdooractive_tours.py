"""
Utility script to download curated Outdooractive tour data per category.

Usage example:
    python backend/scripts/fetch_outdooractive_tours.py --api-key $OUTDOORACTIVE_API_KEY
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import ssl
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence
from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree import ElementTree as ET


NS = {"oa": "http://www.outdooractive.com/api/"}
FILTER_URL = "https://www.outdooractive.com/api/project/api-dev-oa/filter/tour"
OOIS_URL = "https://www.outdooractive.com/api/project/api-dev-oa/oois"

DEFAULT_CATEGORIES: Sequence[Dict[str, Any]] = (
    {"id": 8982346, "name": "Theme trail", "count": 20},
    {"id": 8982343, "name": "Hiking trail", "count": 20},
    {"id": 8982347, "name": "Cycling", "count": 40},
    {"id": 8982357, "name": "Trail running", "count": 20},
    {"id": 8982356, "name": "Jogging", "count": 20},
)


class HttpClient:
    def __init__(self, verify_ssl: bool = True):
        if verify_ssl:
            self._ssl_context = ssl.create_default_context()
        else:
            self._ssl_context = ssl._create_unverified_context()  # type: ignore[attr-defined]

    def get(self, url: str, params: Dict[str, Any] | None = None, timeout: int = 60) -> bytes:
        request_url = url
        if params:
            request_url = f"{url}?{urlencode(params)}"
        with urlopen(request_url, timeout=timeout, context=self._ssl_context) as response:
            status = getattr(response, "status", response.getcode())
            if status and status >= 400:
                raise RuntimeError(f"GET {request_url} failed with status {status}")
            return response.read()


def chunked(seq: Sequence[int], size: int) -> Iterable[Sequence[int]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def fetch_tour_ids(client: HttpClient, api_key: str, category_id: int, limit: int) -> List[int]:
    params = {
        "category": category_id,
        "key": api_key,
        "limit": max(limit, 20),
    }
    payload = client.get(FILTER_URL, params=params, timeout=60)
    root = ET.fromstring(payload)
    ids = [int(node.attrib["id"]) for node in root.findall("oa:data", NS)]
    if not ids:
        raise RuntimeError(f"No tours returned for category {category_id}")
    return ids[:limit]


def _text(elem: ET.Element | None) -> str | None:
    if elem is None or elem.text is None:
        return None
    return elem.text.strip() or None


def parse_tour(tour_elem: ET.Element) -> Dict[str, Any]:
    category_elem = tour_elem.find("oa:category", NS)
    rating_elem = tour_elem.find("oa:rating", NS)
    length_elem = tour_elem.find("oa:length", NS)
    time_elem = tour_elem.find("oa:time", NS)
    elevation_elem = tour_elem.find("oa:elevation", NS)
    start_elem = tour_elem.find("oa:startingPoint", NS)
    season_elem = tour_elem.find("oa:season", NS)

    def attr_float(elem: ET.Element | None, attr: str) -> float | None:
        if elem is None:
            return None
        value = elem.attrib.get(attr)
        return float(value) if value is not None else None

    def attr_int(elem: ET.Element | None, attr: str) -> int | None:
        if elem is None:
            return None
        value = elem.attrib.get(attr)
        return int(float(value)) if value is not None else None

    images = []
    for img in tour_elem.findall("oa:images/oa:image", NS):
        images.append(
            {
                "id": int(img.attrib["id"]),
                "title": _text(img.find("oa:title", NS)),
                "source": _text(img.find("oa:source", NS)),
                "width": attr_int(img, "width"),
                "height": attr_int(img, "height"),
                "primary": img.attrib.get("primary") == "true",
                "gallery": img.attrib.get("gallery") == "true",
            }
        )

    regions = []
    for region in tour_elem.findall("oa:regions/oa:region", NS):
        regions.append(
            {
                "id": int(region.attrib["id"]),
                "name": region.attrib.get("name"),
                "type": region.attrib.get("type"),
                "is_start_region": region.attrib.get("isStartRegion") == "true",
            }
        )

    season = {}
    if season_elem is not None:
        for month in (
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ):
            season[month] = season_elem.attrib.get(month) == "true"

    return {
        "id": int(tour_elem.attrib["id"]),
        "title": _text(tour_elem.find("oa:title", NS)),
        "localized_titles": [
            {
                "lang": lt.attrib.get("lang"),
                "value": _text(lt.find("oa:value", NS)),
            }
            for lt in tour_elem.findall("oa:localizedTitle", NS)
        ],
        "category": {
            "id": int(category_elem.attrib["id"]) if category_elem is not None else None,
            "name": category_elem.attrib.get("name") if category_elem is not None else None,
            "icon_url": category_elem.attrib.get("iconUrl") if category_elem is not None else None,
        },
        "short_text": _text(tour_elem.find("oa:shortText", NS)),
        "long_text": _text(tour_elem.find("oa:longText", NS)),
        "length_m": attr_float(length_elem, "value") or attr_float(length_elem, "length")
        or attr_float(length_elem, "data")
        or (float(length_elem.text) if length_elem is not None and length_elem.text else None),
        "duration_min": attr_int(time_elem, "min"),
        "difficulty": rating_elem.attrib.get("difficulty") if rating_elem is not None else None,
        "rating": {
            key: rating_elem.attrib.get(key)
            for key in ("condition", "difficulty", "qualityOfExperience", "landscape")
        }
        if rating_elem is not None
        else None,
        "elevation": {
            key: attr_int(elevation_elem, key)
            for key in ("ascent", "descent", "minAltitude", "maxAltitude")
        }
        if elevation_elem is not None
        else None,
        "starting_point": {
            "description": _text(tour_elem.find("oa:startingPointDescr", NS)),
            "lon": attr_float(start_elem, "lon"),
            "lat": attr_float(start_elem, "lat"),
        }
        if start_elem is not None
        else None,
        "season": season or None,
        "public_transit": _text(tour_elem.find("oa:publicTransit", NS)),
        "getting_there": _text(tour_elem.find("oa:gettingThere", NS)),
        "parking": _text(tour_elem.find("oa:parking", NS)),
        "directions": _text(tour_elem.find("oa:directions", NS)),
        "equipment": _text(tour_elem.find("oa:equipment", NS)),
        "additional_information": _text(tour_elem.find("oa:additionalInformation", NS)),
        "images": images or None,
        "regions": regions or None,
    }


def fetch_tour_details(client: HttpClient, api_key: str, tour_ids: Sequence[int]) -> List[Dict[str, Any]]:
    tours: List[Dict[str, Any]] = []
    for batch in chunked(list(tour_ids), 20):
        ids_param = ",".join(str(tid) for tid in batch)
        payload = client.get(f"{OOIS_URL}/{ids_param}", params={"key": api_key}, timeout=120)
        root = ET.fromstring(payload)
        for tour_elem in root.findall("oa:tour", NS):
            tours.append(parse_tour(tour_elem))
    return tours


def build_dataset(client: HttpClient, api_key: str, categories: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    collected = []
    for cat in categories:
        ids = fetch_tour_ids(client, api_key, cat["id"], cat["count"])
        tours = fetch_tour_details(client, api_key, ids)
        collected.append(
            {
                "id": cat["id"],
                "name": cat["name"],
                "requested_count": cat["count"],
                "fetched_count": len(tours),
                "tour_ids": ids,
                "tours": tours,
            }
        )
    return {
        "fetched_at": dt.datetime.utcnow().isoformat() + "Z",
        "source": "Outdooractive",
        "categories": collected,
        "total_tours": sum(len(cat["tours"]) for cat in collected),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch Outdooractive tours per category.")
    parser.add_argument("--api-key", help="Outdooractive project API key", default=os.getenv("OUTDOORACTIVE_API_KEY"))
    parser.add_argument(
        "--output-dir",
        default="backend/data/outdooractive",
        help="Directory where the aggregated JSON file will be stored.",
    )
    parser.add_argument(
        "--disable-ssl-verify",
        action="store_true",
        help="Disable SSL verification (only use if your environment lacks CA certificates).",
    )
    args = parser.parse_args(argv)

    if not args.api_key:
        parser.error("An API key is required. Provide --api-key or set OUTDOORACTIVE_API_KEY.")

    client = HttpClient(verify_ssl=not args.disable_ssl_verify)
    dataset = build_dataset(client, args.api_key, DEFAULT_CATEGORIES)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_file = output_dir / f"tours_{timestamp}.json"
    output_file.write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {output_file} with {dataset['total_tours']} tours.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

