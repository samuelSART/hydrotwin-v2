import { LegendItem, VariableValue } from "@/interfaces";
import { arrayAvg, groupBy } from "@/utils";
import { i18n } from "@/plugins/i18n";

export enum PiezometerColors {
    GREEN = "#1BF540",
    BLUE = "#4699E6",
    CYAN = "#39FFDE",
    ORANGE = "#EB951C",
    RED = "#D13608",
    PURPLE = "#C330FA",
    BLACK = "#000000"
}

export interface CPTimeRangeConfig {
    range: string;
    reqBody: unknown;
    computeStateColor: (varValues: VariableValue[]) => string;
    displayInfo?: (varValues: VariableValue[], numPiez?: number) => string;
    diffDays?: () => number;
    getLegend?: () => LegendItem[];
}

const getDiffDays = (start: Date, end: Date) => {
    const difference = Math.abs(start.getTime() - end.getTime());
    return Math.ceil(difference / (1000 * 3600 * 24));
};

const getCurYearDate = () => new Date(new Date().getFullYear(), 0, 1);
const getHydroYearDate = () => new Date("1 October 2015");
const getLast365DaysDate = () =>
    new Date(new Date().setDate(new Date().getDate() - 365));
const validTimeValue = (timeValue: VariableValue): boolean =>
    Boolean(timeValue._time) && Boolean(timeValue._value);

const getClosestValue = (
    varValues: VariableValue[],
    date: Date
): VariableValue | null => {
    const values = [...varValues];
    values.sort((va, vb) => {
        const dista = Math.abs(+date - +new Date(va._time));
        const distb = Math.abs(+date - +new Date(vb._time));

        return dista - distb;
    });

    return values[0] || null;
};

const getStateColorLatest = (value: number) => {
    if (value <= 50) return PiezometerColors.GREEN;
    if (value > 50 && value <= 100) return PiezometerColors.BLUE;
    if (value > 100 && value <= 150) return PiezometerColors.CYAN;
    if (value > 150 && value <= 250) return PiezometerColors.ORANGE;
    if (value > 250 && value <= 350) return PiezometerColors.RED;
    if (value > 350) return PiezometerColors.PURPLE;

    return PiezometerColors.BLACK;
};

const getStateColorInitYear = (value: number) => {
    if (value <= -0.5) return PiezometerColors.GREEN;
    if (value > -0.5 && value <= 0) return PiezometerColors.BLUE;
    if (value > 0 && value <= 0.5) return PiezometerColors.CYAN;
    if (value > 0.5 && value <= 1) return PiezometerColors.ORANGE;
    if (value > 1) return PiezometerColors.RED;

    return PiezometerColors.BLACK;
};

const getStateColorInitControl = (value: number) => {
    if (value > -1) return PiezometerColors.GREEN;
    if (value <= -1 && value > -25) return PiezometerColors.BLUE;
    if (value <= -25 && value > -50) return PiezometerColors.CYAN;
    if (value <= -50 && value > -100) return PiezometerColors.ORANGE;
    if (value <= -100 && value > -200) return PiezometerColors.RED;
    if (value <= -200) return PiezometerColors.PURPLE;

    return PiezometerColors.BLACK;
};

const computeAquiferDataByDate = (varValues: VariableValue[], date: Date) => {
    // get piezometers groups
    const piezometersGroups = groupBy(varValues, "variableCode");

    // for each piezometer finds the closest value and compute de avg
    const initValues: number[] = [];
    const endValues: number[] = [];
    for (const [, pieVarValues] of Object.entries<VariableValue[]>(
        piezometersGroups
    )) {
        const pnpInit = getClosestValue(pieVarValues, date); // get the closest value to a date
        const pnpEnd = pieVarValues[0] || null;

        if (
            pnpInit?._value &&
            pnpEnd?._value &&
            pnpInit?._time !== pnpEnd?._time
        ) {
            initValues.push(pnpInit._value);
            endValues.push(pnpEnd._value);
        }
    }

    const avgInit = arrayAvg(initValues);
    const avgEnd = arrayAvg(endValues);
    const delta = avgEnd - avgInit;

    return { avgInit, avgEnd, delta };
};

