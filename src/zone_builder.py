from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from geomeppy.builder import Block, Zone

from .geometry_utils import generate_points_in_polygon


ROOM_CONFIG = {
    "bedroom": {
        "dual_sp": "Bedroom_DualSP",
        "tstat_prefix": "Bedroom_Tstat",
        "light_schedule": "DL_NightOff_bedroom",
        "add_hvac": True,
        "add_lights": True,
    },
    "living": {
        "dual_sp": "LivingRoom_DualSP",
        "tstat_prefix": "Living_Tstat",
        "light_schedule": "DL_NightOff_living",
        "add_hvac": True,
        "add_lights": True,
    },
    "kitchen": {
        "dual_sp": None,
        "tstat_prefix": None,
        "light_schedule": "DL_CookingOnly",
        "add_hvac": False,
        "add_lights": True,
    },
}

OTHER_ROOM_TYPES = ["bathroom", "other", "transformation", "garage"]


def add_all_room_zones(
    idf,
    plan_dic: dict,
    deg: float,
    num_stories: int,
    storey_height: float,
    lighting_power_density: float = 5.0,
):
    """Create EnergyPlus zones, surfaces, HVAC and lighting objects."""
    plan_json = {}

    for room_type in ["bedroom", "living", "kitchen"]:
        if room_type not in plan_dic:
            continue
        cfg = ROOM_CONFIG[room_type]
        for room_id, polygon in enumerate(plan_dic[room_type]):
            add_room_polygon(
                idf=idf,
                polygon=polygon,
                room_type=room_type,
                room_id=room_id,
                cfg=cfg,
                plan_json=plan_json,
                deg=deg,
                num_stories=num_stories,
                storey_height=storey_height,
                lighting_power_density=lighting_power_density,
            )

    for room_type in OTHER_ROOM_TYPES:
        if room_type not in plan_dic:
            continue
        for room_id, polygon in enumerate(plan_dic[room_type]):
            add_room_polygon(
                idf=idf,
                polygon=polygon,
                room_type=room_type,
                room_id=room_id,
                cfg={"add_hvac": False, "add_lights": False},
                plan_json=plan_json,
                deg=deg,
                num_stories=num_stories,
                storey_height=storey_height,
                lighting_power_density=lighting_power_density,
            )

    return plan_json


def add_room_polygon(
    idf,
    polygon,
    room_type: str,
    room_id: int,
    cfg: dict,
    plan_json: dict,
    deg: float,
    num_stories: int,
    storey_height: float,
    lighting_power_density: float,
):
    polygon = orient(polygon, sign=1.0)
    area = polygon.area
    coords = list(polygon.exterior.coords)

    block = Block(
        f"{room_type}_{room_id}",
        coordinates=coords,
        height=storey_height * num_stories,
        num_stories=num_stories,
        below_ground_stories=0,
        below_ground_storey_height=0,
    )

    zones = [
        Zone(f"Block {block.name} Storey {storey['storey_no']}", storey)
        for storey in block.stories
    ]

    for zone in zones:
        zone_name = zone.__dict__["name"]
        idf.newidfobject("ZONE", Name=zone_name)
        storey_no = int(zone_name.split("Storey")[-1].strip())
        plan_json[zone_name] = list(polygon.exterior.coords)

        add_surfaces_from_zone(idf, zone, zone_name)

        if cfg.get("add_hvac", False):
            add_ideal_loads_to_zone(
                idf=idf,
                zone_name=zone_name,
                thermostat_name=f"{cfg['tstat_prefix']}_{zone_name}",
                dual_sp_name=cfg["dual_sp"],
            )
            add_zone_infiltration_ach(
                idf=idf, 
                zone_name = zone_name, 
                ach=1.0
                )

        if cfg.get("add_lights", False):
            add_lights_and_daylighting(
                idf=idf,
                zone_name=zone_name,
                polygon=polygon,
                deg=deg,
                schedule_name=cfg["light_schedule"],
                lighting_level=area * lighting_power_density,
                z_ref=storey_no * storey_height + 0.8,
            )


def add_surfaces_from_zone(idf, zone, zone_name: str):
    for surface_type in zone.__dict__.keys():
        if surface_type == "name":
            continue
        for i, surface_coords in enumerate(zone.__dict__[surface_type], 1):
            if not surface_coords:
                continue
            surface_single = surface_type[:-1]
            name = f"{zone_name}_{surface_single}_{i:04d}"
            s = idf.newidfobject(
                "BUILDINGSURFACE:DETAILED",
                Construction_Name=f"{surface_single}_U1",
                Name=name,
                Surface_Type=surface_single,
                Zone_Name=zone_name,
            )
            s.setcoords(surface_coords)


