def add_constructions(idf, envelope: dict):
    """Add envelope materials and constructions from one JSON scenario."""
    add_opaque_material_and_construction(
        idf,
        material_name="wall_U1_Layer",
        construction_name="wall_U1",
        roughness="MediumSmooth",
        spec=envelope["wall"],
    )

    add_opaque_material_and_construction(
        idf,
        material_name="roof_U1_Layer",
        construction_name="roof_U1",
        roughness="MediumRough",
        spec=envelope["roof"],
    )

    add_opaque_material_and_construction(
        idf,
        material_name="floor_U1_Layer",
        construction_name="floor_U1",
        roughness="MediumRough",
        spec=envelope["floor"],
    )

    idf.newidfobject(
        "MATERIAL",
        Name="ceiling_U1_Layer",
        Roughness="MediumRough",
        Thickness=0.20,
        Conductivity=1.40,
        Density=2300,
        Specific_Heat=900,
    )
    idf.newidfobject(
        "CONSTRUCTION",
        Name="ceiling_U1",
        Outside_Layer="ceiling_U1_Layer",
    )

    add_opaque_material_and_construction(
        idf,
        material_name="InteriorWall_U05_Layer",
        construction_name="InteriorWall_U05",
        roughness="MediumSmooth",
        spec=envelope["interior_wall"],
    )

    idf.newidfobject(
        "WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM",
        Name="Window_U25",
        UFactor=envelope["window"]["u_factor"],
        Solar_Heat_Gain_Coefficient=envelope["window"]["shgc"],
        Visible_Transmittance=envelope["window"]["vt"],
    )
    idf.newidfobject(
        "CONSTRUCTION",
        Name="WindowConstruction_U25",
        Outside_Layer="Window_U25",
    )


def add_opaque_material_and_construction(idf, material_name: str, construction_name: str, roughness: str, spec: dict):
    idf.newidfobject(
        "MATERIAL",
        Name=material_name,
        Roughness=roughness,
        Thickness=spec["thickness"],
        Conductivity=spec["conductivity"],
        Density=spec["density"],
        Specific_Heat=spec["specific_heat"],
    )
    idf.newidfobject(
        "CONSTRUCTION",
        Name=construction_name,
        Outside_Layer=material_name,
    )
