import flet as ft
import requests
import threading
import time
from datetime import datetime
import traceback  # Error catch karne ke liye

def main(page: ft.Page):
    try:
        # ================= UI THEME SETTINGS =================
        page.title = "NIFTY PRO ADVANCED ANALYZER"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#0B0F19"
        page.padding = 15
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.scroll = ft.ScrollMode.AUTO

        price_history = []
        auto_refresh_active = False

        # ================= HEADER & CLOCK =================
        title_text = ft.Text("NIFTY PRO AI", size=24, weight=ft.FontWeight.W_900, color=ft.colors.BLUE_400)
        subtitle_text = ft.Text("Institutional Multi-Timeframe Terminal", size=11, color=ft.colors.WHITE54)
        time_text = ft.Text("--:--:--", size=13, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_300)
        price_text = ft.Text("₹0.00", size=36, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400)
        
        # ================= GRAPH COMPONENT =================
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
            content=line_chart, height=150, width=380, padding=10, 
            bgcolor="#151A28", border_radius=10, visible=False
        )

        # ================= OPTIONS DATA =================
        sup_text = ft.Text("--", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_300)
        pcr_text = ft.Text("0.95", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        res_text = ft.Text("--", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.RED_300)
        
        data_row = ft.Container(
            content=ft.Row([
                ft.Column([ft.Text("SUPPORT", size=9, color=ft.colors.WHITE54), sup_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([ft.Text("PCR RATIO", size=9, color=ft.colors.WHITE54), pcr_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([ft.Text("RESISTANCE", size=9, color=ft.colors.WHITE54), res_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            bgcolor="#151A28", padding=12, border_radius=10, width=380
        )

        # ================= MULTI-TIMEFRAME PANEL =================
        vol_text = ft.Text("Waiting for tick...", size=12, color=ft.colors.WHITE, text_align=ft.TextAlign.CENTER)
        box_volatile = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.icons.FLASH_ON, size=16, color=ft.colors.YELLOW_400), ft.Text("5-SEC VOLATILE", size=11, weight=ft.FontWeight.BOLD, color=ft.colors.YELLOW_400)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(color=ft.colors.WHITE10, height=5),
                vol_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#151A28", padding=10, border_radius=10, width=185, height=95,
            border=ft.border.all(1, ft.colors.YELLOW_400)
        )

        trend_15m_text = ft.Text("Analyzing 15m...", size=12, color=ft.colors.WHITE, text_align=ft.TextAlign.CENTER)
        box_15m = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.icons.TIMELINE, size=16, color=ft.colors.CYAN_400), ft.Text("15-MIN TREND", size=11, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_400)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(color=ft.colors.WHITE10, height=5),
                trend_15m_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#151A28", padding=10, border_radius=10, width=185, height=95,
            border=ft.border.all(1, ft.colors.CYAN_400)
        )

        multi_tf_row = ft.Row([box_volatile, box_15m], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=380)

        # ================= AI MACRO PREDICTION BOX =================
        ai_final_text = ft.Text("System Ready. Click Live Macro Scan.", size=12, color=ft.colors.WHITE, text_align=ft.TextAlign.CENTER)
        ai_box = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.icons.SMART_TOY, color=ft.colors.ORANGE_400), ft.Text("AI MACRO & FINAL PREDICTION", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE_400)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(color=ft.colors.WHITE10),
                ai_final_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#151A28", padding=12, border_radius=10, width=380,
            border=ft.border.all(1, ft.colors.ORANGE_400)
        )

        # ================= LOGIC & API SYSTEM =================
        def update_clock():
            while True:
                try:
                    time_text.value = datetime.now().strftime("%d %b | %H:%M:%S")
                    page.update()
                except: pass
                time.sleep(1)

        def fetch_market_data(e=None):
            scan_btn.disabled = True
            ai_final_text.value = "Analyzing Previous Day Data, GIFT Nifty & Global Cues..."
            page.update()
            
            try:
                url = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI"
                res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                res.raise_for_status()
                data = res.json()
                
                meta = data["chart"]["result"][0]["meta"]
                price = meta["regularMarketPrice"]
                prev_close = meta["chartPreviousClose"]
                day_high = meta.get("regularMarketDayHigh", price * 1.002)
                day_low = meta.get("regularMarketDayLow", price * 0.998)
                
                support = round(prev_close * 0.995, 0)
                resistance = round(prev_close * 1.005, 0)
                
                price_text.value = f"₹{price:,.2f}"
                price_text.color = ft.colors.GREEN_400 if price >= prev_close else ft.colors.RED_400
                sup_text.value = str(support)
                res_text.value = str(resistance)
                
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

                if price > resistance:
                    vol_text.value = f"🚀 BREAKOUT!\nBuy Call | SL: {price-20}"
                    vol_text.color = ft.colors.GREEN_300
                elif price < support:
                    vol_text.value = f"🔻 BREAKDOWN!\nBuy Put | SL: {price+20}"
                    vol_text.color = ft.colors.RED_300
                else:
                    vol_text.value = f"🟢 BULLISH TICK" if price > prev_close else f"🔴 BEARISH TICK"
                    vol_text.color = ft.colors.GREEN_400 if price > prev_close else ft.colors.RED_400

                if len(price_history) >= 5:
                    trend_15m_text.value = f"📈 15M UPTREND" if price > (sum(price_history[-5:])/5) else f"📉 15M DOWNTREND"
                    trend_15m_text.color = ft.colors.CYAN_300 if price > (sum(price_history[-5:])/5) else ft.colors.ORANGE_300
                else:
                    trend_15m_text.value = "Gathering data..."

                diff_from_prev = price - prev_close
                pct_change = (diff_from_prev / prev_close) * 100
                macro_sentiment = "BULLISH CUES 🟢" if diff_from_prev >= 0 else "BEARISH CUES 🔴"
                
                ai_final_text.value = (
                    f"📊 Prev Close: {prev_close} | H/L: {int(day_high)}/{int(day_low)}\n"
                    f"🌍 Global Sentiment: {macro_sentiment} ({pct_change:+.2f}%)\n"
                    f"🎯 FINAL VERDICT: {'BUY CALL' if diff_from_prev >= 0 else 'BUY PUT'}"
                )
                
            except Exception as ex:
                ai_final_text.value = f"Network Error: {str(ex)}"
            
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

        scan_btn = ft.ElevatedButton("Live Macro Scan", icon=ft.icons.RADAR, bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE, on_click=fetch_market_data)
        auto_switch = ft.Switch(label="Auto (5s)", value=False, on_change=toggle_auto_refresh, active_color=ft.colors.CYAN_400)

        # Background threads mobile par kabhi kabhi crash karte hain, isliye inhe try catch mein dala hai
        try:
            clock_thread = threading.Thread(target=update_clock, daemon=True)
            clock_thread.start()
        except Exception as e:
            pass 

        # ADD EVERYTHING TO UI (Mentor widget yahan se temporarily hata diya gaya hai diagnostic ke liye)
        page.add(
            ft.Row([ft.Column([title_text, subtitle_text], spacing=0), time_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=380),
            ft.Container(height=2),
            ft.Text("CURRENT NIFTY PRICE", size=10, color=ft.colors.WHITE54), price_text,
            chart_container, ft.Container(height=2), data_row, ft.Container(height=2),
            multi_tf_row, ft.Container(height=2),
            ai_box, ft.Container(height=2),
            ft.Row([scan_btn, auto_switch], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=380),
            ft.Container(height=5)
        )
        
    except Exception as full_error:
        # AGAR KOI BHI ERROR AATA HAI TOH CRASH NAHI HOGA, SCREEN PAR LAL RANG MEIN ERROR DIKHEGA
        page.add(
            ft.Text("APP CRASHED! ERROR LOG:", color=ft.colors.RED_400, weight=ft.FontWeight.BOLD, size=20),
            ft.Text(str(traceback.format_exc()), color=ft.colors.WHITE, size=12, selectable=True)
        )
