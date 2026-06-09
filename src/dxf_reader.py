from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import ezdxf
import numpy as np
from shapely.geometry import Point, LineString, Polygon


def dxf_to_layer_geometries(dxf_path: Path):
    """Read DXF entities and convert them into Shapely geometries by layer."""
    doc = ezdxf.readfile(str(dxf_path))
    msp = doc.modelspace()

    layer_dict = defaultdict(list)
    total_area = 0.0
    bedroom_area = 0.0
    living_area = 0.0

    for entity in msp:
        layer = entity.dxf.layer
        geom = dxf_entity_to_shapely(entity)
        if geom is None:
            continue

        layer_dict[layer].append(geom)
        if layer in ["bathroom", "bedroom", "living", "balcony"]:
            total_area += geom.area
            if layer == "bedroom":
                bedroom_area += geom.area
            elif layer == "living":
                living_area += geom.area

    return dict(layer_dict), total_area, bedroom_area, living_area


def dxf_entity_to_shapely(entity):
    etype = entity.dxftype()

    if etype == "POINT":
        x, y, *_ = entity.dxf.location
        return Point(x, y)

    if etype == "LINE":
        return LineString([
            (entity.dxf.start.x, entity.dxf.start.y),
            (entity.dxf.end.x, entity.dxf.end.y),
        ])

    if etype == "LWPOLYLINE":
        pts = [(p[0], p[1]) for p in entity.get_points()]
        return Polygon(pts) if entity.closed and len(pts) >= 3 else LineString(pts)

    if etype == "POLYLINE":
        pts = [(v.dxf.location.x, v.dxf.location.y) for v in entity.vertices()]
        return Polygon(pts) if entity.is_closed and len(pts) >= 3 else LineString(pts)

    if etype == "CIRCLE":
        center = entity.dxf.center
        return Point(center.x, center.y).buffer(entity.dxf.radius, resolution=64)

    if etype == "ARC":
        return arc_to_linestring(entity, n=64)

    return None


def arc_to_linestring(entity, n: int = 64) -> LineString:
    cx, cy = entity.dxf.center.x, entity.dxf.center.y
    r = entity.dxf.radius
    a1 = entity.dxf.start_angle
    a2 = entity.dxf.end_angle

    if a2 < a1:
        a2 += 360

    angles = np.deg2rad(np.linspace(a1, a2, n))
    pts = [(cx + r * np.cos(a), cy + r * np.sin(a)) for a in angles]
    return LineString(pts)
