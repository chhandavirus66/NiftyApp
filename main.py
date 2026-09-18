import flet as ft
import requests
import threading
import time

def main(page: ft.Page):
    # ================= UI THEME SETTINGS =================
    page.title = "NIFTY PRO ANALYZER"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0B0F19"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 400  # Mobile screen size ke hisaab se adjust
    page.window_height = 800

    price_history = []
    auto_refresh_active = False

    title_text = ft.Text("NIFTY PRO", size=26, weight=ft.FontWeight.W_900, color=ft.colors.BLUE_400)
    subtitle_text = ft.Text("Live Market Tracker & AI Trade Setup", size=12, color=ft.colors.WHITE54)
    price_text = ft.Text("₹0.00", size=40, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400)
    
    # --- GRAPH COMPONENT ---
    chart_points = []
    chart_series = ft.LineChartData(
        data_points=chart_points, stroke_width=3, color=ft.colors.CYAN_400,
        curved=True, stroke_cap_round=True,
    )
    line_chart = ft.LineChart(
        data_series=[chart_series], border=ft.border.all(1, ft.colors.WHITE10),
        horizontal_grid_lines=ft.ChartGridLines(interval=10, color=ft.colors.WHITE10, width=1),
        vertical_grid_lines=ft.ChartGridLines(interval=1, color=ft.colors.WHITE10, width=1),
        tooltip_bgcolor=ft.colors.BLUE_GREY_900, expand=True,
    )
    chart_container = ft.Container(
        content=line_chart, height=180, width=350, padding=10, 
        bgcolor="#151A28", border_radius=10, visible=False
    )

    # --- OPTIONS DATA ---
    sup_text = ft.Text("--", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_300)
    pcr_text = ft.Text("0.95", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
    res_text = ft.Text("--", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.RED_300)
    
    data_row = ft.Container(
        content=ft.Row([
            ft.Column([ft.Text("SUPPORT", size=10, color=ft.colors.WHITE54), sup_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Column([ft.Text("PCR", size=10, color=ft.colors.WHITE54), pcr_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Column([ft.Text("RESIST", size=10, color=ft.colors.WHITE54), res_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        bgcolor="#151A28", padding=15, border_radius=10, width=350
    )

    # --- AI TRADE SUGGESTION BOX ---
    ai_text = ft.Text("System Ready. Click Live Scan.", size=14, color=ft.colors.WHITE, text_align=ft.TextAlign.CENTER)
    ai_box = ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.icons.SMART_TOY, color=ft.colors.ORANGE_400), ft.Text("AI SUGGESTION", weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE_400)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(color=ft.colors.WHITE10),
            ai_text
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#151A28", padding=15, border_radius=10, width=350,
        border=ft.border.all(1, ft.colors.ORANGE_400)
    )

    # ================= ALL-IN-ONE LOGIC =================
    def fetch_market_data(e=None):
        scan_btn.disabled = True
        ai_text.value = "Fetching Live Data..."
        page.update()
        
        try:
            # 1. Fetching directly from Yahoo Finance (No Backend Needed)
            url = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            res.raise_for_status()
            data = res.json()
            
            meta = data["chart"]["result"][0]["meta"]
            price = meta["regularMarketPrice"]
            prev_close = meta["chartPreviousClose"]
            
            support = round(prev_close * 0.995, 0)
            resistance = round(prev_close * 1.005, 0)
            
            # 2. Update UI Texts
            price_text.value = f"₹{price:,.2f}"
            price_text.color = ft.colors.GREEN_400 if price >= prev_close else ft.colors.RED_400
            sup_text.value = str(support)
            res_text.value = str(resistance)
            
            # 3. Graph Logic
            if price > 0:
                chart_container.visible = True
                price_history.append(price)
                if len(price_history) > 20: price_history.pop(0)
                
                chart_points.clear()
                for i, p in enumerate(price_history): chart_points.append(ft.LineChartDataPoint(i, p))
                
                min_p = min(price_history) - 5
                max_p = max(price_history) + 5
                line_chart.min_y = min_p
                line_chart.max_y = max_p
                line_chart.horizontal_grid_lines.interval = max(1, (max_p - min_p) / 4)

            # 4. Smart AI Logic
            if price > resistance:
                ai_text.value = f"🚀 BREAKOUT! BUY CALL\nEntry: {price} | Target: {price + 45} | SL: {price - 20}"
            elif price < support:
                ai_text.value = f"🔻 BREAKDOWN! BUY PUT\nEntry: {price} | Target: {price - 45} | SL: {price + 20}"
            elif price > prev_close:
                ai_text.value = f"🟢 BULLISH! BUY CALL\nEntry: {price} | Target: {resistance} | SL: {price - 25}"
            else:
                ai_text.value = f"🔴 BEARISH! BUY PUT\nEntry: {price} | Target: {support} | SL: {price + 25}"
            
        except Exception as ex:
            ai_text.value = f"Network Error! Check Internet."
        
        scan_btn.disabled = False
        page.update()

    def auto_refresh_loop():
        while auto_refresh_active:
            fetch_market_data()
            time.sleep(5)

    def toggle_auto_refresh(e):
        nonlocal auto_refresh_active
        auto_refresh_active = auto_switch.value
        if auto_refresh_active:
            scan_btn.disabled = True
            threading.Thread(target=auto_refresh_loop, daemon=True).start()
        else:
            scan_btn.disabled = False
        page.update()

    scan_btn = ft.ElevatedButton("Live Scan Market", icon=ft.icons.RADAR, bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE, on_click=fetch_market_data)
    auto_switch = ft.Switch(label="Auto Refresh (5s)", value=False, on_change=toggle_auto_refresh, active_color=ft.colors.CYAN_400)

    page.add(
        title_text, subtitle_text, ft.Container(height=5),
        ft.Text("CURRENT PRICE", size=10, color=ft.colors.WHITE54), price_text,
        chart_container, ft.Container(height=5), data_row, ft.Container(height=5),
        ai_box, ft.Container(height=10),
        ft.Row([scan_btn, auto_switch], alignment=ft.MainAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    ft.app(target=main)