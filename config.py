from pathlib import Path

# =========================================================
# Project paths
# =========================================================
ROOT_DIR = Path(r"D:/LMH/energy_consumption5")
DXF_DIR = Path(r"D:/LMH/NEW_PLAN")
CONSTRUCTION_DIR = Path(r"construction")

IDD_PATH = Path(r"Energy+.idd")
BASE_IDF_PATH = Path(r"Minimal.idf")
EPW_PATH = Path(r"CHN_Hubei.Wuhan.574940_CSWD.epw")

# =========================================================
# Batch settings
# =========================================================
DEGREES = [0]
start_idx = 15078
MAX_ID = 20000
BATCH_SIZE_PER_DEGREE = 100

# =========================================================
# Building settings
# =========================================================
NUM_STORIES = 3
STOREY_HEIGHT = 2.5
LIGHTING_POWER_DENSITY = 5.0

# =========================================================
# Output settings
# =========================================================
SUMMARY_CSV = ROOT_DIR / "summary_results.csv"
TEMP_RUN_DIR = ROOT_DIR / "_energyplus_runs"
