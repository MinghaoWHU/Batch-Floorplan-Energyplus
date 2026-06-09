import traceback
import config
from src.io_utils import ensure_dir, get_finished_indices, append_summary_row
from src.simulation import simulate_one_case


def run_batch_once():
    ensure_dir(config.ROOT_DIR)
    ensure_dir(config.TEMP_RUN_DIR)

    for deg in config.DEGREES:
        degree_dir = ensure_dir(config.ROOT_DIR / str(deg))
        finished_idxs = get_finished_indices(degree_dir, config.MAX_ID)
        start_idx = max(finished_idxs + [config.start_idx])

        for idx in range(start_idx, start_idx + config.BATCH_SIZE_PER_DEGREE):
            if idx in finished_idxs or idx > config.MAX_ID:
                continue

            dxf_path = config.DXF_DIR / f"output_{idx}.dxf"
            if not dxf_path.exists():
                continue

            try:
                summary = simulate_one_case(idx=idx, deg=deg, config_module=config)
                if summary is not None:
                    append_summary_row(config.SUMMARY_CSV, summary)
            except Exception:
                print(f"[失败] idx={idx}, deg={deg}")
                traceback.print_exc()


def run_batch(repeat_times=1000):
    for round_id in range(1, repeat_times + 1):
        print("\n" + "=" * 80)
        print(f"开始第 {round_id}/{repeat_times} 轮批量模拟")
        print("=" * 80)

        run_batch_once()

        print("\n" + "-" * 80)
        print(f"第 {round_id}/{repeat_times} 轮结束")
        print("-" * 80)


if __name__ == "__main__":
    run_batch(repeat_times=1000)