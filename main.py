import flet as ft
import requests
import threading
import time
import math
import random
from datetime import datetime

def main(page: ft.Page):
    # ================= UI & THEME SETTINGS (MOBILE OPTIMIZED) =================
    page.title = "NIFTY PRO ADVANCED QUANT"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#050914"  # Deep professional dark
    page.padding = 10
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    price_history = []
    auto_refresh_active = False

    # ================= 1. HEADER & LIVE PRICE =================
    header_row = ft.Row(
        [
            ft.Column([
                ft.Text("NIFTY QUANT AI", size=22, weight=ft.FontWeight.W_900, color=ft.colors.BLUE_400),
                ft.Text("Multi-Engine Terminal", size=10, color=ft.colors.WHITE54)
            ], spacing=0),
            ft.Text("--:--:--", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_300)
        ], 
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=380
    )
    
    price_text = ft.Text("₹0.00", size=38, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
    live_status = ft.Text("Waiting for data...", size=12, color=ft.colors.WHITE54)

    # ================= 2. LIVE CHART COMPONENT =================
    chart_points = []
    chart_series = ft.LineChartData(
        data_points=chart_points, stroke_width=2, color=ft.colors.CYAN_400,
        curved=True, stroke_cap_round=True,
    )
    line_chart = ft.LineChart(
        data_series=[chart_series], border=ft.border.all(1, ft.colors.WHITE10),
        horizontal_grid_lines=ft.ChartGridLines(interval=10, color=ft.colors.WHITE10, width=1),
        vertical_grid_lines=ft.ChartGridLines(interval=1, color=ft.colors.WHITE10, width=1),
        tooltip_bgcolor=ft.colors.BLUE_GREY_900, expand=True,
    )
    chart_container = ft.Container(
        content=line_chart, height=130, width=380, padding=10, 
        bgcolor="#0B101E", border_radius=8, visible=False
    )

    # ================= 3. ADVANCED QUANT DATA ROW =================
    def create_data_box(title, val_ref, color):
        return ft.Column([ft.Text(title, size=9, color=ft.colors.WHITE54), val_ref], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    sup_text = ft.Text("--", size=13, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400)
    res_text = ft.Text("--", size=13, weight=ft.FontWeight.BOLD, color=ft.colors.RED_400)
    vix_text = ft.Text("--", size=13, weight=ft.FontWeight.BOLD, color=ft.colors.YELLOW_400)
    atr_text = ft.Text("--", size=13, weight=ft.FontWeight.BOLD, color=ft.colors.PURPLE_300)
    vwap_text = ft.Text("--", size=13, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_300)

    data_row = ft.Container(
        content=ft.Row([
            create_data_box("S1 (PIVOT)", sup_text, ft.colors.GREEN_400),
            create_data_box("R1 (PIVOT)", res_text, ft.colors.RED_400),
            create_data_box("INDIA VIX", vix_text, ft.colors.YELLOW_400),
            create_data_box("ATR (VOL)", atr_text, ft.colors.PURPLE_300),
            create_data_box("VWAP (EST)", vwap_text, ft.colors.BLUE_300),
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        bgcolor="#0B101E", padding=10, border_radius=8, width=380, border=ft.border.all(1, ft.colors.WHITE10)
    )

    # ================= 4. THE 3 AI ENGINES (OUTPUTS) =================
    engine_news_text = ft.Text("Awaiting Macro Scan...", size=11, color=ft.colors.WHITE70)
    engine_tech_text = ft.Text("Awaiting Quant Scan...", size=11, color=ft.colors.WHITE70)
    engine_live_text = ft.Text("Awaiting Price Action...", size=11, color=ft.colors.WHITE70)

    def create_engine_box(title, icon, icon_color, text_ref):
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, size=14, color=icon_color), ft.Text(title, size=10, weight=ft.FontWeight.BOLD, color=icon_color)]),
                text_ref
            ], spacing=2),
            bgcolor="#0B101E", padding=10, border_radius=8, width=380,
            border=ft.border.only(left=ft.border.BorderSide(3, icon_color))
        )

    box_news = create_engine_box("ENGINE 1: MACRO & VIP STATEMENTS", ft.icons.PUBLIC, ft.colors.ORANGE_400, engine_news_text)
    box_tech = create_engine_box("ENGINE 2: QUANT & INDICATORS", ft.icons.DATA_EXPLORATION, ft.colors.PURPLE_400, engine_tech_text)
    box_live = create_engine_box("ENGINE 3: LIVE PRICE ACTION", ft.icons.BOLT, ft.colors.YELLOW_400, engine_live_text)

    # ================= 5. FINAL TRADE PROMPT (VERDICT) =================
    final_verdict_text = ft.Text("RUN LIVE SCAN TO GENERATE SETUP", size=14, weight=ft.FontWeight.W_900, color=ft.colors.WHITE)
    entry_text = ft.Text("ENTRY: --", size=11, color=ft.colors.WHITE)
    target_text = ft.Text("TARGET: --", size=11, color=ft.colors.GREEN_300)
    sl_text = ft.Text("SL: --", size=11, color=ft.colors.RED_300)
    exit_text = ft.Text("EXIT STRATEGY: --", size=11, color=ft.colors.WHITE70)

    final_box = ft.Container(
        content=ft.Column([
            final_verdict_text,
            ft.Divider(color=ft.colors.WHITE24, height=5),
            ft.Row([entry_text, target_text, sl_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            exit_text
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#111B2D", padding=15, border_radius=10, width=380,
        border=ft.border.all(2, ft.colors.BLUE_500)
    )

    # ================= 6. VIP MOCK DATABASE FOR MACRO ENGINE =================
    vip_statements = [
        ("Jerome Powell", "hints at neutral rate policy", "NEUTRAL"),
        ("Shaktikanta Das", "highlights strong domestic liquidity", "BULLISH"),
        ("Donald Trump", "proposes new trade tariffs", "BEARISH"),
        ("Warren Buffett", "accumulates cash, warns on valuations", "BEARISH"),
        ("Jensen Huang", "predicts massive AI infrastructure demand", "BULLISH"),
        ("Christine Lagarde", "ECB remains cautious on inflation", "BEARISH")
    ]

    # ================= 7. CORE MATH & API LOGIC =================
    def update_clock():
        while True:
            try:
                time_text.value = datetime.now().strftime("%d %b | %H:%M:%S")
                page.update()
            except: pass
            time.sleep(1)

    def fetch_market_data(e=None):
        scan_btn.disabled = True
        live_status.value = "Fetching Live & Quant Data..."
        page.update()
        
        try:
            # Fetch Nifty Data
            url_nifty = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI"
            res_nifty = requests.get(url_nifty, headers={"User-Agent": "Mozilla/5.0"}, timeout=5).json()
            meta = res_nifty["chart"]["result"][0]["meta"]
            
            price = meta["regularMarketPrice"]
            prev_close = meta["chartPreviousClose"]
            day_high = meta.get("regularMarketDayHigh", price * 1.002)
            day_low = meta.get("regularMarketDayLow", price * 0.998)
            vol = meta.get("regularMarketVolume", 0)

            # Fetch India VIX (If fails, mock it around 14)
            try:
                res_vix = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/^INDIAVIX", headers={"User-Agent": "Mozilla/5.0"}, timeout=3).json()
                vix_val = res_vix["chart"]["result"][0]["meta"]["regularMarketPrice"]
            except:
                vix_val = 14.50
            
            # --- HIGH MATH FORMULAS ---
            # 1. Pivot Points (Standard)
            pivot = (day_high + day_low + prev_close) / 3
            s1 = (2 * pivot) - day_high
            r1 = (2 * pivot) - day_low
            
            # 2. ATR (Average True Range Approximation)
            atr = max(day_high - day_low, abs(day_high - prev_close), abs(day_low - prev_close))
            
            # 3. Estimated VWAP (Typical Price logic for intraday)
            vwap = (day_high + day_low + price) / 3

            # Update UI Data Row
            price_text.value = f"₹{price:,.2f}"
            price_text.color = ft.colors.GREEN_400 if price >= prev_close else ft.colors.RED_400
            sup_text.value = str(int(s1))
            res_text.value = str(int(r1))
            vix_text.value = str(round(vix_val, 2))
            atr_text.value = str(int(atr))
            vwap_text.value = str(int(vwap))

            # Chart Update
            if price > 0:
                chart_container.visible = True
                price_history.append(price)
                if len(price_history) > 20: price_history.pop(0)
                chart_points.clear()
                for i, p in enumerate(price_history): chart_points.append(ft.LineChartDataPoint(i, p))
                line_chart.min_y = min(price_history) - 5
                line_chart.max_y = max(price_history) + 5

            # --- ENGINE 1: MACRO & VIP NEWS LOGIC ---
            vip = random.choice(vip_statements) # Simulating live AI scraping
            news_sentiment = vip[2]
            engine_news_text.value = f"🗣️ {vip[0]} {vip[1]}.\n🌍 Global sentiment impact: {news_sentiment}."
            
            # --- ENGINE 2: QUANT & MACRO LOGIC ---
            vix_status = "High Fear" if vix_val > 18 else "Stable/Low Risk"
            quant_sentiment = "BULLISH" if price > vwap else "BEARISH"
            engine_tech_text.value = f"📊 VIX at {vix_val:.1f} ({vix_status}). Price is {'above' if price>vwap else 'below'} VWAP.\n📈 15m Trend: {quant_sentiment}."

            # --- ENGINE 3: LIVE PRICE ACTION ---
            if price > r1:
                pa_status = f"Price broke R1 Resistance! Strong Momentum."
                live_sent = "STRONG BUY"
            elif price < s1:
                pa_status = f"Price broke S1 Support! Heavy Selling."
                live_sent = "STRONG SELL"
            else:
                pa_status = f"Price consolidating between {int(s1)} and {int(r1)}."
                live_sent = "NEUTRAL / CHOPPY"
            engine_live_text.value = f"⚡ {pa_status}\nVolume context: {'Active' if vol > 0 else 'Average'}. Sentiment: {live_sent}."

            # --- FINAL PROFESSIONAL PROMPT GENERATION ---
            bullish_score = (1 if news_sentiment=="BULLISH" else 0) + (1 if quant_sentiment=="BULLISH" else 0) + (1 if "BUY" in live_sent else 0)
            bearish_score = (1 if news_sentiment=="BEARISH" else 0) + (1 if quant_sentiment=="BEARISH" else 0) + (1 if "SELL" in live_sent else 0)

            if bullish_score >= 2:
                final_verdict_text.value = "🟢 FINAL VERDICT: BUY CALL"
                final_verdict_text.color = ft.colors.GREEN_400
                final_box.border = ft.border.all(2, ft.colors.GREEN_500)
                entry_text.value = f"ENTRY: CMP or {int(vwap)}"
                target_text.value = f"TARGET: {int(price + atr)}"
                sl_text.value = f"SL: {int(price - (atr/2))}"
                exit_text.value = "EXIT STRATEGY: Trail SL if price crosses Target 1. Exit if India VIX spikes above 18."
            elif bearish_score >= 2:
                final_verdict_text.value = "🔴 FINAL VERDICT: BUY PUT"
                final_verdict_text.color = ft.colors.RED_400
                final_box.border = ft.border.all(2, ft.colors.RED_500)
                entry_text.value = f"ENTRY: CMP or {int(vwap)}"
                target_text.value = f"TARGET: {int(price - atr)}"
                sl_text.value = f"SL: {int(price + (atr/2))}"
                exit_text.value = "EXIT STRATEGY: Book 50% at Target. Exit immediately if price reclaims VWAP."
            else:
                final_verdict_text.value = "🟡 FINAL VERDICT: NO TRADE ZONE"
                final_verdict_text.color = ft.colors.YELLOW_400
                final_box.border = ft.border.all(2, ft.colors.YELLOW_500)
                entry_text.value = "ENTRY: Await Breakout"
                target_text.value = f"UPPER LEVEL: {int(r1)}"
                sl_text.value = f"LOWER LEVEL: {int(s1)}"
                exit_text.value = "EXIT STRATEGY: Market is choppy (Premium decay risk). Wait for clear trend."

            live_status.value = "Data Synced Successfully."
            
        except Exception as e:
            live_status.value = f"Network/Data Error!"
        
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

    # ================= 8. CONTROLS & CHAT UI =================
    scan_btn = ft.ElevatedButton("RUN FULL QUANT SCAN", icon=ft.icons.RADAR, bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE, on_click=fetch_market_data)
    auto_switch = ft.Switch(label="Auto (5s)", value=False, on_change=toggle_auto_refresh, active_color=ft.colors.CYAN_400)

    chat_list = ft.ListView(expand=True, spacing=5, height=100, auto_scroll=True)
    chat_list.controls.append(ft.Text("🤖 Nifty Guru: Terminal ready. Type query...", size=11, color=ft.colors.CYAN_200))
    
    def send_ai_message(e):
        if not user_input.value: return
        query = user_input.value.lower()
        chat_list.controls.append(ft.Text(f"👤: {user_input.value}", size=11, color=ft.colors.WHITE))
        user_input.value = ""
        page.update()
        time.sleep(0.5) 
        ai_reply = "🤖 Nifty Guru: Analyzing macro variables... (Connect Gemini API here)"
        chat_list.controls.append(ft.Text(ai_reply, size=11, color=ft.colors.CYAN_200))
        page.update()

    user_input = ft.TextField(hint_text="Ask AI...", expand=True, bgcolor="#0B101E", border_color=ft.colors.WHITE24, text_size=11, height=35, content_padding=5, on_submit=send_ai_message)
    send_btn_chat = ft.IconButton(icon=ft.icons.SEND, icon_size=16, icon_color=ft.colors.BLUE_400, on_click=send_ai_message)

    assistant_box = ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.icons.SUPPORT_AGENT, size=14, color=ft.colors.BLUE_300), ft.Text("AI TRADING MENTOR", size=10, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_300)]),
            chat_list, ft.Row([user_input, send_btn_chat])
        ]),
        bgcolor="#0B101E", padding=10, border_radius=8, width=380, border=ft.border.all(1, ft.colors.BLUE_800)
    )

    try:
        threading.Thread(target=update_clock, daemon=True).start()
    except: pass

    # ================= 9. ASSEMBLE ENTIRE UI =================
    page.add(
        header_row,
        ft.Row([price_text, live_status], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=380),
        chart_container, 
        data_row,
        box_news, box_tech, box_live,
        final_box,
        ft.Row([scan_btn, auto_switch], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=380),
        assistant_box
    )
    
