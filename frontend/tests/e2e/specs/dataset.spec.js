/// <reference types="cypress" />

context("Dataset Page", () => {
    beforeEach(() => {
        cy.intercept(
            { method: "GET", url: "**/api/population/country**" },
            { fixture: "get.all.countries.fixture.json" }
        ).as("getCountries");
    });

    it("should change the URL to /dataset", () => {
        cy.visit("/");

        const user = cy;
        user.findByText(/dataset table section/i).click();
        user.url().should("eq", "http://localhost:8080/#/dataset");
    });

    it.only("should show the dataset table correctly", () => {
        cy.visit("/#/dataset");
        cy.wait("@getCountries");

        cy.get("tbody > tr").should("have.length", 20);

        cy.wait(100);

        cy.get("tbody > tr")
            .eq(0)
            .should("contain", "China")
            .should("contain", "1440000000");

        cy.get("tbody > tr")
            .eq(1)
            .should("contain", "India")
            .should("contain", "1380000000");

        cy.get("tbody > tr")
            .eq(2)
            .should("contain", "United States")
            .should("contain", "331000000");

        cy.get("tbody > tr")
            .eq(3)
            .should("contain", "Indonesia")
            .should("contain", "274000000");

        cy.get("tbody > tr")
            .eq(4)
            .should("contain", "Pakistan")
            .should("contain", "221000000");
    });
});
