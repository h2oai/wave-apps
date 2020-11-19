from h2o_wave.test import Cypress, cypress

BIG_TIMEOUT = {"timeout": 90000}
CUSTOMER_NO = "3548815"


@cypress("Walk through the churn risk app")
def app_walkthrough(cy: Cypress):
    def getdiv(name: str, *args):
        return cy.get(f'div[data-test="{name}"', *args)

    def getdivcontain(value: str, *args):
        return cy.get("div").contains(f"{value}", *args)

    def button(name: str, *args):
        return cy.get(f'button[name="{name}"],button[data-test="{name}"]', *args)

    def contains_text(divname, content):
        getdiv(divname).contains(content, BIG_TIMEOUT)

    cy.visit("/", BIG_TIMEOUT)
    cy.locate("customers", BIG_TIMEOUT).click().type(CUSTOMER_NO)
    getdivcontain(CUSTOMER_NO).click()
    button("select_customer_button", BIG_TIMEOUT).click()
    contains_text("customer", CUSTOMER_NO)
    contains_text("day_stat", "Day Charges")
    contains_text("eve_stat", "Evening Charges")
    contains_text("night_stat", "Night Charges")
    contains_text("intl_stat", "Int'l Charges")
    contains_text("stat_pie", "Total call charges breakdown")
