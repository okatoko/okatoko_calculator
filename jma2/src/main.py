import flet as ft
import requests
import sqlite3
from datetime import datetime

# APIのエンドポイントURL
AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json"

def init_db():
    conn = sqlite3.connect("weather_forecast.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT,
            parent_code TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT,
            date TEXT,
            weather_code TEXT,
            temp_min TEXT,
            temp_max TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_area_data(areas):
    conn = sqlite3.connect("weather_forecast.db")
    cursor = conn.cursor()

    for region_code, region in areas['centers'].items():
        for pref in region["children"]:
            if pref in areas["offices"]:
                cursor.execute("""
                    INSERT OR IGNORE INTO areas (code, name, parent_code) VALUES (?, ?, ?)
                """, (pref, areas["offices"][pref]["name"], region_code))

    conn.commit()
    conn.close()

def save_forecast_data(area_code, forecast_data):
    print(f"Saving forecast data for area_code: {area_code}")
    conn = sqlite3.connect("weather_forecast.db")
    cursor = conn.cursor()

    date_index = 0
    for series in forecast_data:
        if "timeSeries" in series:
            for ts in series["timeSeries"]:
                for time_define in ts["timeDefines"]:
                    weather_code = 'N/A'
                    temp_min_value = 'N/A'
                    temp_max_value = 'N/A'

                    if 'areas' in ts:
                        for area in ts["areas"]:
                            if 'weatherCodes' in ts and date_index < len(ts['weatherCodes']):
                                weather_code = ts['weatherCodes'][date_index]

                            if 'tempsMin' in ts and date_index < len(ts['tempsMin']):
                                temp_min_value = (ts['tempsMin'][date_index])
                            if 'tempsMax' in ts and date_index < len(ts['tempsMax']):
                                temp_max_value = (ts['tempsMax'][date_index])

                    date = time_define.split("T")[0]
                    print(f"Inserting data: {area_code, date, weather_code, temp_min_value, temp_max_value}")
                    cursor.execute("""
                        INSERT OR REPLACE INTO forecasts (area_code, date, weather_code, temp_min, temp_max)
                        VALUES (?, ?, ?, ?, ?)
                    """, (area_code, date, weather_code, temp_min_value, temp_max_value))
                    date_index += 1

    conn.commit()
    conn.close()

def main(page: ft.Page):
    page.spacing = 0
    page.padding = 0

    page.bgcolor = "#87CEFA"
    page.horizontal_alignment = "stretch"
    page.padding = 0
    page.spacing = 0

    date_input = ft.TextField(label="選択日", hint_text="YYYY-MM-DD")

    def on_search_click(e):
        selected_date = date_input.value
        if selected_date:
            search_data(selected_date)

    header = ft.Container(
        height=100,
        padding=ft.padding.symmetric(horizontal=15),
        content=ft.Row(
            controls=[
                ft.Text("天気予報", color="white", size=35),
                date_input,
                ft.ElevatedButton(text="検索", on_click=on_search_click, height=40)
            ],
        ),
        bgcolor="#4682B4",
    )

    spinner = ft.ProgressRing(visible=False)

    forecast_column = ft.Column(
        scroll="always",
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    def load_area_data():
        response = requests.get(AREA_URL)
        response.raise_for_status()
        return response.json()

    def load_forecast_data(area_code):
        response = requests.get(FORECAST_URL_TEMPLATE.format(area_code))
        response.raise_for_status()
        forecast_data = response.json()
        save_forecast_data(area_code, forecast_data)

    def on_region_select(e):
        area_code = e.control.data
        spinner.visible = True
        forecast_column.controls.clear()
        page.update()

        try:
            load_forecast_data(area_code)

            conn = sqlite3.connect("weather_forecast.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date, weather_code, temp_min, temp_max, name FROM forecasts
                JOIN areas ON forecasts.area_code = areas.code
                WHERE area_code = ?
            """, (area_code,))
            rows = cursor.fetchall()
            conn.close()

            forecast_cards = create_forecast_cards(rows)
            forecast_column.controls.extend(forecast_cards)
        except Exception as ex:
            forecast_column.controls.append(ft.Text(f"Error loading forecast data: {ex}", color="red"))
        finally:
            spinner.visible = False
            page.update()

    def search_data(selected_date):
        try:
            conn = sqlite3.connect("weather_forecast.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date, weather_code, temp_min, temp_max, name FROM forecasts
                JOIN areas ON forecasts.area_code = areas.code
                WHERE date = ?
            """, (selected_date,))
            rows = cursor.fetchall()
            conn.close()
            forecast_column.controls.clear()
            forecast_cards = create_forecast_cards(rows)
            forecast_column.controls.extend(forecast_cards)
        except Exception as ex:
            forecast_column.controls.append(ft.Text(f"Error loading historical data: {ex}", color="red"))
        finally:
            spinner.visible = False
            page.update()

    def create_forecast_cards(rows):
        cards = []
        for row in rows:
            date, weather_code, temp_min_value, temp_max_value, area_name = row
            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(date, size=16),
                        ft.Image(f"https://www.jma.go.jp/bosai/forecast/img/{weather_code}.png", width=50, height=50),
                        ft.Text(area_name, size=14),
                        ft.Text(f"Min: {temp_min_value}°C / Max: {temp_max_value}°C", size=14),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=200,
                height=250,
                padding=ft.padding.all(10),
                margin=ft.margin.all(5),
                bgcolor="white",
                border_radius=ft.border_radius.all(5),
                shadow=ft.BoxShadow(offset=ft.Offset(2, 2), blur_radius=4),
            )
            cards.append(card)
        return cards

    try:
        areas = load_area_data()
        save_area_data(areas)
    except Exception as ex:
        page.add(ft.Text(f"Error loading area data: {ex}", color="red"))
        return

    region_tiles = []
    for region_code, region in areas['centers'].items():
        prefecture_list_tiles = [
            ft.ListTile(
                title=ft.Text(areas["offices"][pref]["name"]),
                data=pref,
                on_click=on_region_select
            )
            for pref in region["children"]
            if pref in areas["offices"]
        ]
        expansion_tile = ft.ExpansionTile(
            title=ft.Text(region['name']),
            controls=prefecture_list_tiles,
            initially_expanded=False
        )
        region_tiles.append(expansion_tile)

    expansion_tile_list = ft.ListView(expand=1, controls=region_tiles)

    page.add(
        ft.Row(
            [
                ft.Column(
                    [header, expansion_tile_list],
                    expand=True,
                    scroll=True,
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            spinner,
                            forecast_column,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                    expand=True,
                    padding=ft.padding.all(10),
                ),
            ],
            expand=True,
        )
    )

init_db()
ft.app(main)