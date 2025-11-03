import { EChartsOption } from "echarts";
import { ForecastValue } from "@/interfaces";
import { i18n } from "@/plugins/i18n";

type OptionAxisType = "category" | "value" | "time" | "log" | undefined;

type ChartOptions = {
    xAxisName?: string;
    yAxisName?: string;
    xAxisType?: OptionAxisType;
    yAxisType?: OptionAxisType;
};

// Empty chart with a centered title
export const getEmptyOption = (text = "No data") => {
    return {
        title: {
            show: true,
            textStyle: {
                color: "#bcbcbc"
            },
            left: "center",
            top: "center",
            text
        }
    };
};

export const getLineChartOption = ({
    xAxisName = "",
    yAxisName = ""
}: ChartOptions): EChartsOption => {
    return {
        xAxis: {
            data: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            boundaryGap: false,
            axisTick: {
                show: false
            },
            name: xAxisName,
            nameLocation: "middle",
            nameGap: 30,
            nameTextStyle: {
                fontWeight: "bold"
            }
        },
        grid: {
            left: 20,
            right: 20,
            bottom: 20,
            top: 30,
            containLabel: true
        },
        tooltip: {
            trigger: "axis",
            axisPointer: {
                type: "cross"
            },
            padding: [5, 10]
        },
        yAxis: {
            axisTick: {
                show: false
            },
            name: yAxisName,
            nameTextStyle: {
                fontWeight: "bold"
            }
        },
        series: [
            {
                name: "actual",
                smooth: true,
                type: "line",
                emphasis: {
                    focus: "series"
                },
                data: [10, 40, 60, 2, 5, 40, 0].map(value => value * 3),
                animationDuration: 700,
                animationEasing: "quadraticOut"
            },
            {
                name: "actual2",
                smooth: true,
                type: "line",
                emphasis: {
                    focus: "series"
                },
                data: [10, 40, 60, 2, 5, 40, 0].map(value => value * 2),
                animationDuration: 700,
                animationEasing: "quadraticOut"
            },
            {
                name: "actual3",
                smooth: true,
                type: "line",
                emphasis: {
                    focus: "series"
                },
                data: [10, 40, 60, 2, 5, 40, 0].map(value => value * 1),
                animationDuration: 700,
                animationEasing: "quadraticOut"
            }
        ]
    };
};

export const getBarChartOption = ({
    xAxisName = "",
    yAxisName = "",
    xAxisType = "category",
    yAxisType = "value"
}: ChartOptions): EChartsOption => {
    return {
        tooltip: {
            trigger: "axis",
            axisPointer: {
                type: "shadow"
            },
            backgroundColor: "rgba(255,255,255,0.85)"
        },
        grid: {
            left: 10,
            right: 10,
            bottom: 22,
            top: yAxisName ? 30 : 10,
            containLabel: true
        },
        xAxis: {
            type: xAxisType,
            data: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            axisTick: {
                alignWithLabel: true
            },
            name: xAxisName,
            nameLocation: "middle",
            nameGap: 30,
            nameTextStyle: {
                fontWeight: "bold"
            }
        },
        yAxis: {
            type: yAxisType,
            axisTick: {
                show: false
            },
            name: yAxisName,
            nameTextStyle: {
                fontWeight: "bold"
            }
        },
        series: [
            {
                name: "pageA",
                type: "bar",
                stack: "vistors",
                barWidth: "60%",
                data: [79, 52, 200, 334, 390, 330, 220],
                animationDuration: 500
            },
            {
                name: "pageB",
                type: "bar",
                stack: "vistors",
                barWidth: "60%",
                data: [80, 52, 200, 334, 390, 330, 220],
                animationDuration: 500
            },
            {
                name: "pageC",
                type: "bar",
                stack: "vistors",
                barWidth: "60%",
                data: [30, 52, 200, 334, 390, 330, 220],
                animationDuration: 500
            }
        ]
    };
};

export const getPieChartOption = (): EChartsOption => {
    return {
        tooltip: {
            trigger: "item"
        },
        legend: {
            orient: "horizontal",
            bottom: "bottom"
        },
        series: [
            {
                name: "Regions",
                type: "pie",
                radius: "65%",
                data: [
                    { value: 1048, name: "Asia" },
                    { value: 735, name: "Europe" },
                    { value: 580, name: "Americas" },
                    { value: 484, name: "Africa" }
                ],
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: "rgba(0, 0, 0, 0.5)"
                    }
                }
            }
        ]
    };
};

/**
 *
 * @param forecastingData Data coming from forecaster
 * @param options.serieCopy Serie default format
 * @param options.areaColor stack area color
 * @returns {Array} Series
 */
export const getForecastingSeries = (
    forecastingData: ForecastValue[],
    {
        serieCopy = undefined,
        areaColor = "#ccc"
    }: { serieCopy; areaColor: string }
) => {
    const fData = forecastingData.map(({ ds, yhat }: ForecastValue) => [
        ds,
        yhat.toFixed(3)
    ]);

    // forecasting series
    const fSerie = {
        ...serieCopy,
        name: i18n.t("form.predictions.forecasting"),
        data: fData,
        symbol: "none",
        lineStyle: {
            type: "solid"
        }
    };

    // lower data
    const lData = forecastingData.map(
        // eslint-disable-next-line @typescript-eslint/camelcase
        ({ ds, yhat_lower }: ForecastValue) => [ds, yhat_lower.toFixed(3)]
    );

    const lSeries = {
        ...serieCopy,
        name: i18n.t("form.predictions.forecastingLower"),
        data: lData,
        symbol: "none",
        lineStyle: {
            opacity: 0
        },
        areaStyle: {
            color: "white",
            origin: "start"
        }
    };

    // upper data
    const uData = forecastingData.map(
        // eslint-disable-next-line @typescript-eslint/camelcase
        ({ ds, yhat_upper }: ForecastValue) => [ds, yhat_upper.toFixed(3)]
    );

    const uSeries = {
        ...serieCopy,
        name: i18n.t("form.predictions.forecastingUpper"),
        data: uData,
        symbol: "none",
        lineStyle: {
            opacity: 0
        },
        areaStyle: {
            color: areaColor,
            origin: "start"
        }
    };

    return [fSerie, uSeries, lSeries];
};
