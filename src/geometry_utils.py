from typing import List, Dict, Any

import numpy as np
from shapely.geometry import Point, LineString, Polygon, MultiLineString
from shapely.ops import triangulate, unary_union


def merge_and_check(plan_dic: Dict[str, Any]):
    """
    Keep only doors that are not almost completely inside the merged room polygon.

    Note: this function does not mutate plan_dic. The original script deleted balcony
    before checking doors. Here the same effect is achieved with a filtered copy.
    """
    plan_no_balcony = {k: v for k, v in plan_dic.items() if k != "balcony"}
    polygons = [
        item
        for sublist in plan_no_balcony.values()
        if isinstance(sublist, list)
        for item in sublist
        if isinstance(item, Polygon)
    ]
    if not polygons:
        return []

    merged_polygon = unary_union(polygons)
    valid_doors = []
    for door in plan_dic.get("door", []):
        if isinstance(door, (LineString, MultiLineString)):
            buffered_door = door.buffer(0.3)
            if buffered_door.area <= 0:
                continue
            ratio = merged_polygon.intersection(buffered_door).area / buffered_door.area
            if ratio < 0.9:
                valid_doors.append(door)
    return valid_doors


def windows_from_linestring(
    ls: LineString,
    z_bottom: float = 0.9,
    z_top: float = 2.2,
    linearity_tol: float = 1e-6,
):
    """Convert a 2D LineString into one or more 3D EnergyPlus window rectangles."""
    if not isinstance(ls, LineString):
        raise ValueError("Input must be a LineString")

    coords = np.array(ls.coords)
    n = len(coords)

    if n > 2:
        xs = coords[:, 0]
        ys = coords[:, 1]
        coeffs = np.polyfit(xs, ys, 1)
        ys_fit = np.polyval(coeffs, xs)
        max_dev = np.max(np.abs(ys - ys_fit))
        is_straight = max_dev < linearity_tol
    else:
        is_straight = True

    windows = []
    if is_straight:
        sorted_idx = np.argsort(coords[:, 0] + coords[:, 1] * 1e-6)
        p1 = coords[sorted_idx[0]]
        p2 = coords[sorted_idx[-1]]
        windows.append([
            (p1[0], p1[1], z_bottom),
            (p2[0], p2[1], z_bottom),
            (p2[0], p2[1], z_top),
            (p1[0], p1[1], z_top),
        ])
        return windows

    for i in range(n - 1):
        x1, y1 = coords[i]
        x2, y2 = coords[i + 1]
        windows.append([
            (x1, y1, z_bottom),
            (x2, y2, z_bottom),
            (x2, y2, z_top),
            (x1, y1, z_top),
        ])
    return windows


def surface_normal(coords):
    p1, p2, p3 = np.array(coords[0]), np.array(coords[1]), np.array(coords[2])
    normal = np.cross(p2 - p1, p3 - p1)
    n = np.linalg.norm(normal)
    return normal / n if n > 1e-12 else normal


def is_coplanar(win_coords, wall_coords, tol: float = 1e-6) -> bool:
    p1 = np.array(wall_coords[0])
    n = surface_normal(wall_coords)
    for p in win_coords:
        p = np.array(p)
        d = np.dot(n, p - p1)
        if abs(d) > tol:
            return False
    return True


def project_to_wall_plane(win_coords, wall_coords):
    p1 = np.array(wall_coords[0])
    n = surface_normal(wall_coords)
    projected = []
    for p in win_coords:
        p = np.array(p)
        d = np.dot(n, p - p1)
        projected.append(tuple(p - d * n))
    return projected


def split_to_quads(coords):
    poly = Polygon([(x, y) for x, y, z in coords])
    tris = triangulate(poly)

    quads = []
    for i in range(0, len(tris), 2):
        if i + 1 < len(tris):
            t1 = list(tris[i].exterior.coords[:-1])
            t2 = list(tris[i + 1].exterior.coords[:-1])
            quad_xy = t1[:2] + t2[:2]
        else:
            t = list(tris[i].exterior.coords[:-1])
            centroid = poly.centroid
            quad_xy = [t[0], t[1], t[2], (centroid.x, centroid.y)]

        z = coords[0][2]
        quads.append([(x, y, z) for x, y in quad_xy])
    return quads


def generate_points_in_polygon(poly, deg, num_points: int = 10, grid_size: int = 10, dis: float = -1):
    """Generate evenly distributed daylighting reference points inside a polygon."""
    poly0 = poly.buffer(dis)
    while poly0.is_empty:
        dis = dis / 4
        poly0 = poly.buffer(dis)
    poly = poly0

    minx, miny, maxx, maxy = poly.bounds
    points = []

    while len(points) < num_points:
        x_step = (maxx - minx) / grid_size
        y_step = (maxy - miny) / grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                x = minx + (i + 0.5) * x_step
                y = miny + (j + 0.5) * y_step
                point = Point(x, y)
                if poly.contains(point):
                    points.append(point)

        grid_size *= 2
        if len(points) > num_points:
            points = list(np.random.choice(points, num_points, replace=False))

    rad = np.radians(deg)
    cos_rad = np.cos(rad)
    sin_rad = np.sin(rad)

    rotated_points = []
    for point in points:
        x, y = point.x, point.y
        x_rot = x * cos_rad - y * sin_rad
        y_rot = x * sin_rad + y * cos_rad
        rotated_points.append(Point(x_rot, y_rot))
    return rotated_points


def linestring_touch_wall(ls_coords, wall_coords, tol: float = 1e-6) -> bool:
    """Check whether a 3D window/door baseline touches the 2D projection of a wall."""
    ls_2d = LineString([(x, y) for x, y, z in ls_coords])
    wall_xy = [(x, y) for x, y, z in wall_coords]

    # Remove duplicated consecutive points. Vertical EnergyPlus wall polygons can
    # collapse to a 2D line after projection.
    cleaned = []
    for p in wall_xy:
        if not cleaned or p != cleaned[-1]:
            cleaned.append(p)
    unique = list(dict.fromkeys(cleaned))
    if len(unique) < 2:
        return False

    wall_line = LineString(unique)
    return ls_2d.intersects(wall_line) or ls_2d.distance(wall_line) <= tol


def is_degenerate(quad) -> bool:
    xs = [p[0] for p in quad]
    ys = [p[1] for p in quad]
    return (max(xs) - min(xs) < 1e-6) and (max(ys) - min(ys) < 1e-6)
