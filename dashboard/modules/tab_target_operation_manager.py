# dashboard/modules/tab_target_operation_manager.py
from shiny import ui, render, reactive, Inputs, Outputs, Session
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# Path settings
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "test.csv"

# Data preparation
df = pd.read_csv(DATA_FILE, encoding="utf-8", low_memory=False)

# ==========================================================
# UI 정의
# ==========================================================
tab_ui = ui.div(
    ui.tags.style("""
        /* ===== 공통 설정 ===== */
        ::-webkit-scrollbar { display: none; }
        * { scrollbar-width: none; }
        * { -ms-overflow-style: none; }
        body { overflow-y: scroll; overflow-x: hidden; }
        .main-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px 40px;
        }

        /* ===== KPI 카드 디자인 ===== */
        .kpi-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.15);
        }
        .kpi-title {
            font-size: 15px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        .kpi-line {
            width: 60%;
            height: 3px;
            margin: 0 auto 15px auto;
            border-radius: 2px;
        }
        .red-line { background-color: #d9534f; }
        .yellow-line { background-color: #f0ad4e; }
        .navy-line { background-color: #2c3e50; }
        .kpi-value {
            font-size: 28px;
            font-weight: 700;
            color: #111;
            margin-bottom: 8px;
        }
        .kpi-sub {
            font-size: 13px;
            color: #777;
        }

        /* ===== 상태표시등 전체 컨테이너 ===== */
        .status-panel {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: flex-start;
            height: 200px;
            gap: 22px;
            padding-left: 20px;
        }

        /* ===== 각 상태표시등 행 ===== */
        .status-row {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 14px;
        }

        /* ===== 신호등 기본 스타일 ===== */
        .status-indicator-circle {
            width: 55px;
            height: 55px;
            border-radius: 50%;
            border: 3px solid #333;
            flex-shrink: 0;
            transition: all 0.3s ease;
        }

        /* ===== 개별 신호등 색상 ===== */
        #lof_indicator {
            background-color: #C00000;   /* 🔴 위험 (LOF 이상) */
            box-shadow: 0 0 22px rgba(192,0,0,0.55);
        }
        #process_indicator {
            background-color: #3B7D23;   /* 🟢 관리도 이상 */
            box-shadow: 0 0 20px rgba(59,125,35,0.5);
        }
        #defect_indicator {
            background-color: #3B7D23;   /* 🟢 불량 발생 */
            box-shadow: 0 0 20px rgba(59,125,35,0.5);
        }

        /* ===== 텍스트 라벨 ===== */
        .status-indicator-label {
            font-size: 16px;
            font-weight: 700;
            color: #111;
            line-height: 1;
            white-space: nowrap;
        }
    """),

    # ===== 전체 레이아웃 =====
    ui.div(
        ui.layout_columns(
            # 왼쪽 KPI 카드
            ui.div(
                ui.layout_columns(
                    ui.div(
                        ui.p("금형별 수율", class_="kpi-title"),
                        ui.div(class_="kpi-line red-line"),
                        ui.h1("95.5%", class_="kpi-value"),
                        ui.p("open tickets | 16% of total", class_="kpi-sub"),
                        class_="kpi-card"
                    ),
                    ui.div(
                        ui.p("제품 사이클 타임", class_="kpi-title"),
                        ui.div(class_="kpi-line yellow-line"),
                        ui.h1("12.3 sec", class_="kpi-value"),
                        ui.p("open tickets | 21% of total", class_="kpi-sub"),
                        class_="kpi-card"
                    ),
                    ui.div(
                        ui.p("설비 가동률", class_="kpi-title"),
                        ui.div(class_="kpi-line navy-line"),
                        ui.h1("87.2%", class_="kpi-value"),
                        ui.p("open tickets | 31% of total", class_="kpi-sub"),
                        class_="kpi-card"
                    ),
                    col_widths=[4, 4, 4]
                ),
                style="flex: 3;"
            ),

            # 오른쪽 신호등
            ui.div(
                ui.div(
                    ui.div(
                        ui.div(id="lof_indicator", class_="status-indicator-circle"),
                        ui.div("이상치 발생", class_="status-indicator-label"),
                        class_="status-row"
                    ),
                    ui.div(
                        ui.div(id="process_indicator", class_="status-indicator-circle"),
                        ui.div("관리도 이상", class_="status-indicator-label"),
                        class_="status-row"
                    ),
                    ui.div(
                        ui.div(id="defect_indicator", class_="status-indicator-circle"),
                        ui.div("불량 발생", class_="status-indicator-label"),
                        class_="status-row"
                    ),
                    class_="status-panel"
                ),
                style="flex: 1; text-align: left;"
            ),
            col_widths=[9, 3]
        ),

        # 검색 영역
        ui.card(
            ui.card_header("검색 및 설정"),
            ui.layout_columns(
                ui.input_text("mold_code", "Mold Code 검색", placeholder="Mold Code를 입력하세요"),
                ui.input_text("variable_setting", "변수 설정", placeholder="변수를 입력하세요"),
                col_widths=[6, 6]
            )
        ),

        # 런 차트
        ui.card(
            ui.card_header("런 차트"),
            ui.output_plot("plot_realtime")
        ),

        # Top 10 로그
        ui.card(
            ui.card_header("Top 10 로그"),
            ui.output_table("table_kpi")
        ),
        class_="main-container"
    )
)


