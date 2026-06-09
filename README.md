# EnergyPlus DXF Batch Simulation Project

这个项目由原来的单文件脚本拆分而来。原脚本同时包含 DXF 读取、几何处理、IDF 构建、房间热区生成、窗门写入、仿真运行和结果汇总。现在每一部分被拆成独立模块，便于后续修改、调试和复用。

## 1. 项目结构

```text
energyplus_batch_project/
├─ main.py                         # 批量运行入口
├─ config.py                       # 路径、角度、楼层、批量参数设置
├─ requirements.txt                # 依赖库
├─ README.md
└─ src/
   ├─ __init__.py
   ├─ io_utils.py                  # 文件夹、已完成编号、summary 汇总
   ├─ dxf_reader.py                # DXF → Shapely geometry
   ├─ geometry_utils.py            # 门窗、法向、投影、采样点等几何函数
   ├─ envelope.py                  # 随机读取 construction/*.json
   ├─ schedules.py                 # 温控、照明 schedule
   ├─ constructions.py             # 围护结构材料与构造
   ├─ zone_builder.py              # 房间 polygon → Zone/Surface/HVAC/Lighting
   ├─ balcony.py                   # 阳台遮阳面
   ├─ fenestration.py              # 窗户和门写入 IDF
   ├─ model_builder.py             # 组装完整 IDF
   └─ simulation.py                # 单个案例仿真、输出、能耗汇总
```

## 2. 运行方式

先在 `config.py` 里检查这些路径：

```python
ROOT_DIR = Path(r"D:/LMH/energy_consumption4")
DXF_DIR = Path(r"D:/LMH/NEW_PLAN")
CONSTRUCTION_DIR = Path(r"construction")
IDD_PATH = Path(r"Energy+.idd")
BASE_IDF_PATH = Path(r"Minimal.idf")
EPW_PATH = Path(r"CHN_Hubei.Wuhan.574940_CSWD.epw")
```

然后在项目根目录运行：

```bash
python main.py
```

## 3. 输出文件

每个角度会在 `ROOT_DIR/角度/` 下输出：

```text
{idx}_{scenario_id}_{degree}_{area}.idf
{idx}_{scenario_id}_{degree}_{area}_ec.csv
{idx}_{scenario_id}_{degree}_plan.json
```

同时会在 `ROOT_DIR/summary_results.csv` 中追加保存每个案例的汇总结果。

## 4. 相比原脚本的小修正

1. `merge_and_check()` 不再直接删除 `plan_dic['balcony']`，避免影响后续阳台处理。
2. `add_window_by_coords()` 中墙体匹配的坐标判断改为更稳健的 X/Y 墙面判断。
3. 客厅能耗汇总列由原脚本中的 `BEDROOM` 修正为 `LIVING`。
4. EnergyPlus 临时运行结果默认放入 `ROOT_DIR/_energyplus_runs/`。

## 5. 后续扩展建议

- 如果要测试固定围护结构方案，可以把 `load_random_envelope()` 改为按指定 `scenario_id` 读取。
- 如果要并行仿真，可以在 `main.py` 中改为 `ProcessPoolExecutor`，但要注意 EnergyPlus 输出目录必须分开。
- 如果要加入优化算法，可以单独新增 `optimizer.py`，再调用 `simulate_one_case()`。
