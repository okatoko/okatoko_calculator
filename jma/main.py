import flet as ft
import json


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
        height=100,  # 高さを100に設定
        bgcolor="#00008b",
        padding=ft.padding.symmetric(horizontal=10),
        content=ft.Row(
            controls=[
                ft.Text("天気予報", color="white", size=30),
            ],
        ),
    )

    # ヘッダーをフリー位置に配置し、ページ幅に広げる
    page.add(ft.Row([
        ft.Container(content=header, expand=True)
    ]))

    def handle_expansion_tile_change(e):
        page.open(
            ft.SnackBar(
                ft.Text(f"ExpansionTile was {'expanded' if e.data == 'true' else 'collapsed'}"),
                duration=1000,
            )
        )
        if e.control.trailing:
            e.control.trailing.name = (
                ft.Icons.ARROW_DROP_DOWN
                if e.control.trailing.name == ft.Icons.ARROW_DROP_DOWN_CIRCLE
                else ft.Icons.ARROW_DROP_DOWN_CIRCLE
            )
        page.update()

    # areas.json の内容を読み込み
    areas_json = """
    {
        "centers": {
            "010100": {
                "name": "北海道地方",
                "enName": "Hokkaido",
                "officeName": "札幌管区気象台",
                "children": [
                    "011000",
                    "012000",
                    "013000",
                    "014030",
                    "014100",
                    "015000",
                    "016000",
                    "017000"
                ]
            },
            "010200": {
                "name": "東北地方",
                "enName": "Tohoku",
                "officeName": "仙台管区気象台",
                "children": [
                    "020000",
                    "030000",
                    "040000",
                    "050000",
                    "060000",
                    "070000"
                ]
            },
            "010300": {
                "name": "関東甲信地方",
                "enName": "Kanto Koshin",
                "officeName": "気象庁",
                "children": [
                    "080000",
                    "090000",
                    "100000",
                    "110000",
                    "120000",
                    "130000",
                    "140000",
                    "190000",
                    "200000"
                ]
            },
            "010400": {
                "name": "東海地方",
                "enName": "Tokai",
                "officeName": "名古屋地方気象台",
                "children": [
                    "210000",
                    "220000",
                    "230000",
                    "240000"
                ]
            },
            "010500": {
                "name": "北陸地方",
                "enName": "Hokuriku",
                "officeName": "新潟地方気象台",
                "children": [
                    "150000",
                    "160000",
                    "170000",
                    "180000"
                ]
            },
            "010600": {
                "name": "近畿地方",
                "enName": "Kinki",
                "officeName": "大阪管区気象台",
                "children": [
                    "250000",
                    "260000",
                    "270000",
                    "280000",
                    "290000",
                    "300000"
                ]
            },
            "010700": {
                "name": "中国地方（山口県を除く）",
                "enName": "Chugoku (Excluding Yamaguchi)",
                "officeName": "広島地方気象台",
                "children": [
                    "310000",
                    "320000",
                    "330000",
                    "340000"
                ]
            },
            "010800": {
                "name": "四国地方",
                "enName": "Shikoku",
                "officeName": "高松地方気象台",
                "children": [
                    "360000",
                    "370000",
                    "380000",
                    "390000"
                ]
            },
            "010900": {
                "name": "九州北部地方（山口県を含む）",
                "enName": "Northern Kyushu (Including Yamaguchi)",
                "officeName": "福岡管区気象台",
                "children": [
                    "350000",
                    "400000",
                    "410000",
                    "420000",
                    "430000",
                    "440000"
                ]
            },
            "011000": {
                "name": "九州南部・奄美地方",
                "enName": "Southern Kyushu and Amami",
                "officeName": "鹿児島地方気象台",
                "children": [
                    "450000",
                    "460040",
                    "460100"
                ]
            },
            "011100": {
                "name": "沖縄地方",
                "enName": "Okinawa",
                "officeName": "沖縄気象台",
                "children": [
                    "471000",
                    "472000",
                    "473000",
                    "474000"
                ]
            }
        }
    }
    """
    areas = json.loads(areas_json)["centers"]

    # ExpansionTile に地域名を追加
    region_tiles = [
        ft.ListTile(title=ft.Text(region["name"]))
        for region in areas.values()
    ]

    page.add(
        ft.ExpansionTile(
            title=ft.Text("地域を選択"),
            affinity=ft.TileAffinity.PLATFORM,
            maintain_state=True,
            collapsed_text_color=ft.Colors.BLACK,
            text_color=ft.Colors.BLACK,
            controls=region_tiles,
        ),
    )


ft.app(main)