def add_ideal_loads_to_zone(idf, zone_name: str, thermostat_name: str, dual_sp_name: str):
    idf.newidfobject(
        "ZONECONTROL:THERMOSTAT",
        Name=thermostat_name,
        Zone_or_ZoneList_Name=zone_name,
        Control_Type_Schedule_Name="ALWAYS_DUAL",
        Control_1_Object_Type="ThermostatSetpoint:DualSetpoint",
        Control_1_Name=dual_sp_name,
    )

    idf.newidfobject(
        "ZONEHVAC:IDEALLOADSAIRSYSTEM",
        Name=f"{zone_name}_IdealLoads",
        Zone_Supply_Air_Node_Name=f"{zone_name}_Inlet",
        Zone_Exhaust_Air_Node_Name=f"{zone_name}_Exhaust",
        Heating_Limit="NoLimit",
        Cooling_Limit="NoLimit",
        Maximum_Heating_Supply_Air_Temperature=50,
        Minimum_Cooling_Supply_Air_Temperature=12,
    )

    idf.newidfobject(
        "ZONEHVAC:EQUIPMENTCONNECTIONS",
        Zone_Name=zone_name,
        Zone_Conditioning_Equipment_List_Name=f"{zone_name}_EquipList",
        Zone_Air_Inlet_Node_or_NodeList_Name=f"{zone_name}_Inlet",
        Zone_Air_Exhaust_Node_or_NodeList_Name=f"{zone_name}_Exhaust",
        Zone_Air_Node_Name=f"{zone_name}_AirNode",
        Zone_Return_Air_Node_or_NodeList_Name=f"{zone_name}_Return",
    )

    idf.newidfobject(
        "ZONEHVAC:EQUIPMENTLIST",
        Name=f"{zone_name}_EquipList",
        Load_Distribution_Scheme="SequentialLoad",
        Zone_Equipment_1_Object_Type="ZoneHVAC:IdealLoadsAirSystem",
        Zone_Equipment_1_Name=f"{zone_name}_IdealLoads",
        Zone_Equipment_1_Cooling_Sequence=1,
        Zone_Equipment_1_Heating_or_NoLoad_Sequence=1,
    )

def add_zone_infiltration_ach(idf, zone_name: str, ach: float = 1.0):
    """
    Add infiltration based on air changes per hour.

    ACH = 1.0 means the zone air volume is replaced once per hour.
    """
    idf.newidfobject(
        "ZONEINFILTRATION:DESIGNFLOWRATE",
        Name=f"{zone_name}_Infiltration_ACH",
        Zone_or_ZoneList_or_Space_or_SpaceList_Name=zone_name,
        Schedule_Name="ALWAYS_DUAL",
        Design_Flow_Rate_Calculation_Method="AirChanges/Hour",
        Design_Flow_Rate="",
        Flow_Rate_per_Floor_Area="",
        Flow_Rate_per_Exterior_Surface_Area="",
        Air_Changes_per_Hour=ach,
        Constant_Term_Coefficient=1.0,
        Temperature_Term_Coefficient=0.0,
        Velocity_Term_Coefficient=0.0,
        Velocity_Squared_Term_Coefficient=0.0,
        Density_Basis="Outdoor",
    )

def add_lights_and_daylighting(idf, zone_name: str, polygon: Polygon, deg: float, schedule_name: str, lighting_level: float, z_ref: float):
    idf.newidfobject(
        "LIGHTS",
        Name=f"{zone_name}_Lights",
        Zone_or_ZoneList_or_Space_or_SpaceList_Name=zone_name,
        Schedule_Name=schedule_name,
        Design_Level_Calculation_Method="LightingLevel",
        Lighting_Level=lighting_level,
        Fraction_Radiant=0.6,
        Fraction_Visible=0.2,
        Fraction_Replaceable=1.0,
    )

    kwargs = {}
    points = generate_points_in_polygon(polygon, deg)
    for i, point in enumerate(points, start=1):
        ref_name = f"{zone_name}_RefPt_{i}"
        idf.newidfobject(
            "DAYLIGHTING:REFERENCEPOINT",
            Name=ref_name,
            Zone_or_Space_Name=zone_name,
            XCoordinate_of_Reference_Point=round(point.x, 3),
            YCoordinate_of_Reference_Point=round(point.y, 3),
            ZCoordinate_of_Reference_Point=z_ref,
        )
        kwargs[f"Daylighting_Reference_Point_{i}_Name"] = ref_name
        kwargs[f"Fraction_of_Lights_Controlled_by_Reference_Point_{i}"] = 0.1
        kwargs[f"Illuminance_Setpoint_at_Reference_Point_{i}"] = 100

    idf.newidfobject(
        "DAYLIGHTING:CONTROLS",
        Name=f"DLC_{zone_name}",
        Zone_or_Space_Name=zone_name,
        Daylighting_Method="SplitFlux",
        Lighting_Control_Type="Continuous",
        **kwargs,
    )
