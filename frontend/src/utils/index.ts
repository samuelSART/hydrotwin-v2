import { TYPOLOGIES_UNITS, VARIABLE_TYPOLOGIES } from "@/config";
import { TypedVariableValue } from "@/interfaces";
import { i18n } from "@/plugins/i18n";

/**
 * @param {Function} func
 * @param {number} wait
 * @param {boolean} immediate
 * @return {*}
 */
export const debounce = (fn: Function, ms = 300) => {
    let timeoutId: ReturnType<typeof setTimeout>;
    return function(this, ...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), ms);
    };
};

export const sleep = async (delay: number) => {
    return new Promise(resolve => setTimeout(resolve, delay));
};

export const groupBy = (xs, key) => {
    return xs.reduce(function(rv, x) {
        (rv[x[key]] = rv[x[key]] || []).push(x);
        return rv;
    }, {});
};

export const arrayAvg = (data: number[]) => {
    return data.reduce((a, b) => a + b, 0) / data.length;
};

export const downloadCSV = (csv: string, fileName: string) => {
    const anchor = document.createElement("a");
    anchor.href = "data:text/csv;charset=utf-8," + encodeURIComponent(csv);
    anchor.target = "_blank";
    anchor.download = `${fileName}.csv`;
    anchor.click();
};

export const exportDataToCSV = (
    timeSeries: TypedVariableValue[][],
    variableCode: string
) => {
    let csv = "variablecode,date,type,value\n";
    for (const tSerie of timeSeries) {
        tSerie.forEach(({ _time, _value, type = "-?-" }) => {
            // format timestamp to dd-mm-yyyy hh:mm:ss
            const date = new Date(_time)
                .toLocaleString("es-ES")
                .replace(/\//g, "-")
                .replace(/,/g, " ");
            const value = _value.toFixed(4);
            csv += [variableCode, date, type, value].join(",");
            csv += "\n";
        });
    }

    return csv;
};

export const getTypologyUnitText = (typology: string): string => {
    const typologyUnit = TYPOLOGIES_UNITS.get(typology) || "";
    const typologyText =
        i18n.t(`form.variableTypology.${VARIABLE_TYPOLOGIES.get(typology)}`) ||
        "";

    if (typologyUnit) {
        return `${typologyText} (${typologyUnit})`;
    }

    return `${typologyText}`;
};