const computeAquiferInitControlData = (varValues: VariableValue[]) => {
    const piezometersGroups = groupBy(varValues, "variableCode");

    // for each piezometer get the init and end value and compute de avg
    const initValues: number[] = [];
    const endValues: number[] = [];

    for (const [, pieVarValues] of Object.entries<VariableValue[]>(
        piezometersGroups
    )) {
        const pnpInit = pieVarValues[0] || null;
        const pnpEnd = pieVarValues[pieVarValues.length - 1] || null;

        if (pnpInit?._value && pnpEnd?._value && pnpInit !== pnpEnd) {
            initValues.push(pnpInit._value);
            endValues.push(pnpEnd._value);
        }
    }

    const avgInit = arrayAvg(initValues);
    const avgEnd = arrayAvg(endValues);
    const delta = avgEnd - avgInit;

    return { avgInit, avgEnd, delta };
};

export const cpTimeRangesPieConfig: CPTimeRangeConfig[] = [
    {
        range: "latest",
        reqBody: {
            type: "latest"
        },
        computeStateColor: (varValues: VariableValue[]): string => {
            const lastPNPValue = varValues[varValues.length - 1] || null;
            const delta = lastPNPValue._value;
            return getStateColorLatest(delta);
        },
        displayInfo: (varValues: VariableValue[]): string => {
            const lastPNPValue = varValues[varValues.length - 1] || null;
            const delta = lastPNPValue._value.toFixed(2);

            return `
                <div>
                    PNP: ${delta}
                </div>
                <div>
                    ${i18n.t("CPPiezometer.date")}: ${new Date(
                lastPNPValue._time
            ).toLocaleDateString()}
                </div>
            `;
        },
        getLegend: () => {
            return [
                { color: PiezometerColors.GREEN, text: "pnp <= 50" },
                {
                    color: PiezometerColors.BLUE,
                    text: "50 < pnp <= 100"
                },
                {
                    color: PiezometerColors.CYAN,
                    text: "100 < pnp <= 150"
                },
                {
                    color: PiezometerColors.ORANGE,
                    text: "150 < pnp <= 250"
                },
                {
                    color: PiezometerColors.RED,
                    text: "250 < pnp <= 350"
                },
                { color: PiezometerColors.PURPLE, text: "> 350" },
                {
                    color: PiezometerColors.BLACK,
                    text: `${i18n.t("CPPiezometer.noData")}`
                }
            ];
        }
    },
    {
        range: "lastYear",
        reqBody: {
            type: "custom",
            range: {
                start: getLast365DaysDate().toISOString(),
                end: new Date().toISOString()
            }
        },
        computeStateColor: (varValues: VariableValue[]): string => {
            const pnpInit = getClosestValue(varValues, getLast365DaysDate()); // get the closest value to a date
            const pnpEnd = varValues[0] || null;

            if (
                !pnpInit ||
                !pnpEnd ||
                !validTimeValue(pnpInit) ||
                !validTimeValue(pnpEnd)
            )
                return PiezometerColors.BLACK;

            const delta = pnpEnd._value - pnpInit._value;
            return getStateColorInitYear(delta);
        },
        displayInfo: (varValues: VariableValue[]): string => {
            const pnpInit = getClosestValue(varValues, getLast365DaysDate()); // get the closest value to a date
            const pnpEnd = varValues[0] || null;

            if (
                !pnpInit ||
                !pnpEnd ||
                !validTimeValue(pnpInit) ||
                !validTimeValue(pnpEnd)
            )
                return "";

            const delta = pnpEnd._value - pnpInit._value;

            return `
                <div>
                    Delta: ${delta.toFixed(2)}
                </div>
                <div>
                    ${i18n.t("CPPiezometer.initDate")}: ${new Date(
                pnpInit._time
            ).toLocaleDateString()} (${pnpInit._value.toFixed()})
                </div>
                <div>
                     ${i18n.t("CPPiezometer.endDate")}: ${new Date(
                pnpEnd._time
            ).toLocaleDateString()} (${pnpEnd._value.toFixed()})
                </div>
            `;
        },
        diffDays: () => getDiffDays(getLast365DaysDate(), new Date()),
        getLegend: () => {
            return [
                { color: PiezometerColors.GREEN, text: "delta <= -0.5" },
                {
                    color: PiezometerColors.BLUE,
                    text: "-0.5 < delta <= 0"
                },
                {
                    color: PiezometerColors.CYAN,
                    text: "0 < delta <= 0.5"
                },
                {
                    color: PiezometerColors.ORANGE,
                    text: "0.5 < delta <= 1"
                },
                { color: PiezometerColors.RED, text: "> 1" },
                {
                    color: PiezometerColors.BLACK,
                    text: `${i18n.t("CPPiezometer.noData")}`
                }
            ];
        }
    },
    {
        range: "initYear",
        reqBody: {
            type: "custom",
            range: {
                start: getCurYearDate().toISOString(),
                end: new Date().toISOString()
            }
        },
        computeStateColor: (varValues: VariableValue[]): string => {
            const pnpInit = getClosestValue(varValues, getCurYearDate()); // get the closest value to a date
            const pnpEnd = varValues[0] || null;

            if (
                !pnpInit ||
                !pnpEnd ||
                !validTimeValue(pnpInit) ||
                !validTimeValue(pnpEnd)
            )
                return PiezometerColors.BLACK;

            const delta = pnpEnd._value - pnpInit._value;
            return getStateColorInitYear(delta);
        },
        displayInfo: (varValues: VariableValue[]): string => {
            const pnpInit = getClosestValue(varValues, getCurYearDate()); // get the closest value to a date
            const pnpEnd = varValues[0] || null;

            if (
                !pnpInit ||
                !pnpEnd ||
                !validTimeValue(pnpInit) ||
                !validTimeValue(pnpEnd)
            )
                return "";

            const delta = pnpEnd._value - pnpInit._value;

            return `
                <div>
                    Delta: ${delta.toFixed(2)}
                </div>
                <div>
                    ${i18n.t("CPPiezometer.initDate")}: ${new Date(
                pnpInit._time
            ).toLocaleDateString()} (${pnpInit._value.toFixed()})
                </div>
                <div>
                     ${i18n.t("CPPiezometer.endDate")}: ${new Date(
                pnpEnd._time
            ).toLocaleDateString()} (${pnpEnd._value.toFixed()})
                </div>
            `;
        },
        diffDays: () => getDiffDays(getCurYearDate(), new Date()),
        getLegend: () => {
            return [
                { color: PiezometerColors.GREEN, text: "delta <= -0.5" },
                {
                    color: PiezometerColors.BLUE,
                    text: "-0.5 < delta <= 0"
                },
                {
                    color: PiezometerColors.CYAN,
                    text: "0 < delta <= 0.5"
                },
                {
                    color: PiezometerColors.ORANGE,
                    text: "0.5 < delta <= 1"
                },
                { color: PiezometerColors.RED, text: "> 1" },
                {
                    color: PiezometerColors.BLACK,
                    text: `${i18n.t("CPPiezometer.noData")}`
                }
            ];
        }
    },
    {
        range: "initHydroYear",
        reqBody: {
            type: "custom",
            range: {
                start: getHydroYearDate().toISOString(),
                end: new Date().toISOString()
            }
        },
        computeStateColor: (varValues: VariableValue[]): string => {
            const pnpInit = getClosestValue(varValues, getHydroYearDate()); // get the closest value to a date
            const pnpEnd = varValues[0] || null;

            if (
                !pnpInit ||
                !pnpEnd ||
                !validTimeValue(pnpInit) ||
                !validTimeValue(pnpEnd)
            )
                return PiezometerColors.BLACK;

            const delta = pnpEnd._value - pnpInit._value;
            return getStateColorInitYear(delta);
        },
        displayInfo: (varValues: VariableValue[]): string => {
            const pnpInit = getClosestValue(varValues, getHydroYearDate()); // get the closest value to a date
            const pnpEnd = varValues[0] || null;

            if (
                !pnpInit ||
                !pnpEnd ||
                !validTimeValue(pnpInit) ||
                !validTimeValue(pnpEnd)
            )
                return "";

            const delta = pnpEnd._value - pnpInit._value;

            return `
                <div>
                    Delta: ${delta.toFixed(2)}
                </div>
                <div>
                     ${i18n.t("CPPiezometer.initDate")}: ${new Date(
                pnpInit._time
            ).toLocaleDateString()} (${pnpInit._value.toFixed()})
                </div>
                <div>
                     ${i18n.t("CPPiezometer.endDate")}: ${new Date(
                pnpEnd._time
            ).toLocaleDateString()} (${pnpEnd._value.toFixed()})
                </div>
            `;
        },
        diffDays: () => getDiffDays(getHydroYearDate(), new Date()),
        getLegend: () => {
            return [
                { color: PiezometerColors.GREEN, text: "delta <= -0.5" },
                {
                    color: PiezometerColors.BLUE,
                    text: "-0.5 < delta <= 0"
                },
                {
                    color: PiezometerColors.CYAN,
                    text: "0 < delta <= 0.5"
                },
                {
                    color: PiezometerColors.ORANGE,
                    text: "0.5 < delta <= 1"
                },
                { color: PiezometerColors.RED, text: "> 1" },
                {
                    color: PiezometerColors.BLACK,
                    text: `${i18n.t("CPPiezometer.noData")}`
                }
            ];
        }
    },
    {
        range: "initControl",
        reqBody: {
            type: "initial"
        },
        computeStateColor: (varValues: VariableValue[]): string => {
            if (varValues.length < 2) return PiezometerColors.BLACK;

            const pnpInit = varValues[0] || null;
            const pnpEnd = varValues[varValues.length - 1] || null;
            const delta = pnpEnd._value - pnpInit._value;

            return getStateColorInitControl(delta);
        },
        displayInfo: (varValues: VariableValue[]): string => {
            if (varValues.length < 2) return "";

            const pnpInit = varValues[0] || null;
            const pnpEnd = varValues[varValues.length - 1] || null;
            const delta = pnpEnd._value - pnpInit._value;

            return `
                <div>
                    Delta: ${delta.toFixed(2)}
                </div>
                <div>
                     ${i18n.t("CPPiezometer.initDate")}: ${new Date(
                pnpInit._time
            ).toLocaleDateString()} (${pnpInit._value.toFixed(2)})
                </div>
                <div>
                     ${i18n.t("CPPiezometer.latestDate")}: ${new Date(
                pnpEnd._time
            ).toLocaleDateString()} (${pnpEnd._value.toFixed(2)})
                </div>
            `;
        },
        diffDays: () => getDiffDays(new Date(0), new Date()),
        getLegend: () => {
            return [
                { color: PiezometerColors.GREEN, text: "delta <= -1" },
                {
                    color: PiezometerColors.BLUE,
                    text: "-1 <= delta < -25"
                },
                {
                    color: PiezometerColors.CYAN,
                    text: "-25 <= delta < -50"
                },
                {
                    color: PiezometerColors.ORANGE,
                    text: "-50 <= delta < -100"
                },
                {
                    color: PiezometerColors.RED,
                    text: "-100 <= delta < -200"
                },
                { color: PiezometerColors.PURPLE, text: "<= -200" },
                {
                    color: PiezometerColors.BLACK,
                    text: `${i18n.t("CPPiezometer.noData")}`
                }
            ];
        }
    }
];

