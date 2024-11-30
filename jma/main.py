import flet as ft

#背景色を#87CEFAに設定
def main(page: ft.Page):
    page.bgcolor="#87CEFA"
    page.horizontal_alignment = "stretch"
    page.padding = 0
    page.spacing = 0

    #上部のバーを作成
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

ft.app(main)