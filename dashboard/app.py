from pathlib import Path
from shiny import App, render, ui, reactive
import pandas as pd

from dashboard.shared import RealTimeStreamer
from modules import tab1, tab2, tab3

streamer = RealTimeStreamer()
shared_df = reactive.Value(pd.DataFrame())
streaming_active = reactive.Value(False)  # ✅ 스트리밍 상태 공유

app_ui = ui.page_fluid(
    ui.h1("Casting Process 실시간 대시보드"),
    ui.navset_tab(
        ui.nav_panel("현장 운영 담당자", tab1.tab_ui),
        ui.nav_panel("품질관리팀", tab2.tab_ui),
        ui.nav_panel("데이터 분석가", tab3.tab_ui),
    ),
)

def server(input, output, session):
    last_index = reactive.Value(0)
    
    @reactive.effect
    def _global_auto_update():
        reactive.invalidate_later(streamer.interval_sec)
        
        if streamer.is_running:
            current_idx = streamer.get_last_update_time()
            if current_idx != last_index.get():
                last_index.set(current_idx)
                shared_df.set(streamer.get_current_data())
                streaming_active.set(True)
        else:
            streaming_active.set(False)

    # ✅ 각 탭에 공유 상태 전달
    tab1.tab_server(input, output, session, streamer, shared_df, streaming_active)
    tab2.tab_server(input, output, session, streamer, shared_df, streaming_active)
    tab3.tab_server(input, output, session, streamer, shared_df, streaming_active)

static_path = Path(__file__).parent / "data" / "png"
app = App(app_ui, server, static_assets=str(static_path))