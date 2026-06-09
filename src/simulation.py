import json
from pathlib import Path
import pandas as pd
from .dxf_reader import dxf_to_layer_geometries
from .model_builder import build_idf_from_plan
import shutil

def simulate_one_case(idx: int, deg: float, config_module):
    dxf_path = config_module.DXF_DIR / f"output_{idx}.dxf"
    if not dxf_path.exists():
        return None

    print(f"+++++++++++++++++++++++ {idx} | deg={deg} +++++++++++++++++++++++")
    plan_dic, total_area, bedroom_area, living_area = dxf_to_layer_geometries(dxf_path)

    if "living" not in plan_dic:
        print(f"[跳过] output_{idx}.dxf 没有 living 图层")
        return None

    idf, plan_json, envelope = build_idf_from_plan(plan_dic, deg, config_module)
    sid = envelope.get("id", "")

    output_dir = config_module.ROOT_DIR / str(deg)
    output_dir.mkdir(parents=True, exist_ok=True)

    case_name = f"{idx}_{sid}_{deg}_"
    run_dir = config_module.TEMP_RUN_DIR / f"{idx}_{sid}_{deg}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Some geomeppy/eppy versions support output_directory. If not, fall back to cwd output.
    try:
        idf.run(readvars=True, output_directory=str(run_dir))
        eplus_csv = run_dir / "eplusout.csv"
    except TypeError:
        idf.run(readvars=True)
        eplus_csv = Path("eplusout.csv")

    if not eplus_csv.exists():
        raise FileNotFoundError(f"未找到 EnergyPlus 输出 CSV: {eplus_csv}")

    df = pd.read_csv(eplus_csv)

    idf_path = output_dir / f"{case_name}.idf"
    csv_path = output_dir / f"{case_name}.csv"
    json_path = output_dir / f"{case_name}.json"

    idf.saveas(str(idf_path))
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(plan_json, f, ensure_ascii=False, indent=2)

    summary = summarize_energy(
        df=df,
        idx=idx,
        sid=sid,
        deg=deg,
        total_area=total_area,
        bedroom_area=bedroom_area,
        living_area=living_area,
        idf_path=idf_path,
        csv_path=csv_path,
        json_path=json_path,
    )

    print("===" * 10)
    print(case_name, summary["bedroom_eui"], summary["living_eui"], summary["total_eui"])
    # 删除 EnergyPlus 临时运行目录
    if run_dir.exists():
        shutil.rmtree(run_dir, ignore_errors=True)
        print(f"[已删除临时目录] {run_dir}")
    return summary


def summarize_energy(
    df: pd.DataFrame,
    idx: int,
    sid: str,
    deg: float,
    total_area: float,
    bedroom_area: float,
    living_area: float,
    idf_path: Path,
    csv_path: Path,
    json_path: Path,
):
    ideal_cols = [col for col in df.columns if "Zone Ideal Loads" in col]
    bedroom_cols = [col for col in ideal_cols if "BEDROOM" in col.upper()]
    living_cols = [col for col in ideal_cols if "LIVING" in col.upper()]

    total_eui = safe_eui(df, ideal_cols, total_area)
    bedroom_eui = safe_eui(df, bedroom_cols, bedroom_area)
    living_eui = safe_eui(df, living_cols, living_area)

    return {
        "idx": idx,
        "scenario_id": sid,
        "degree": deg,
        "total_area": total_area,
        "bedroom_area": bedroom_area,
        "living_area": living_area,
        "bedroom_eui": bedroom_eui,
        "living_eui": living_eui,
        "total_eui": total_eui,
        "idf_path": str(idf_path),
        "csv_path": str(csv_path),
        "json_path": str(json_path),
    }


def safe_eui(df: pd.DataFrame, cols: list, area: float):
    if not cols or area <= 0:
        return None
    return df[cols].sum().sum() / 3600000 / 2 / area / 2.5
