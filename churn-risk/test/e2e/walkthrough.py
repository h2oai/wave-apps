from h2o_wave.test import cypress, Cypress

BIG_TIMEOUT = {"timeout": 90000}

@cypress("Walk through the churn risk app")
def app_walkthrough(cy: Cypress):
    def getdiv(name: str, *args):
        return cy.get('div[data-test="{name}"', *args)

    def getbuttoncontain(name: str, *args):
        return cy.get('button').contains(f'{name}', *args)

    cy.visit("/abc")
    # getbuttoncontain('Customer Profiles').click()
    # cy.get('[data-test=customers]').click()
    # cy.get('[data-test=customers]').type('3548815')
    # getbuttoncontain('Submit').click()

    # cy.visit('http://localhost:55555/');
    # cy.get('#Pivot1-Tab0 .ms-Pivot-text').click();
    # cy.get('[data-test=customers]').click();
    # cy.get('[data-test=customers]').type('3548815');
    # cy.get('.ms-TagItem-TextOverflow').click();
    # cy.get('#id__26').click();


# getbuttoncontain('Upload', BIG_TIMEOUT).click()
    # getdiv("Customer Profiles").click()
    # getbuttoncontain('default payment next month').click()
    # cy.get('button[data-test="select"').click()
    # getdiv("predict_what").click()
    # cy.get('button[data-index="0"').click()
    # getbuttoncontain('Select All').click()
    # cy.get('button[data-test="selection_features"').click()
    # cy.get('button[data-test="run_scorecard"').click()
    # cy.wait(5000)
    # cy.get('button[data-content="Diagnostics"').click()
