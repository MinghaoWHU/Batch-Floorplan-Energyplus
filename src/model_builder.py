from pathlib import Path
from typing import Dict, Any

from geomeppy import IDF

from .balcony import add_balcony_shading
from .constructions import add_constructions
from .envelope import load_random_envelope
from .fenestration import add_windows_and_doors
from .schedules import add_all_schedules
from .zone_builder import add_all_room_zones

_IDD_READY = False


def create_base_idf(idd_path: Path, base_idf_path: Path, epw_path: Path):
    global _IDD_READY
    if not _IDD_READY:
        IDF.setiddname(str(idd_path))
        _IDD_READY = True

    idf = IDF(str(base_idf_path))
    idf.epw = str(epw_path)
    return idf


def build_idf_from_plan(plan_dic: dict, deg: float, config_module):
    """Build one EnergyPlus IDF model from the parsed DXF geometry dictionary."""
    idf = create_base_idf(
        idd_path=config_module.IDD_PATH,
        base_idf_path=config_module.BASE_IDF_PATH,
        epw_path=config_module.EPW_PATH,
    )

    envelope = load_random_envelope(config_module.CONSTRUCTION_DIR)
    sid = envelope.get("id", "")
    print(f"✔ Using envelope scenario: {sid} - {envelope.get('description', '')}")

    add_all_schedules(idf)
    add_constructions(idf, envelope)

    plan_json = add_all_room_zones(
        idf=idf,
        plan_dic=plan_dic,
        deg=deg,
        num_stories=config_module.NUM_STORIES,
        storey_height=config_module.STOREY_HEIGHT,
        lighting_power_density=config_module.LIGHTING_POWER_DENSITY,
    )

    add_balcony_shading(
        idf=idf,
        plan_dic=plan_dic,
        plan_json=plan_json,
        num_stories=config_module.NUM_STORIES,
        storey_height=config_module.STOREY_HEIGHT,
    )

    idf.intersect_match()

    add_windows_and_doors(
        idf=idf,
        plan_dic=plan_dic,
        plan_json=plan_json,
        num_stories=config_module.NUM_STORIES,
        storey_height=config_module.STOREY_HEIGHT,
    )

    idf.idfobjects["BUILDING"][0].North_Axis = deg
    add_run_control_and_outputs(idf)

    return idf, plan_json, envelope


def add_run_control_and_outputs(idf):
    sc = idf.idfobjects["SIMULATIONCONTROL"][0]
    sc.Run_Simulation_for_Sizing_Periods = "No"
    sc.Run_Simulation_for_Weather_File_Run_Periods = "Yes"

    idf.newidfobject(
        "RUNPERIOD",
        Name="Annual",
        Begin_Month=1,
        Begin_Day_of_Month=1,
        End_Month=12,
        End_Day_of_Month=31,
        Day_of_Week_for_Start_Day="Sunday",
        Use_Weather_File_Holidays_and_Special_Days="Yes",
        Use_Weather_File_Daylight_Saving_Period="Yes",
        Apply_Weekend_Holiday_Rule="No",
        Use_Weather_File_Rain_Indicators="Yes",
        Use_Weather_File_Snow_Indicators="Yes",
    )

    for var_name in [
        "Zone Ideal Loads Zone Total Heating Energy",
        "Zone Ideal Loads Zone Total Cooling Energy",
        "Zone Lights Electricity Energy",
        # "Zone Thermal Comfort ASHRAE 55 Simple Model Summer Clothes Not Comfortable Time",
        # "Zone Thermal Comfort ASHRAE 55 Simple Model Winter Clothes Not Comfortable Time",
        # "Zone Heating Setpoint Not Met Time",
        # "Zone Cooling Setpoint Not Met Time",
        "Zone Mean Air Temperature",
        "Zone Air Relative Humidity",
        "Zone Mean Radiant Temperature",
        "Zone Operative Temperature",
        # "Zone Mechanical Ventilation Air Changes per Hour",
        # "Surface Inside Face Temperature",
        # "Surface Outside Face Temperature",
        # "Surface Heat Storage Rate",
        # "Surface Inside Face Conduction Heat Transfer Rate",
        # "Surface Window Transmitted Solar Radiation Rate",
        # "Surface Outside Face Incident Solar Radiation Rate per Area"
    ]:
        idf.newidfobject(
            "OUTPUT:VARIABLE",
            Variable_Name=var_name,
            Reporting_Frequency="hourly",
        )

    idf.newidfobject(
        "OUTPUT:VARIABLEDICTIONARY",
        Key_Field="IDF",
    )
