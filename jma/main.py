import flet as ft

#背景色を#87CEFAに設定
def main(page: ft.Page):
    page.bgcolor="#87CEFA"

    page.add(ft.SafeArea(ft.Text("Hello, Flet!")))


ft.app(main)