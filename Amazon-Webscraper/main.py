import signal
import sys
import time

import typer
from rich import print
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, TextColumn, BarColumn
from rich.prompt import Prompt
from rich.table import Table, Style
from selectorlib import Extractor

from amazon import AmazonSession, AmazonSearchResult, AccessException
from filter import filter_price, filter_rating, filter_discount, filter_review_count
from serialize import AmazonSearchResultEncoder
from sort import SortMethod, SortType, sort_data

progress = Progress(
    TextColumn("[bold blue]Processing", justify="right"),
    BarColumn(style=Style(color="yellow")),
    "[progress.percentage]{task.percentage:>3.1f}%"
)

LIFECYCLE_OPTIONS = ["sort", "show", "exit"]
in_show = False


def handler(sig, frame):
    global in_show
    if in_show:
        in_show = False
        return
    print("\n[red]Exiting...[/red]")
    sys.exit(0)


signal.signal(signal.SIGINT, handler)


def main(search: str, limit: int = 10, price: int | None = None, rating: float | None = None,
         review_count: int | None = None, discount: int | None = None):
    console = Console(log_time=False, log_path=False)
    with console.status("[bold blue]Starting Amazon Scraper[/bold blue]", spinner="aesthetic") as status:
        console.log("[yellow]Starting Amazon Scraper[/yellow]")
        console.log("[green]Initializing session...[/green]")
        session = AmazonSession()
        time.sleep(2)
        e = Extractor.from_yaml_file("search_result_selector.yml")
        console.log("[green]Session initialized[/green]")

    try:
        session.home()
        console.log(f"[gray]Searching for [yellow]{search}[/yellow]...[/gray]")

        result = []
        with progress:
            task_id = progress.add_task("extract", True, total=limit + 4)
            progress.update(task_id, advance=2)
            page = 1
            while len(result) < limit:
                if page > 10:
                    progress.update(task_id, advance=limit - len(result))
                    break

                res = session.search(search, page)
                data = e.extract(res.text)
                ext = [AmazonSearchResultEncoder.from_dict(r) for r in data['product']]

                # Filters data
                if price:
                    ext = filter_price(ext, price)
                if rating:
                    ext = filter_rating(ext, rating)
                if review_count:
                    ext = filter_review_count(ext, review_count)
                if discount:
                    ext = filter_discount(ext, discount)

                progress.update(task_id, advance=len(ext))
                result.extend(ext)
                page += 1

            progress.update(task_id, advance=2)
        result = result[:limit]

        sorted_by = (None, None)
        # Event loop
        while True:
            show_table(result, sorted_by[0], sorted_by[1])

            print()
            opt = Prompt.ask("What do you want to do?", choices=LIFECYCLE_OPTIONS)

            if opt == "show":
                # Show expanded data
                print(f"Enter index: [purple][1-{len(result)}][/purple]", end=" ")
                idx = int(input())

                element = result[idx - 1]

                print()
                show_element(element)

                global in_show
                in_show = True
                while in_show:
                    pass

            elif opt == "sort":
                # Sort data
                method = Prompt.ask("Sort by?", choices=["price", "original", "rating", "review_count", "discount"])
                sort_type = Prompt.ask("Sort type? [purple]a[/purple] [yellow]->[/yellow] [green]ascending[/green],"
                                       " [purple]d[/purple] [yellow]->[/yellow] [green]descending[/green]",
                                       choices=["a", "d"], default="a", show_choices=False)

                console.log("[yellow]Sorting...[/yellow]")
                result = sort_data(result, method, sort_type)
                sorted_by = (method, sort_type)
            elif opt == "exit":
                break
    except AccessException as e:
        print("[red]" + str(e) + "[/red]")


def __get_review_formatted(review: float) -> str:
    if review < 3:
        return f"[red]{review}/5[/red]"
    elif review < 4:
        return f"[yellow]{review}/5[/yellow]"
    else:
        return f"[green]{review}/5[/green]"


