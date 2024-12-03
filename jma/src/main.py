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
    forecast_text = ft.Text("", size=20, expand=1)

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
        page.update()

        # 天気予報を読み込む
        try:
            forecast_data = load_forecast_data(area_code)
            forecast_info = parse_forecast_data(forecast_data)
            forecast_text.value = forecast_info
        except Exception as ex:
            forecast_text.value = f"Error loading forecast data: {ex}"
        finally:
            spinner.visible = False
            page.update()

    def parse_forecast_data(data):
        # シンプルな天気予報情報を抜粋して表示する
        forecast_parts = []
        for item in data:
            if "timeSeries" in item:
                for series in item["timeSeries"]:
                    if "areas" in series:
                        for area in series["areas"]:
                            forecast_parts.append(f"{area['area']['name']} - {area['weatherCodes'][0]}")

        return "\n".join(forecast_parts)

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
                    ft.Column(
                        [
                            spinner,
                            forecast_text,
                        ],
                        alignment=ft.MainAxisAlignment.START,
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
