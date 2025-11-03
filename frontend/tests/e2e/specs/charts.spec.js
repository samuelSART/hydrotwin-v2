/// <reference types="cypress" />

context("Charts Page", () => {
    beforeEach(() => {
        cy.intercept(
            { method: "GET", url: "**/api/population/country?countries=**" },
            { fixture: "get.country.fixture.json" }
        ).as("getCountries");

        cy.intercept(
            { method: "GET", url: "**/api/population/top**" },
            { fixture: "get.top.fixture.json" }
        ).as("getTopCountries");

        cy.intercept(
            { method: "GET", url: "**/api/population/region**" },
            { fixture: "get.region.fixture.json" }
        ).as("getRegions");

        cy.visit("/");

        cy.wait(1000);

        cy.viewport(800, 600);

        cy.wait(1000);
    });

    it('should show the "Countries\' population" chart correctly', () => {
        cy.wait("@getCountries");

        // get canvas of countries population
        cy.findByTestId("countries-population-chart")
            .find("canvas")
            .as("canvasChart");

        // wait 1 sec to finalize chart animation
        cy.wait(1000);

        // match snapshots
        cy.get("@canvasChart").toMatchImageSnapshot({
            name: "countries-pupolation-chart",
            disableTimersAndAnimations: false
        });
    });

    it('should show the "Top populations" chart correctly', () => {
        cy.wait("@getTopCountries");

        // get canvas of countries population
        cy.findByTestId("top-populations-chart")
            .find("canvas")
            .as("canvasChart");

        // wait 1 sec to finalize chart animation
        cy.wait(1000);

        // match snapshots
        cy.get("@canvasChart").toMatchImageSnapshot({
            name: "top-populations-chart",
            disableTimersAndAnimations: false
        });
    });

    it('should show the "Regions" chart correctly', () => {
        cy.wait("@getRegions");

        // get canvas of countries population
        cy.findByTestId("regions-chart")
            .find("canvas")
            .as("canvasChart");

        // wait 1 sec to finalize chart animation
        cy.wait(1000);

        // match snapshots
        cy.get("@canvasChart").toMatchImageSnapshot({
            name: "regions-chart",
            disableTimersAndAnimations: false
        });
    });
});
