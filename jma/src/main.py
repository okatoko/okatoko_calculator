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


ft.app(main)