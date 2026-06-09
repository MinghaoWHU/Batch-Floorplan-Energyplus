def add_all_schedules(idf):
    add_thermal_schedules(idf)
    add_lighting_schedules(idf)


def add_thermal_schedules(idf):
    idf.newidfobject(
        "SCHEDULETYPELIMITS",
        Name="TEMPERATURE",
        Lower_Limit_Value=-20.0,
        Upper_Limit_Value=40.0,
        Numeric_Type="Continuous",
        Unit_Type="Temperature",
    )

    idf.newidfobject(
        "SCHEDULETYPELIMITS",
        Name="ControlType",
        Lower_Limit_Value=0,
        Upper_Limit_Value=4,
        Numeric_Type="Discrete",
    )

    idf.newidfobject(
        "SCHEDULE:COMPACT",
        Name="ALWAYS_DUAL",
        Schedule_Type_Limits_Name="ControlType",
        Field_1="Through: 12/31",
        Field_2="For: AllDays",
        Field_3="Until: 24:00, 4",
    )

    idf.newidfobject(
        "SCHEDULE:COMPACT",
        Name="Bedroom_CoolingSetpoint",
        Schedule_Type_Limits_Name="Temperature",
        Field_1="Through: 12/31",
        Field_2="For: AllDays",
        Field_3="Until: 08:00, 26.0",
        Field_4="Until: 18:00, 40.0",
        Field_5="Until: 24:00, 26.0",
    )

    idf.newidfobject(
        "SCHEDULE:COMPACT",
        Name="Bedroom_HeatingSetpoint",
        Schedule_Type_Limits_Name="Temperature",
        Field_1="Through: 12/31",
        Field_2="For: AllDays",
        Field_3="Until: 08:00, 18.0",
        Field_4="Until: 18:00, 5.0",
        Field_5="Until: 24:00, 18.0",
    )

    idf.newidfobject(
        "THERMOSTATSETPOINT:SINGLEHEATING",
        Name="B_HeatSP",
        Setpoint_Temperature_Schedule_Name="Bedroom_HeatingSetpoint",
    )

    idf.newidfobject(
        "THERMOSTATSETPOINT:SINGLECOOLING",
        Name="B_CoolSP",
        Setpoint_Temperature_Schedule_Name="Bedroom_CoolingSetpoint",
    )

    idf.newidfobject(
        "THERMOSTATSETPOINT:DUALSETPOINT",
        Name="Bedroom_DualSP",
        Heating_Setpoint_Temperature_Schedule_Name="Bedroom_HeatingSetpoint",
        Cooling_Setpoint_Temperature_Schedule_Name="Bedroom_CoolingSetpoint",
    )

    idf.newidfobject(
        "SCHEDULE:COMPACT",
        Name="LivingRoom_CoolingSetpoint",
        Schedule_Type_Limits_Name="Temperature",
        Field_1="Through: 12/31",
        Field_2="For: AllDays",
        Field_3="Until: 08:00, 40.0",
        Field_4="Until: 18:00, 26.0",
        Field_5="Until: 24:00, 40.0",
    )

    idf.newidfobject(
        "SCHEDULE:COMPACT",
        Name="LivingRoom_HeatingSetpoint",
        Schedule_Type_Limits_Name="Temperature",
        Field_1="Through: 12/31",
        Field_2="For: AllDays",
        Field_3="Until: 08:00, 5.0",
        Field_4="Until: 18:00, 18.0",
        Field_5="Until: 24:00, 5.0",
    )

    idf.newidfobject(
        "THERMOSTATSETPOINT:SINGLEHEATING",
        Name="L_HeatSP",
        Setpoint_Temperature_Schedule_Name="LivingRoom_HeatingSetpoint",
    )

    idf.newidfobject(
        "THERMOSTATSETPOINT:SINGLECOOLING",
        Name="L_CoolSP",
        Setpoint_Temperature_Schedule_Name="LivingRoom_CoolingSetpoint",
    )

    idf.newidfobject(
        "THERMOSTATSETPOINT:DUALSETPOINT",
        Name="LivingRoom_DualSP",
        Heating_Setpoint_Temperature_Schedule_Name="LivingRoom_HeatingSetpoint",
        Cooling_Setpoint_Temperature_Schedule_Name="LivingRoom_CoolingSetpoint",
    )


def add_lighting_schedules(idf):
    idf.newidfobject(
        "SCHEDULETYPELIMITS",
        Name="FRACTION",
        Lower_Limit_Value=0.0,
        Upper_Limit_Value=1.0,
        Numeric_Type="Continuous",
        Unit_Type="Dimensionless",
    )

    idf.newidfobject(
        "SCHEDULE:COMPACT",
        Name="DL_NightOff_bedroom",
        Schedule_Type_Limits_Name="Fraction",
        Field_1="Through: 12/31",
        Field_2="For: AllDays",
        Field_3="Until: 06:00, 0",
        Field_4="Until: 08:00, 1",
        Field_5="Until: 21:00, 0",
        Field_6="Until: 22:00, 1",
        Field_7="Until: 24:00, 0",
    )

    idf.newidfobject(
        "SCHEDULE:COMPACT",
        Name="DL_NightOff_living",
        Schedule_Type_Limits_Name="Fraction",
        Field_1="Through: 12/31",
        Field_2="For: AllDays",
        Field_3="Until: 06:00, 0",
        Field_4="Until: 08:00, 1",
        Field_5="Until: 17:00, 0",
        Field_6="Until: 22:00, 1",
        Field_7="Until: 24:00, 0",
    )

    idf.newidfobject(
        "SCHEDULE:COMPACT",
        Name="DL_CookingOnly",
        Schedule_Type_Limits_Name="Fraction",
        Field_1="Through: 12/31",
        Field_2="For: AllDays",
        Field_3="Until: 07:00, 0",
        Field_4="Until: 09:00, 1",
        Field_5="Until: 11:00, 0",
        Field_6="Until: 13:00, 1",
        Field_7="Until: 17:00, 0",
        Field_8="Until: 19:00, 1",
        Field_9="Until: 24:00, 0",
    )