# ==========================================================
# SERVER 정의
# ==========================================================
def tab_server(input: Inputs, output: Outputs, session: Session):
    """Target Operation Manager 탭 서버 로직"""

    def generate_sample_data():
        n_points = 100
        timestamps = pd.date_range(start=datetime.now(), periods=n_points, freq='1min')
        data = pd.DataFrame({
            'timestamp': timestamps,
            'mold_code': np.random.choice(['M001', 'M002', 'M003', 'M004', 'M005'], n_points),
            'yield_rate': np.random.uniform(85, 99, n_points),
            'cycle_time': np.random.uniform(10, 15, n_points),
            'temperature': np.random.uniform(180, 220, n_points),
            'pressure': np.random.uniform(80, 120, n_points)
        })
        return data

    data_store = reactive.Value(generate_sample_data())

    @output
    @render.plot
    def plot_realtime():
        df = data_store()
        mold_filter = input.mold_code()
        if mold_filter and mold_filter.strip():
            df_filtered = df[df['mold_code'] == mold_filter.upper()]
            if df_filtered.empty:
                df_filtered = df
        else:
            df_filtered = df

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Real-time Monitoring Dashboard', fontsize=16)

        for i, (col, title, marker) in enumerate([
            ('yield_rate', 'Yield Rate (%)', 'o'),
            ('cycle_time', 'Cycle Time (sec)', 's'),
            ('temperature', 'Temperature (°C)', '^'),
            ('pressure', 'Pressure (bar)', 'd')
        ]):
            ax = axes[i // 2, i % 2]
            for mold in df_filtered['mold_code'].unique():
                mold_data = df_filtered[df_filtered['mold_code'] == mold]
                ax.plot(mold_data.index[:20], mold_data[col][:20],
                        label=mold, marker=marker, markersize=3)
            ax.set_title(title)
            ax.legend(loc='best', fontsize=8)
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    @output
    @render.table
    def table_kpi():
        df = data_store()
        kpi_df = df.groupby('mold_code').agg({
            'yield_rate': ['mean', 'min', 'max', 'std'],
            'cycle_time': 'mean',
            'temperature': 'mean',
            'pressure': 'mean'
        }).round(2)
        kpi_df.columns = ['Avg Yield', 'Min Yield', 'Max Yield', 'Std Yield',
                          'Avg Cycle Time', 'Avg Temp', 'Avg Pressure']
        kpi_df = kpi_df.reset_index().rename(columns={'mold_code': 'Mold Code'})
        return kpi_df.head(10)

    @reactive.Effect
    def update_data():
        reactive.invalidate_later(5000)
        data_store.set(generate_sample_data())
