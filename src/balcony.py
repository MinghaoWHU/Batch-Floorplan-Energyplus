def add_balcony_shading(idf, plan_dic: dict, plan_json: dict, num_stories: int, storey_height: float):
    if "balcony" not in plan_dic:
        return

    for balcony_id, polygon in enumerate(plan_dic["balcony"]):
        exterior = list(polygon.exterior.coords)
        for storey in range(num_stories):
            plan_json[f"balcony_{balcony_id}_{storey}"] = exterior
            coords_3d = [(x, y, storey_height * (storey + 1)) for x, y in exterior]
            shade = idf.newidfobject(
                "SHADING:SITE:DETAILED",
                Name=f"Shade_{storey}_{balcony_id}",
                Number_of_Vertices=len(coords_3d),
            )
            shade.setcoords(coords_3d)
