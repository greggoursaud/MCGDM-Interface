import flet as ft

def main(page: ft.Page):
    page.title = "Define a Problem"
    page.bgcolor = "#EAEAEA"  # Background color for entire page

    # Navbar
    navbar = ft.Container(
        bgcolor="#EAEAEA",
        padding=ft.padding.symmetric(vertical=15, horizontal=40),
        content=ft.Row(
            [
                # Logo (Placeholder)
                ft.Icon(ft.icons.BUBBLE_CHART, size=30),

                # Navigation Links
                ft.Row(
                    [
                        ft.Text("Resources"),
                        ft.Text("About"),
                        ft.Text("Contact"),
                        ft.ElevatedButton("Sign in", bgcolor="white", color="black"),
                        ft.ElevatedButton("Register", bgcolor="black", color="white"),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=15
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
    )

    # Title and Subtitle
    title_section = ft.Column(
        [
            ft.Text(
                "Define a Problem",
                size=40,
                weight=ft.FontWeight.BOLD,
                color="white",
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                "Define your decision-making problem by specifying key criteria, alternatives, and decision makers. This will structure the evaluation process.",
                italic=True,
                size=16,
                color="white",
                text_align=ft.TextAlign.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    # Form Inputs
    form = ft.Container(
        width=400,
        padding=ft.padding.all(20),
        bgcolor="#1C1C1C",
        border_radius=10,
        content=ft.Column(
            [
                ft.TextField(label="Number of Criteria", value="3", text_align=ft.TextAlign.CENTER),
                ft.TextField(label="Number of Alternatives", value="5", text_align=ft.TextAlign.CENTER),
                ft.TextField(label="Number of Decision Makers", value="4", text_align=ft.TextAlign.CENTER),
                ft.TextField(label="Description", multiline=True, hint_text="Value"),
                ft.ElevatedButton("Continue", bgcolor="white", color="black"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
        ),
    )

    # Full Layout
    page.add(
        navbar,
        ft.Container(
            expand=True,
            bgcolor="#2C2C2C",
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    title_section,
                    form,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=30,
            ),
        ),
    )

ft.app(target=main)