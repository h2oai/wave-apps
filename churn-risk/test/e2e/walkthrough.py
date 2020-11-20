from h2o_wave.test import Cypress, cypress

OPERATION_TIMEOUT = {"timeout": 10000}
CUSTOMER_NO = "3548815"


@cypress("Walk through the churn risk app")
def app_walkthrough(cy: Cypress):

    def get_aria_label(label: str, *args):
        return cy.get(f'div[aria-label="{label}"]', *args)

    def contains_text(component, content):
        cy.locate(component).contains(content, OPERATION_TIMEOUT)

    cy.visit("/", OPERATION_TIMEOUT)
    cy.locate("customers", OPERATION_TIMEOUT).click().type(CUSTOMER_NO)
    get_aria_label(CUSTOMER_NO).click()
    cy.locate("select_customer_button", OPERATION_TIMEOUT).click()
    contains_text("customer", CUSTOMER_NO)
    contains_text("day_stat", "Day Charges")
    contains_text("eve_stat", "Evening Charges")
    contains_text("night_stat", "Night Charges")
    contains_text("intl_stat", "Int'l Charges")
    contains_text("stat_pie", "Total call charges breakdown")
