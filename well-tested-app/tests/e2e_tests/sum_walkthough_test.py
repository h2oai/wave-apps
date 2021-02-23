from playwright.sync_api import Page

from .utils import click, has_text, see


def test_sum_walkthrough(page: Page):
    page.goto("http://127.0.0.1:10101")
    page.click("input#ChoiceGroup1-sum")
    click(page, "calculate")
    see(page, "stop")
    has_text(page, "progress", "A sum in progress")
    has_text(page, "result", "Result: 15")
    click(page, "again")
    see(page, "calculate")
