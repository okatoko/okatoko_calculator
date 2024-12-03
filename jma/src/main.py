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


ft.app(main)
