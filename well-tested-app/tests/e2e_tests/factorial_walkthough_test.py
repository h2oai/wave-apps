from playwright.sync_api import Page

from .utils import click, has_text, see


def test_factorial_walkthrough(page: Page):
    page.goto("http://127.0.0.1:10101")
    click(page, "calculate")
    see(page, "stop")
    has_text(page, "progress", "A factorial in progress")
    has_text(page, "result", "Result: 120")
    click(page, "again")
    see(page, "calculate")
