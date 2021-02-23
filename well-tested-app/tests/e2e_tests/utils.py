from playwright.sync_api import ElementHandle, Page


def selector(data_test: str):
    return f"[data-test='{data_test}']"


def see(p: Page, data_test: str) -> ElementHandle:
    return p.wait_for_selector(selector(data_test))


def click(p: Page, data_test: str):
    p.click(selector(data_test))


def has_text(p: Page, data_test: str, text: str):
    assert text in see(p, data_test).inner_text()
