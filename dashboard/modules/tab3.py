from shiny import ui, render, reactive
import pandas as pd

tab_ui = ui.page_fluid(
    ui.h2("데이터 분석가 탭"),
    ui.p("아래 버튼으로 데이터 스트리밍을 제어할 수 있습니다."),
    ui.row(
        ui.column(4, ui.input_action_button("tab3_start_btn", "▶ 시작", class_="btn btn-success w-100")),
        ui.column(4, ui.input_action_button("tab3_stop_btn", "⏸ 정지", class_="btn btn-warning w-100")),
        ui.column(4, ui.input_action_button("tab3_reset_btn", "🔁 리셋", class_="btn btn-danger w-100")),
    ),
    ui.hr(),
    ui.output_text("tab3_progress_text"),
    ui.output_table("tab3_table_realtime"),
)

def tab_server(input, output, session, streamer, shared_df, streaming_active):

    @reactive.effect
    @reactive.event(input.tab3_start_btn)
    def _on_start():
        streamer.start_stream()
        streaming_active.set(True)

    @reactive.effect
    @reactive.event(input.tab3_stop_btn)
    def _on_stop():
        streamer.stop_stream()
        streaming_active.set(False)

    @reactive.effect
    @reactive.event(input.tab3_reset_btn)
    def _on_reset():
        streamer.reset_stream()
        shared_df.set(pd.DataFrame())
        streaming_active.set(False)

    @output
    @render.text
    def tab3_progress_text():
        status = streaming_active.get()
        _ = shared_df.get()
        status_text = "진행 중" if status else "정지"
        return f"상태: {status_text} | 진행률: {streamer.progress():.1f}%"

    @output
    @render.table
    def tab3_table_realtime():
        df = shared_df.get()
        
        if df.empty:
            return pd.DataFrame({"메시지": ["데이터를 불러오는 중..."]})
        
        result = df.tail(10).drop(columns=['line', 'name', 'mold_name'], errors='ignore')
        return result