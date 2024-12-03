import flet as ft
import requests
import json

# 気象庁APIのエンドポイントURL
AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json"

def main(page: ft.Page):
    page.spacing = 0
    page.padding = 0

    # 背景色を#87CEFAに設定
    page.bgcolor = "#87CEFA"
    page.horizontal_alignment = "stretch"
    page.padding = 0
    page.spacing = 0

    # 上部のバーを作成
    header = ft.Container(
        height=100,
        padding=ft.padding.symmetric(horizontal=15),
        content=ft.Row(
            controls=[
                ft.Text("天気予報", color="white", size=35),
            ],
        ),
        bgcolor="#4682B4",
    )

    # データロード用のスピナー
    spinner = ft.ProgressRing(visible=False)

    # 天気予報の表示エリア
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
        return response.json()

    def on_region_select(e):
        area_code = e.control.data
        spinner.visible = True
        forecast_column.controls.clear()
        page.update()

        # 天気予報を読み込む
        try:
            forecast_data = load_forecast_data(area_code)
            forecast_cards = create_forecast_cards(forecast_data)
            forecast_column.controls.extend(forecast_cards)
        except Exception as ex:
            forecast_column.controls.append(ft.Text(f"Error loading forecast data: {ex}", color="red"))
        finally:
            spinner.visible = False
            page.update()

    def create_forecast_cards(data):
        cards = []
        date_index = 0
        for series in data[0]["timeSeries"]:
            if "areas" in series:
                for area in series["areas"]:
                    for weather_info in series["timeDefines"]:
                        weather_code = 'N/A'
                        temp_min_value = 'N/A'
                        temp_max_value = 'N/A'

                        # Extract weather codes
                        if 'weatherCodes' in area and date_index < len(area['weatherCodes']):
                            weather_code = area['weatherCodes'][date_index]

                        # Extract temperatures if available
                        for temp_series in data:
                            for ts in temp_series["timeSeries"]:
                                if 'tempsMin' in ts["areas"][0] or 'tempsMax' in ts["areas"][0]:
                                    for temp_area in ts["areas"]:
                                        if temp_area['area']['code'] == area['area']['code']:
                                            if 'tempsMin' in temp_area and date_index < len(temp_area['tempsMin']):
                                                temp_min_value = temp_area['tempsMin'][date_index]
                                            if 'tempsMax' in temp_area and date_index < len(temp_area['tempsMax']):
                                                temp_max_value = temp_area['tempsMax'][date_index]
                                            break

                        date = weather_info.split("T")[0]
                        card = ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(date, size=16),
                                    ft.Image(f"https://www.jma.go.jp/bosai/forecast/img/{weather_code}.png", width=50, height=50),
                                    ft.Text(area['area']['name'], size=14),
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
                        date_index += 1
        return cards

    try:
        areas = load_area_data()
    except Exception as ex:
        page.add(ft.Text(f"Error loading area data: {ex}", color="red"))
        return

    # 地域名と都道府県を表示するためのエキスパンションタイルを作成
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

    # 地域エキスパンションタイルのリストビューを作成
    expansion_tile_list = ft.ListView(expand=1, controls=region_tiles)

    # コンテナに左側のナビゲーション要素とコンテンツを追加
    page.add(
        ft.Row(
            [
                ft.Column(
                    [header, expansion_tile_list],   # ヘッダーと地域リストを含める
                    expand=True,
                    scroll=True,  # スクロールを有効にする
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

ft.app(main)