export const cpTimeRangesAqConfig: CPTimeRangeConfig[] = [
    {
        range: "latest",
        reqBody: {
            type: "latest"
        },
        computeStateColor: (varValues: VariableValue[]): string => {
            if (!varValues || varValues.length === 0)
                return PiezometerColors.BLACK;

            const avg = arrayAvg(varValues.map(tv => tv._value));
            return getStateColorLatest(avg);
        },
        displayInfo: (varValues: VariableValue[], numPiez?: number): string => {
            if (!varValues || varValues.length === 0) return "";

            const avg = arrayAvg(varValues.map(tv => tv._value));
            return `
                <div>
                    PNP (${i18n.t("CPPiezometer.avg")}): ${avg.toFixed(2)}
                </div>
                ${
                    !numPiez
                        ? ""
                        : `<div>
                    ${i18n.t("CPPiezometer.numPiezometers")}: ${numPiez}
                </div>`
                }
            `;
        }
    },
    {
        range: "lastYear",
        reqBody: {
            type: "custom",
            range: {
                start: getLast365DaysDate().toISOString(),
                end: new Date().toISOString()
            }
        },
        computeStateColor: (varValues: VariableValue[]): string => {
            if (!varValues || varValues.length === 0)
                return PiezometerColors.BLACK;

            const { delta } = computeAquiferDataByDate(
                varValues,
                getLast365DaysDate()
            );

            if (isNaN(delta)) return PiezometerColors.BLACK;

            return getStateColorInitYear(delta);
        },
        displayInfo: (varValues: VariableValue[], numPiez?: number): string => {
            if (!varValues || varValues.length === 0) return "";

            const { avgInit, avgEnd, delta } = computeAquiferDataByDate(
                varValues,
                getLast365DaysDate()
            );

            if (isNaN(delta)) return "";

            return `
                <div>
                    Delta: ${delta.toFixed(2)}
                </div>
                <div>
                    ${i18n.t("CPPiezometer.initAvg")}: ${avgInit.toFixed(2)}
                </div>
                <div>
                    ${i18n.t("CPPiezometer.endAvg")}: ${avgEnd.toFixed(2)}
                </div>
                ${
                    !numPiez
                        ? ""
                        : `<div>
                    ${i18n.t("CPPiezometer.numPiezometers")}: ${numPiez}
                </div>`
                }
            `;
        }
    },
    {
        range: "initYear",
        reqBody: {
            type: "custom",
            range: {
                start: getCurYearDate().toISOString(),
                end: new Date().toISOString()
            }
        },
        computeStateColor: (varValues: VariableValue[]): string => {
            if (!varValues || varValues.length === 0)
                return PiezometerColors.BLACK;

            const { delta } = computeAquiferDataByDate(
                varValues,
                getCurYearDate()
            );

            if (isNaN(delta)) return PiezometerColors.BLACK;

            return getStateColorInitYear(delta);
        },
        displayInfo: (varValues: VariableValue[], numPiez?: number): string => {
            if (!varValues || varValues.length === 0) return "";

            const { avgInit, avgEnd, delta } = computeAquiferDataByDate(
                varValues,
                getCurYearDate()
            );

            if (isNaN(delta)) return "";

            return `
                <div>
                    Delta: ${delta.toFixed(2)}
                </div>
                <div>
                    ${i18n.t("CPPiezometer.initAvg")}: ${avgInit.toFixed(2)}
                </div>
                <div>
                    ${i18n.t("CPPiezometer.endAvg")}: ${avgEnd.toFixed(2)}
                </div>
                ${
                    !numPiez
                        ? ""
                        : `<div>
                    ${i18n.t("CPPiezometer.numPiezometers")}: ${numPiez}
                </div>`
                }
            `;
        }
    },
    {
        range: "initHydroYear",
        reqBody: {
            type: "custom",
            range: {
                start: getHydroYearDate().toISOString(),
                end: new Date().toISOString()
            }
        },
        computeStateColor: (varValues: VariableValue[]): string => {
            if (!varValues || varValues.length === 0)
                return PiezometerColors.BLACK;

            const { delta } = computeAquiferDataByDate(
                varValues,
                getHydroYearDate()
            );

            if (isNaN(delta)) return PiezometerColors.BLACK;

            return getStateColorInitYear(delta);
        },
        displayInfo: (varValues: VariableValue[], numPiez?: number): string => {
            if (!varValues || varValues.length === 0) return "";

            const { avgInit, avgEnd, delta } = computeAquiferDataByDate(
                varValues,
                getHydroYearDate()
            );

            if (isNaN(delta)) return "";

            return `
                <div>
                    Delta: ${delta.toFixed(2)}
                </div>
                <div>
                    ${i18n.t("CPPiezometer.initAvg")}: ${avgInit.toFixed(2)}
                </div>
                <div>
                    ${i18n.t("CPPiezometer.endAvg")}: ${avgEnd.toFixed(2)}
                </div>
                ${
                    !numPiez
                        ? ""
                        : `<div>
                    ${i18n.t("CPPiezometer.numPiezometers")}: ${numPiez}
                </div>`
                }
            `;
        }
    },
    {
        range: "initControl",
        reqBody: {
            type: "initial"
        },
        computeStateColor: (varValues: VariableValue[]): string => {
            if (varValues.length < 2) return PiezometerColors.BLACK;

            const { delta } = computeAquiferInitControlData(varValues);

            if (isNaN(delta)) return PiezometerColors.BLACK;

            return getStateColorInitControl(delta);
        },
        displayInfo: (varValues: VariableValue[], numPiez?: number): string => {
            if (varValues.length < 2) return "";

            const { delta, avgInit, avgEnd } = computeAquiferInitControlData(
                varValues
            );

            if (isNaN(delta)) return "";

            return `
                <div>
                    Delta: ${delta.toFixed(2)}
                </div>
                <div>
                    ${i18n.t("CPPiezometer.initAvg")}: ${avgInit.toFixed(2)}
                </div>
                <div>
                    ${i18n.t("CPPiezometer.endAvg")}: ${avgEnd.toFixed(2)}
                </div>
                ${
                    !numPiez
                        ? ""
                        : `<div>
                    ${i18n.t("CPPiezometer.numPiezometers")}: ${numPiez}
                </div>`
                }
            `;
        }
    }
];
