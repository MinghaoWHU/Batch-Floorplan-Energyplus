import numpy as np

from .geometry_utils import (
    merge_and_check,
    windows_from_linestring,
    surface_normal,
    project_to_wall_plane,
    split_to_quads,
    linestring_touch_wall,
    is_degenerate,
)


def add_window_by_coords(idf, coords, construction: str = "", element_id: str = "", element_type: str = ""):
    try:
        ggr = idf.idfobjects["GLOBALGEOMETRYRULES"][0]
    except IndexError:
        ggr = None

    walls = [
        s for s in idf.idfobjects["BUILDINGSURFACE:DETAILED"]
        if s.Surface_Type.upper() == "WALL"
        and s.Outside_Boundary_Condition.upper() == "OUTDOORS"
    ]

    matched_wall = None
    wx, wy, wz = coords[0]
    eps = 1e-7

    for wall in walls:
        wall_coords = wall.coords
        xs = [p[0] for p in wall_coords]
        ys = [p[1] for p in wall_coords]
        zs = [p[2] for p in wall_coords]

        is_x_plane = abs(max(xs) - min(xs)) < eps and abs(wx - xs[0]) < eps
        is_y_plane = abs(max(ys) - min(ys)) < eps and abs(wy - ys[0]) < eps
        if not (is_x_plane or is_y_plane):
            continue

        z_ok = min(zs) - eps <= wz <= max(zs) + eps
        if is_x_plane:
            horizontal_ok = min(ys) - eps <= wy <= max(ys) + eps
        else:
            horizontal_ok = min(xs) - eps <= wx <= max(xs) + eps

        if not (z_ok and horizontal_ok):
            continue

        if not linestring_touch_wall(coords, wall_coords):
            continue

        matched_wall = wall
        break

    if matched_wall is None:
        raise ValueError("❌ 未找到对应的墙体（不共面或不接触）")

    wall_coords = matched_wall.coords
    coords = project_to_wall_plane(coords, wall_coords)

    wall_normal = surface_normal(wall_coords)
    win_normal = surface_normal(coords)
    if np.dot(wall_normal, win_normal) < 0:
        coords = coords[::-1]

    quad_list = [coords] if len(coords) == 4 else split_to_quads(coords)

    windows = []
    for i, quad in enumerate(quad_list):
        if len(quad) < 4 or is_degenerate(quad):
            continue
        win = idf.newidfobject(
            "FENESTRATIONSURFACE:DETAILED",
            Name=f"{matched_wall.Name}_window_{element_id}_{i}_{element_type}",
            Surface_Type="Window",
            Construction_Name=construction,
            Building_Surface_Name=matched_wall.Name,
            View_Factor_to_Ground="autocalculate",
        )
        win.setcoords(quad, ggr)
        windows.append(win)

    return windows


def add_windows_and_doors(idf, plan_dic: dict, plan_json: dict, num_stories: int, storey_height: float):
    plan_json["window"] = {}
    for window_id, ls in enumerate(plan_dic.get("window", [])):
        line_coords = list(ls.coords)
        for storey in range(num_stories):
            plan_json["window"].setdefault(storey, [])
            try:
                wins = windows_from_linestring(
                    ls,
                    z_bottom=0.9 + storey * storey_height,
                    z_top=2.2 + storey * storey_height,
                )
                for j, win_coords in enumerate(wins):
                    add_window_by_coords(
                        idf,
                        win_coords,
                        construction="WindowConstruction_U25",
                        element_id=f"{storey}_{window_id}_{j}",
                        element_type="window",
                    )
                plan_json["window"][storey].append(line_coords)
            except Exception as e:
                print(f"[窗口跳过] storey={storey}, window={window_id}, reason={e}")

    door_list = merge_and_check(plan_dic)
    plan_json["door"] = {}
    for door_id, ls in enumerate(door_list):
        line_coords = list(ls.coords)
        for storey in range(num_stories):
            plan_json["door"].setdefault(storey, [])
            try:
                wins = windows_from_linestring(
                    ls,
                    z_bottom=storey * storey_height + 0.05,
                    z_top=2.2 + storey * storey_height,
                )
                for j, win_coords in enumerate(wins):
                    add_window_by_coords(
                        idf,
                        win_coords,
                        construction="WindowConstruction_U25",
                        element_id=f"{storey}_{door_id}_{j}",
                        element_type="door",
                    )
                plan_json["door"][storey].append(line_coords)
            except Exception as e:
                print(f"[门跳过] storey={storey}, door={door_id}, reason={e}")
