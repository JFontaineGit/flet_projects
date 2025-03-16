import flet as ft
import pandas as pd
from math import pi
from traceback import print_exc

class DataVisualization(ft.UserControl):
    def __init__(self, month_sum: float, max_sum: float, spacing: int, color: str, month: str, sales: float):
        self.month_sum = month_sum
        self.delta_sum = max_sum - self.month_sum
        self.color = color
        self.month = month
        self.sales = sales
        self.is_visible = True

        self.chart = ft.PieChart(
            sections=[
                ft.PieChartSection(value=self.month_sum, color=self.color, radius=15),
                ft.PieChartSection(
                    value=self.delta_sum,
                    color=ft.colors.with_opacity(0.025, "white"),
                    radius=15,
                ),
            ],
            sections_space=0,
            center_space_radius=spacing,
            rotate=ft.Rotate(pi / 2),
        )
        super().__init__()

    def build(self):
        return ft.Container(
            content=self.chart,
            on_click=self.toggle_visibility
        )

    def toggle_visibility(self, e):
        self.is_visible = not self.is_visible
        self.chart.sections[0].color = self.color if self.is_visible else ft.colors.with_opacity(0.1, self.color)
        self.update()

def load_and_process_data():
    try:
        # Carga, filtrado y procesamiento de datos
        sales_data = pd.read_csv("sales.csv")

        sales_data = sales_data.replace("n.a.", pd.NA).dropna()

        for month in sales_data.columns[5:]:
            sales_data[month] = sales_data[month].str.replace(",", "").str.replace("not available", "0").str.replace("not avilable", "0").astype(float)

        return sales_data
    except Exception as e:
        print(f"Error: {e.__class__.__name__}")
        print(f"Message: {str(e)}")
        print("Traceback:")
        print_exc()

def setup_visualization(sales_data):
    colors = [f"purple{num}00" for num in range(1, 13)]

    month_list = sales_data.columns[5:].tolist()
    sum_list = [sales_data[month].sum() for month in month_list]
    max_sum = max(sum_list) if sum_list else 0

    stack = ft.Stack(scale=ft.Scale(0.65))
    size = 60
    for index, month in enumerate(month_list):
        stack.controls.append(
            DataVisualization(
                month_sum=sum_list[index],
                max_sum=max_sum,
                spacing=size,
                color=colors[index],
                month=month,
                sales=sum_list[index]
            )
        )
        size += 30

    return stack, month_list, sum_list, colors

def create_legend(month_list, sum_list, colors, stack):
    col = ft.Column(alignment="center")
    legend_items = []
    for index, month in enumerate(month_list):
        color_dot = ft.Container(
            width=9,
            height=9,
            shape=ft.BoxShape("circle"),
            bgcolor=colors[index],
        )
        text_month = ft.Text(month, size=14, weight="bold")
        text_sales = ft.Text(f"${sum_list[index]:.2f}", size=14, weight="bold")
        legend_item = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        alignment="start",
                        controls=[
                            color_dot,
                            text_month,
                        ],
                    ),
                    ft.Row(
                        alignment="end",
                        controls=[
                            ft.Text(
                                f"${sum_list[index]:.2f}",
                                size=14,
                                weight="bold",
                            ),
                        ],
                    ),
                ],
            ),
            on_click=lambda e, idx=index, dot=color_dot, txt=text_month, txt_sales=text_sales: toggle_legend_item(e, idx, stack, dot, txt, txt_sales, legend_item)
        )
        col.controls.append(legend_item)
        legend_items.append((legend_item, color_dot))
    return col, legend_items

def toggle_legend_item(e, index, stack, dot, txt, txt_sales, legend_item):
    chart = stack.controls[index]
    chart.is_visible = not chart.is_visible
    chart.chart.sections[0].color = chart.color if chart.is_visible else ft.colors.with_opacity(0.1, chart.color)
    chart.update()
    dot.bgcolor = chart.color if chart.is_visible else ft.colors.with_opacity(0.1, "grey")
    dot.update()
    txt.color = "white" if chart.is_visible else ft.colors.with_opacity(0.1, "grey")
    txt.update()
    txt_sales.color = "white" if chart.is_visible else ft.colors.with_opacity(0.1, "grey")
    txt_sales.update()
    legend_item.update()
    
stack = None
colors = []

def main(page: ft.Page):
    global stack, colors
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    try:
        sales_data = load_and_process_data()
        if sales_data is None:
            page.add(ft.Text("No se pudieron cargar los datos."))
            return

        stack, month_list, sum_list, colors = setup_visualization(sales_data)
        legend, legend_items = create_legend(month_list, sum_list, colors, stack)

        page.add(
            ft.Row(
                alignment="center",
                controls=[
                    ft.Container(
                        width=500,
                        height=500,
                        bgcolor=ft.colors.with_opacity(0.009, "white10"),
                        content=stack,
                    ),
                    ft.Container(
                        height=500,
                        width=400,
                        padding=50,
                        bgcolor=ft.colors.with_opacity(0.009, "white10"),
                        content=legend,
                    ),
                ],
            )
        )

        page.update()
    except Exception as e:
        print(f"Error: {e.__class__.__name__}")
        print(f"Message: {str(e)}")
        print("Traceback:")
        print_exc()

if __name__ == "__main__":
    ft.app(target=main)