def show_table(data: list[AmazonSearchResult], sort_method: SortMethod | None = None,
               sort_type: SortType | None = None) -> Table:
    if (sort_method and not sort_type) or (sort_type and not sort_method):
        raise ValueError("Both sort_method and sort_type must be provided")

    table = Table(title="Products", title_style=Style(color="green", bold=True), leading=1)
    table.add_column("S.no.", header_style=Style(color="yellow", bold=True), )
    table.add_column("Title", header_style=Style(color="yellow", bold=True))

    price_col = "Price" if sort_method != "price" else ("↑" if sort_type == "a" else "↓") + "Price"
    table.add_column(price_col, header_style=Style(color="yellow", bold=True), style=Style(bold=True), justify="right")

    original_price_col = "Original Price" if sort_method != "original" else (
                                                                                "↑" if sort_type == "a" else "↓") + "Original Price"
    table.add_column(original_price_col, header_style=Style(color="yellow", bold=True), style=Style(dim=True),
                     justify="right")

    discount_col = "Discount" if sort_method != "discount" else ("↑" if sort_type == "a" else "↓") + "Discount"
    table.add_column(discount_col, header_style=Style(color="yellow", bold=True))

    review_col = "Review" if sort_method != "rating" else ("↑" if sort_type == "a" else "↓") + "Review"
    table.add_column(review_col, header_style=Style(color="yellow", bold=True))

    review_count_col = "Review Count" if sort_method != "review_count" else (
                                                                                "↑" if sort_type == "a" else "↓") + "Review Count"
    table.add_column(review_count_col, header_style=Style(color="yellow", bold=True))

    table.add_column("Badge", header_style=Style(color="yellow", bold=True))
    # table.add_column("[yellow]Link[/yellow]", style=Style(underline=True))

    with Live(table, refresh_per_second=4):
        for i, d in enumerate(data):
            time.sleep(0.3)
            table.add_row(
                str(i + 1) + ".",
                d.title[:75] + "...",
                "₹" + str(format(d.price, '.2f')),
                "₹" + str(format(d.original_price, '.2f')),
                f"[white]{d.discount}%[/white]" if d.discount == 0 else f"[green]{d.discount}%[/green]",
                __get_review_formatted(d.review),
                str(d.review_count),
                d.badge if d.badge else "",
                # f"[link={d.link}]" + d.link[:45] + "...[/link]"
            )


def show_element(element: AmazonSearchResult):
    layout = Layout()
    layout.size = 35
    layout.split_column(
        Layout(name="title", size=4),
        Layout(name="image", size=5),
        Layout(name="price", size=3),
        Layout(name="original", size=3),
        Layout(name="discount", size=3),
        Layout(name="review", size=3),
        Layout(name="review_count", size=3),
        Layout(name="badge", size=3),
        Layout(name="link", size=5),
    )

    layout["title"].update(Panel.fit(f"[bold yellow]{element.title}[/bold yellow]"))

    layout["image"].update(Panel.fit(f"[bold]Image:[/bold] [white u]{element.link}[/white u]"))
    layout["price"].update(Panel.fit(f"[bold]Price:[/bold] [green]₹{element.price}[/green]"))
    layout["original"].update(Panel.fit(f"[bold]Original Price:[/bold] [red]₹{element.original_price}[/red]"))
    layout["discount"].update(Panel.fit(f"[bold]Discount:[/bold] [green]{element.discount}%[/green]"))
    layout["review"].update(Panel.fit(f"[bold]Review:[/bold] {__get_review_formatted(element.review)}"))
    layout["review_count"].update(Panel.fit(f"[bold]Review Count:[/bold] [blue]{element.review_count}[/blue]"))
    layout["badge"].update(Panel.fit(f"[bold]Badge:[/bold] {element.badge if element.badge else ''}"))

    layout["link"].update(Panel.fit(f"[u blue]{element.link}[/u blue]", title="[yellow]Link[/yellow]"))

    print(layout)


if __name__ == '__main__':
    typer.run(main)
