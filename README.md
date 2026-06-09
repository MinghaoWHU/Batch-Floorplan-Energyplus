# EnergyPlus DXF Batch Simulation Project

# EnergyPlus DXF 批量仿真项目

The original script included DXF reading, geometry processing, IDF construction, thermal zone generation, window and door creation, simulation execution, and result aggregation in one file.
原脚本同时包含 DXF 读取、几何处理、IDF 构建、房间热区生成、窗门写入、仿真运行和结果汇总。

The current version separates each function into an independent module.
当前版本将各功能拆分为独立模块。

This structure makes the project easier to modify, debug, and reuse.
该结构便于后续修改、调试和复用。

---

## 1. Project Structure

## 1. 项目结构

```text
energyplus_batch_project/
├─ main.py                         # Batch running entry / 批量运行入口
├─ config.py                       # Paths, angles, floors, and batch settings / 路径、角度、楼层、批量参数设置
├─ requirements.txt                # Required Python packages / 依赖库
├─ README.md                       # Project description / 项目说明
└─ src/
   ├─ __init__.py
   ├─ io_utils.py                  # Folder creation, completed IDs, and summary aggregation / 文件夹、已完成编号、summary 汇总
   ├─ dxf_reader.py                # DXF to Shapely geometry / DXF → Shapely geometry
   ├─ geometry_utils.py            # Geometry functions for doors, windows, normals, projection, and sampling points / 门窗、法向、投影、采样点等几何函数
   ├─ envelope.py                  # Randomly load construction/*.json / 随机读取 construction/*.json
   ├─ schedules.py                 # Thermostat and lighting schedules / 温控、照明 schedule
   ├─ constructions.py             # Envelope materials and constructions / 围护结构材料与构造
   ├─ zone_builder.py              # Room polygon to Zone, Surface, HVAC, and Lighting / 房间 polygon → Zone/Surface/HVAC/Lighting
   ├─ balcony.py                   # Balcony shading surfaces / 阳台遮阳面
   ├─ fenestration.py              # Add windows and doors to IDF / 窗户和门写入 IDF
   ├─ model_builder.py             # Assemble the complete IDF model / 组装完整 IDF
   └─ simulation.py                # Single-case simulation, output processing, and energy summary / 单个案例仿真、输出、能耗汇总
```

---

## 2. How to Run

## 2. 运行方式

Before running the project, check the following paths in `config.py`.
运行项目前，请先在 `config.py` 中检查以下路径。

```python
ROOT_DIR = Path(r"D:/LMH/energy_consumption4")
DXF_DIR = Path(r"D:/LMH/NEW_PLAN")
CONSTRUCTION_DIR = Path(r"construction")
IDD_PATH = Path(r"Energy+.idd")
BASE_IDF_PATH = Path(r"Minimal.idf")
EPW_PATH = Path(r"CHN_Hubei.Wuhan.574940_CSWD.epw")
```

Then run the project from the root directory.
然后在项目根目录运行以下命令。

```bash
python main.py
```

---

## 3. Output Files

## 3. 输出文件

For each rotation angle, the output files are saved under `ROOT_DIR/degree/`.
每个角度的输出文件会保存在 `ROOT_DIR/角度/` 文件夹下。

```text
{idx}_{scenario_id}_{degree}_{area}.idf
{idx}_{scenario_id}_{degree}_{area}_ec.csv
{idx}_{scenario_id}_{degree}_plan.json
```

The summary results of all simulated cases are appended to the following file.
所有案例的汇总结果会追加保存到以下文件中。

```text
ROOT_DIR/summary_results.csv
```

---

## 4. Main Updates Compared with the Original Script

## 4. 相比原脚本的主要修正

1. `merge_and_check()` no longer directly deletes `plan_dic['balcony']`.
   `merge_and_check()` 不再直接删除 `plan_dic['balcony']`。

   This avoids affecting later balcony processing.
   这样可以避免影响后续阳台处理。

2. The coordinate matching in `add_window_by_coords()` was replaced by a more robust X/Y wall-surface check.
   `add_window_by_coords()` 中的墙体坐标匹配改为更稳健的 X/Y 墙面判断。

3. The living room energy summary column was corrected from `BEDROOM` to `LIVING`.
   客厅能耗汇总列由原脚本中的 `BEDROOM` 修正为 `LIVING`。

4. Temporary EnergyPlus running files are saved under `ROOT_DIR/_energyplus_runs/` by default.
   EnergyPlus 临时运行结果默认保存到 `ROOT_DIR/_energyplus_runs/`。

---

## 5. Suggested Future Extensions

## 5. 后续扩展建议

1. Fixed envelope scenarios can be tested by modifying `load_random_envelope()`.
   如果需要测试固定围护结构方案，可以修改 `load_random_envelope()`。

   The function can be changed from random loading to loading a specified `scenario_id`.
   可以将该函数由随机读取改为按指定 `scenario_id` 读取。

2. Parallel simulation can be added in `main.py` with `ProcessPoolExecutor`.
   如果需要并行仿真，可以在 `main.py` 中使用 `ProcessPoolExecutor`。

   Each EnergyPlus run must use a separate output directory.
   但需要注意，每个 EnergyPlus 仿真必须使用独立的输出目录。

3. Optimization algorithms can be added in a new `optimizer.py` module.
   如果需要加入优化算法，可以新增 `optimizer.py` 模块。

   The optimizer can call `simulate_one_case()` as the simulation interface.
   优化模块可以调用 `simulate_one_case()` 作为仿真接口。

---

## 6. Notes

## 6. 注意事项

Make sure that EnergyPlus is correctly installed before running the project.
运行项目前，请确认 EnergyPlus 已正确安装。

Make sure that `Energy+.idd`, `Minimal.idf`, and the weather file are available at the paths specified in `config.py`.
请确认 `Energy+.idd`、`Minimal.idf` 和气象文件位于 `config.py` 中指定的路径。

If the project stops unexpectedly, check the temporary EnergyPlus output folder and the console error message.
如果项目运行中断，请检查 EnergyPlus 临时输出文件夹和终端报错信息。

If some DXF files fail to generate valid rooms, check the layer names, polygon closure, and geometric validity of the original CAD drawings.
如果部分 DXF 文件无法生成有效房间，请检查原始 CAD 图中的图层名称、房间闭合情况和几何有效性。
