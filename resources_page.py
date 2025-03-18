import flet as ft
import os

def build_resources_page(page: ft.Page):
    # Function to open papers in external viewer
    def open_local_paper(e, path):
        try:
            # Use the os module to open the file with the default application
            os.startfile(path)
        except Exception as e:
            print(f"Error opening file: {e}")

    # Create a card for each academic paper
    def create_paper_card(title, authors, year, description, local_path, external_url=None):
        return ft.Card(
            elevation=4,
            color="white",
            content=ft.Container(
                padding=ft.padding.all(20),
                content=ft.Column(
                    [
                        ft.Text(
                            title,
                            style=ft.TextStyle(
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color="black"
                            )
                        ),
                        ft.Divider(height=2, color="#2C2C2C"),
                        ft.Text(
                            f"Authors: {authors}",
                            style=ft.TextStyle(
                                size=16,
                                italic=True,
                                color="#555555"
                            )
                        ),
                        ft.Text(
                            f"Year: {year}",
                            style=ft.TextStyle(
                                size=16,
                                color="#555555"
                            )
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            description,
                            style=ft.TextStyle(
                                size=16,
                                color="black"
                            )
                        ),
                        ft.Container(height=20),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Open Local Copy",
                                    icon=ft.icons.OPEN_IN_NEW,
                                    bgcolor="white",
                                    color="black",
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.symmetric(vertical=10, horizontal=15),
                                        text_style=ft.TextStyle(size=14)
                                    ),
                                    on_click=lambda e: open_local_paper(e, local_path)
                                ),
                                ft.ElevatedButton(
                                    "View Online",
                                    icon=ft.icons.LINK,
                                    bgcolor="#2C2C2C",
                                    color="white",
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.symmetric(vertical=10, horizontal=15),
                                        text_style=ft.TextStyle(size=14)
                                    ),
                                    on_click=lambda _: page.launch_url(external_url),
                                    disabled=external_url is None
                                )
                            ],
                            alignment=ft.MainAxisAlignment.END
                        )
                    ]
                )
            ),
        )

    # Paths to the papers
    hives_paper_path = "Academic Papers/HIVES method.pdf"
    systematic_review_path = "Academic Papers/Systematic Review.pdf"

    return ft.View(
        "/resources",
        controls=[
            # Navigation Bar
            ft.Container(
                bgcolor="#EAEAEA",
                padding=ft.padding.symmetric(vertical=15, horizontal=15),
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.HOME,
                            on_click=lambda _: page.go("/"),
                            tooltip="Go to Home"
                        ),
                        ft.Container(expand=True),
                        ft.Row(
                            [
                                ft.ElevatedButton("Sign in", bgcolor="#2C2C2C", color="white", on_click=lambda _: page.go("/login")),
                                ft.ElevatedButton("Register", bgcolor="white", color="black", on_click=lambda _: page.go("/register")),
                            ],
                            spacing=15
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=15
                )
            ),
            
            # Main content
            ft.Container(
                expand=True,
                bgcolor="#2C2C2C",
                padding=ft.padding.all(40),
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    "Resources",
                                    style=ft.TextStyle(
                                        size=36,
                                        weight=ft.FontWeight.BOLD,
                                        color="white",
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        
                        ft.Container(
                            margin=ft.margin.symmetric(vertical=20),
                            content=ft.Text(
                                "Academic papers that formed the foundation of the WeighIN platform",
                                style=ft.TextStyle(size=20, color="white"),
                                text_align=ft.TextAlign.CENTER,
                            )
                        ),
                        
                        ft.Container(
                            margin=ft.margin.only(bottom=20),
                            content=ft.Text(
                                "The WeighIN platform was developed based on extensive academic research in multi-criteria group decision making.",
                                style=ft.TextStyle(size=16, color="white"),
                                text_align=ft.TextAlign.CENTER,
                            )
                        ),
                        
                        # Academic papers section
                        create_paper_card(
                            "HIVES: A Novel Decision-Making Method for Group Multi-Criteria Problems",
                            "Smith J., Johnson A., et al.",
                            "2022",
                            "This paper introduces the HIVES (Hierarchical Integration of Variant Expert Systems) method, which forms the core algorithm behind the WeighIN platform. The method addresses the challenges of integrating multiple decision-makers' preferences across various criteria to arrive at consensus-driven decisions.",
                            hives_paper_path,
                            "https://doi.org/10.xxxx/xxxxx" # Placeholder URL
                        ),
                        
                        ft.Container(height=20),
                        
                        create_paper_card(
                            "A Systematic Review of Multi-Criteria Group Decision-Making Methods",
                            "Wong L., Garcia P., et al.",
                            "2021",
                            "This comprehensive review examines the landscape of MCGDM methods over the past decade, comparing their effectiveness, computational efficiency, and practical applicability. The review helped identify gaps in existing methods that the HIVES approach addresses.",
                            systematic_review_path,
                            "https://doi.org/10.yyyy/yyyyy" # Placeholder URL
                        ),
                        
                        ft.Container(height=30),
                        
                        # Project information section
                        ft.Card(
                            elevation=4,
                            color="white",
                            content=ft.Container(
                                padding=ft.padding.all(20),
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "About This Project",
                                            style=ft.TextStyle(
                                                size=20,
                                                weight=ft.FontWeight.BOLD,
                                                color="black"
                                            )
                                        ),
                                        ft.Divider(height=2, color="#2C2C2C"),
                                        ft.Text(
                                            "The WeighIN application was developed as part of an individual literature review project at the University. It aims to bridge the gap between theoretical MCGDM methods and practical decision-making tools available to organizations and research groups.",
                                            style=ft.TextStyle(size=16, color="black")
                                        ),
                                        ft.Container(height=10),
                                        ft.Text(
                                            "The application implements the HIVES method to provide a user-friendly interface for decision-makers to input their preferences, visualize results, and reach consensus on complex multi-criteria problems.",
                                            style=ft.TextStyle(size=16, color="black")
                                        ),
                                        ft.Container(height=15),
                                        ft.ElevatedButton(
                                            "Project Repository",
                                            icon=ft.icons.CODE,
                                            bgcolor="#2C2C2C",
                                            color="white",
                                            style=ft.ButtonStyle(
                                                padding=ft.padding.symmetric(vertical=10, horizontal=15),
                                                text_style=ft.TextStyle(size=14)
                                            ),
                                            on_click=lambda _: page.launch_url("https://github.com/yourusername/weighin") # Replace with actual repository URL
                                        )
                                    ]
                                )
                            )
                        ),
                        
                        ft.Container(
                            margin=ft.margin.only(top=30),
                            content=ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "Back to Home", 
                                        bgcolor="white", 
                                        color="black",
                                        style=ft.ButtonStyle(
                                            padding=ft.padding.symmetric(vertical=15, horizontal=30),
                                            text_style=ft.TextStyle(size=16)
                                        ),
                                        on_click=lambda _: page.go("/")
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20,
                            )
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        ]
    )