import flet as ft

def build_start_page(page: ft.Page):
    return ft.View(
        "/start",
        [
            ft.AppBar(
                bgcolor=ft.colors.BLUE_GREY_900,
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda _: page.go("/")
                )
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Get Started",
                            style=ft.TextStyle(
                                size=32,
                                weight=ft.FontWeight.BOLD
                            )
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.GestureDetector(
                                        content=ft.Card(
                                            content=ft.Container(
                                                content=ft.Text("Upload Files", style=ft.TextStyle(size=24)),
                                                alignment=ft.alignment.center,
                                                padding=20
                                            ),
                                            width=200,
                                            height=200
                                        ),
                                        on_tap=lambda _: page.go("/upload")
                                    ),
                                    ft.GestureDetector(
                                        content=ft.Card(
                                            content=ft.Container(
                                                content=ft.Text("Input Data", style=ft.TextStyle(size=24)),
                                                alignment=ft.alignment.center,
                                                padding=20
                                            ),
                                            width=200,
                                            height=200
                                        ),
                                        on_tap=lambda _: page.go("/input")
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20
                            ),
                            alignment=ft.alignment.center,
                            padding=20
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True
                ),
                alignment=ft.alignment.center,
                padding=20
            ),
        ]
    )