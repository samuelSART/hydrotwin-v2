<template>
    <BaseDialog v-model="dialogShown" :loading="loading" :title="damName">
        <template #form>
            <BasicForm
                ref="basicForm"
                v-model="formFilter"
                :variablesOptions="variableOptions"
                :timeRangesOptions="timeRangesOptions"
                :predictionsOptions="predictionOptions"
                :simulationsOptions="simulationOptions"
                @on-refresh="handleFormRefresh"
            />
        </template>
        <template #plot>
            <OptionChart
                ref="chart"
                height="400px"
                :chart-options="variableOption"
            />
        </template>
    </BaseDialog>
</template>

<script lang="ts">
import {
    getLineChartOption,
    getEmptyOption,
    getForecastingSeries
} from "@/config/charts";
import { EChartsOption } from "echarts";
import {
    Component,
    Vue,
    ModelSync,
    Prop,
    Watch,
    Ref
} from "vue-property-decorator";

import {
    DamResponse,
    DamVariable,
    DamVariableResponse as dvr,
    VariableValue,
    VariableValueResponse as vvr,
    ForecastValue,
    ForecastResponse,
    BasicFormInterface,
    ComboBoxItem,
    FormBtnAction,
    TypedVariableValue,
    SimulationResponse
} from "@/interfaces";
import OptionChart from "../charts/OptionChart.vue";
import { EXPORT_PLOT_SVG, VARIABLE_TYPOLOGIES } from "@/config";
import { downloadCSV, exportDataToCSV, getTypologyUnitText } from "@/utils";

interface DatePeriod {
    startDate: Date;
    endDate: Date;
}

interface VolumeLimits {
    max: number;
    min: number;
}

export const TIME_RANGE = new Map<string, string>([
    ["1", "lastDay"],
    ["7", "lastWeek"],
    ["14", "lastTwoWeeks"],
    ["30", "lastMonth"],
    ["90", "lastThreeMonths"],
    ["180", "lastSixMonths"],
    ["365", "lastYear"],
    ["custom", "custom"]
]);

const PREDICTION_RANGE = new Map<number, string>([
    [1, "forecastingType1"],
    [2, "forecastingType2"],
    [3, "forecastingType3"],
    [4, "forecastingType4"],
    [5, "forecastingType5"]
]);

const SIMULATION_RANGE = new Map<number, string>([
    [0, "simulationType1"],
    [1, "simulationType2"]
]);

interface DamPeriod {
    months: [number, number, number];
}

export const DAM_PERIODS = new Map<string, DamPeriod>([
    ["ene_mar", { months: [1, 2, 3] }],
    ["abr_jun", { months: [4, 5, 6] }],
    ["jul_sep", { months: [7, 8, 9] }],
    ["oct_dic", { months: [10, 11, 12] }]
]);

@Component({
    components: {
        BaseDialog: () => import("@/components/dialogs/BaseDialog.vue"),
        OptionChart: () => import("@/components/charts/OptionChart.vue"),
        BasicForm: () => import("@/components/forms/BasicForm.vue")
    }
})
export default class DamVariablesDialog extends Vue {
    @ModelSync("dialogShownValue", "change", { type: Boolean })
    dialogShown!: boolean;

    @Prop({ type: String, required: true })
    damName!: string;

    @Prop({ type: String, required: true })
    damCode!: string;

    @Ref("basicForm") basicFormRef;
    @Ref("chart") readonly chart!: OptionChart;

    loading = false;

    formFilter: BasicFormInterface = {
        valid: false,
        variable: "",
        timeRange: "",
        customTimeRange: [],
        predictionEnabled: true,
        forecasting: 1,
        simulationEnabled: false,
        simulation: 0
    };

    formRules = {
        variable: [
            v => !!v.value || this.$t("damVariablesDialog.variableRequired")
        ],
        timeRange: [
            v => !!v || this.$t("damVariablesDialog.timeRangeRequired")
        ],
        customTimeRange: [v => this.customTimeRangeRule(v)]
    };

    customTimeRangeDisabled = true;

    variableOptions: ComboBoxItem[] = [];
    timeRangesOptions: ComboBoxItem[] = [];
    variableTypologies!: Map<string, string>;

    variableOption: EChartsOption = {};

    @Watch("dialogShown")
    async onDialogShown() {
        if (!this.dialogShown) {
            this.reset();
            return;
        }
        try {
            const damVariablesResponse = await this.$api.getDamVariables<dvr>(
                this.damCode
            );

            if (damVariablesResponse.ok) {
                this.variableTypologies = new Map([]);
                this.variableOptions = damVariablesResponse.data.map(
                    (damVariable: DamVariable) => {
                        this.variableTypologies.set(
                            damVariable.variable,
                            damVariable.typology
                        );

                        return {
                            value: damVariable.variable,
                            text:
                                (this.$t(
                                    `form.variableTypology.${VARIABLE_TYPOLOGIES.get(
                                        damVariable.typology
                                    )}`
                                ) || damVariable.typology) +
                                ` (${damVariable.variable})`
                        };
                    }
                );
                this.timeRangesOptions = Array.from(TIME_RANGE).map(
                    ([key, value]) => {
                        return {
                            value: key,
                            text: this.$t(`form.timeRange.${value}`)
                        };
                    }
                );
            }
        } catch (error) {
            console.log(error);
        }
    }

    @Watch("formFilter.variable")
    onVariableChanged() {
        const typology = this.variableTypologies.get(this.formFilter.variable);

        const levelTypology = "N";
        this.formFilter.simulationEnabled = typology === levelTypology;
    }

    /**
     * Prediction ranges options
     */
    get predictionOptions() {
        return Array.from(PREDICTION_RANGE).map(([key, value]) => {
            return {
                value: key,
                text: this.$t(`form.predictions.${value}`)
            };
        });
    }

    /**
     * Check if the custom time range is selected
     * @return {void}
     */
    checkCustomTimeRange(): void {
        if (this.formFilter.timeRange === "custom") {
            this.customTimeRangeDisabled = false;
        } else {
            this.customTimeRangeDisabled = true;
        }
    }

    /**
     * Custom time range rule
     * @param {any} v Value of the custom time range
     * @return {string | boolean} error message if the custom time range is not valid or true if it is valid
     */
    customTimeRangeRule(v) {
        if (this.formFilter.timeRange === "custom" && v === "") {
            return String(
                this.$t("damVariablesDialog.customTimeRangeRequired")
            );
        } else {
            return true;
        }
    }

    /**
     * Reset from values and plot
     * @return {void}
     */
    reset(): void {
        this.formFilter = {
            valid: false,
            variable: "",
            timeRange: "",
            customTimeRange: [],
            predictionEnabled: true,
            forecasting: 1,
            simulationEnabled: false,
            simulation: 0
        };
        this.basicFormRef.resetValidation();
        if (this.chart) {
            this.chart.clearChart();
        }
    }

    /**
     * Clear chart
     * @return {void}
     */
    clearChart(): void {
        if (!this.chart) return;
        this.chart.clearChart();
    }

    /**
     * Handle variable form submit
     * @return {void}
     */
    async handleFormRefresh(config: FormBtnAction): Promise<void> {
        const selectedVariable = this.variableOptions.find(
            variable => variable.value === this.formFilter.variable
        );

        let limits: VolumeLimits = { max: 0, min: 0 };
        if (
            this.$t("form.variableTypology.volume") === selectedVariable?.text
        ) {
            limits = await this.getDamVolumeLimits(
                selectedVariable.value.toString()
            );
        }

        this.plotVariable(limits, config.forecasting, config.simulation);
    }

    /**
     * Get date range period
     * @params {BasicFormInterface} formFilter Form object
     * @return {DatePeriod} Current date period
     */
    getDatePeriod(formFilter: BasicFormInterface): DatePeriod {
        let startDate: Date, endDate: Date;

        if (formFilter.timeRange === "custom") {
            formFilter.customTimeRange.sort((a, b) => {
                return new Date(a).getTime() - new Date(b).getTime();
            });
            startDate = new Date(formFilter.customTimeRange[0]);
            endDate = new Date(
                new Date(formFilter.customTimeRange[1]).setHours(23, 59, 59)
            );
        } else {
            startDate = new Date(
                new Date().setDate(
                    new Date().getDate() - parseInt(formFilter.timeRange)
                )
            );
            endDate = new Date(new Date().setHours(23, 59, 59));
        }

        return { startDate, endDate };
    }

    /**
     * Get previous date range period
     * @params {BasicFormInterface} formFilter Form object
     * @return {DatePeriod} Previous date period
     */
    getPreviousDatePeriod(formFilter: BasicFormInterface): DatePeriod {
        let startDate: Date, endDate: Date;

        if (formFilter.timeRange === "custom") {
            formFilter.customTimeRange.sort((a, b) => {
                return new Date(a).getTime() - new Date(b).getTime();
            });
            startDate = new Date(
                new Date(formFilter.customTimeRange[0]).setFullYear(
                    new Date(formFilter.customTimeRange[0]).getFullYear() - 1
                )
            );
            endDate = new Date(
                new Date(
                    new Date(formFilter.customTimeRange[1]).setFullYear(
                        new Date(formFilter.customTimeRange[1]).getFullYear() -
                            1
                    )
                ).setHours(23, 59, 59)
            );
        } else {
            startDate = new Date(
                new Date(
                    new Date().setDate(
                        new Date().getDate() - parseInt(formFilter.timeRange)
                    )
                ).setFullYear(
                    new Date(
                        new Date().setDate(
                            new Date().getDate() -
                                parseInt(formFilter.timeRange)
                        )
                    ).getFullYear() - 1
                )
            );
            endDate = new Date(
                new Date(
                    new Date().setFullYear(new Date().getFullYear() - 1)
                ).setHours(23, 59, 59)
            );
        }

        return { startDate, endDate };
    }

    /**
     * Get dam volume limits
     * @return {Promise<VolumeLimits>}
     */
    async getDamVolumeLimits(variable): Promise<VolumeLimits> {
        // Get dam
        const response = await this.$api.getDamByVariable<DamResponse>(
            variable
        );
        // Get current period: ene_mar, abr_jun, jul_sep, oct_dic
        const period = this.getCurrentDatePeriod();
        return {
            min: response.data[0][`min_${period}`],
            max: response.data[0][`max_${period}`]
        };
    }

    /**
     * Get current period for volume limits
     * @return {string} Month period
     */
    getCurrentDatePeriod(): string {
        let currentPeriod;

        DAM_PERIODS.forEach((period: DamPeriod, key: string) => {
            if (period.months.includes(new Date().getMonth() + 1)) {
                currentPeriod = key;
            }
        });

        return currentPeriod;
    }

    /**
     * Plot variable data
     * @return {Promise<void>}
     */
    async plotVariable(
        limits: VolumeLimits,
        forecasting: number | undefined,
        simulation: number | undefined
    ): Promise<void> {
        this.loading = true;

        try {
            const datePeriod = this.getDatePeriod(this.formFilter);

            const variableValues:
                | VariableValue[]
                | undefined = await this.getVariableValues(
                this.formFilter.variable,
                datePeriod.startDate,
                datePeriod.endDate
            );

            /**
             * If there is no data for current or previous period
             */
            if (!variableValues) {
                this.variableOption = {
                    ...getEmptyOption(`${this.$t("chart.noData")}`)
                };
                this.loading = false;
                return;
            }

            let forecastingRes: ForecastResponse | undefined | void = undefined;

            if (forecasting) {
                forecastingRes = await this.$api
                    .getForecast<ForecastResponse>(
                        this.formFilter.variable,
                        forecasting
                    )
                    .catch(e => console.error(e));
            }

            let simulationRes: SimulationResponse | undefined = undefined;
            if (simulation !== undefined) {
                simulationRes = await this.$api.getSimulation<
                    SimulationResponse
                >(
                    [this.formFilter.variable],
                    datePeriod.startDate,
                    datePeriod.endDate,
                    simulation,
                    "mean",
                    "1d"
                );
            }

            this.variableOption = { ...getLineChartOption({}) };

            /**
             * XAxis
             */
            this.variableOption.xAxis = {
                ...this.variableOption.xAxis,
                data: undefined,
                type: "time",
                splitArea: {
                    show: false
                }
            };

            this.variableOption.yAxis = {
                ...this.variableOption.yAxis,
                name: this.getYaxisName(
                    this.variableTypologies.get(this.formFilter.variable)
                ),
                nameLocation: "middle",
                nameGap: 30,
                nameTextStyle: {
                    color: "#000000",
                    fontWeight: "bold"
                }
            };

            /**
             * Activate legend to hide/show generator flow
             */
            const dataSeriesName = this.$t("damVariablesDialog.value");
            const limitMaxSeriesName = this.$t("damVariablesDialog.maxVolume");
            const limitMinSeriesName = this.$t("damVariablesDialog.minVolume");
            const simulationsSeriesname = this.$t(
                "form.simulations.simulationSeries"
            );

            this.variableOption.legend = {
                data: [
                    dataSeriesName,
                    limitMaxSeriesName,
                    limitMinSeriesName,
                    simulationsSeriesname
                ]
            };

            /**
             * Data as arrays of [{timestamp}, {value}]
             */
            const typology = this.variableTypologies.get(
                this.formFilter.variable
            );
            const volumeTypology = "V";

            const data = variableValues.map(
                ({ _time, _value }: VariableValue) => {
                    if (typology === volumeTypology) {
                        return [+new Date(_time), (_value / 1000).toFixed(2)];
                    }

                    return [+new Date(_time), _value];
                }
            );

            const serieCopy = this.variableOption.series
                ? { ...this.variableOption.series[0] }
                : {};

            this.variableOption.series = [];
            this.variableOption.series.push({
                ...serieCopy,
                name: dataSeriesName,
                data,
                symbol: "none"
            });

            /**
             * Volume limits
             */
            if (limits.max !== 0) {
                this.variableOption.series.push({
                    name: `${limitMaxSeriesName}`,
                    type: "line",
                    symbol: "line",
                    data: [],
                    markLine: {
                        symbol: "none",
                        label: {
                            position: "middle",
                            formatter: `${this.$t(
                                "damVariablesDialog.maxVolume"
                            )}: ${limits.max} hm${String.fromCharCode(179)}`
                        },
                        data: [
                            {
                                yAxis: limits.max
                            }
                        ]
                    },
                    animationDuration: 700,
                    animationEasing: "quadraticOut"
                });
            }

            if (limits.min !== 0) {
                this.variableOption.series.push({
                    name: `${limitMinSeriesName}`,
                    type: "line",
                    symbol: "line",
                    data: [],
                    markLine: {
                        symbol: "none",
                        label: {
                            position: "middle",
                            formatter: `${this.$t(
                                "damVariablesDialog.minVolume"
                            )}: ${limits.min} hm${String.fromCharCode(179)}`
                        },
                        data: [
                            {
                                yAxis: limits.min
                            }
                        ]
                    },
                    animationDuration: 700,
                    animationEasing: "quadraticOut"
                });
            }

            this.variableOption.toolbox = {
                feature: {
                    dataZoom: {
                        brushStyle: {
                            color: "gray",
                            opacity: 0.25
                        }
                    },
                    restore: {},
                    myExport: {
                        show: true,
                        title: "csv",
                        icon: EXPORT_PLOT_SVG,
                        onclick: () => {
                            const rData: TypedVariableValue[] = variableValues.map(
                                (value: VariableValue) => {
                                    return { ...value, type: "real" };
                                }
                            );

                            let fData: TypedVariableValue[] = [];
                            if (forecastingRes && forecastingRes.ok) {
                                const forecastingData = forecastingRes.data;
                                fData = forecastingData.map(
                                    ({ ds, yhat }: ForecastValue) => {
                                        return {
                                            _time: ds,
                                            _value: yhat,
                                            type: "predicted",
                                            variableCode: this.formFilter
                                                .variable
                                        };
                                    }
                                );
                            }

                            const csvData = exportDataToCSV(
                                [rData, fData],
                                this.formFilter.variable
                            );

                            downloadCSV(csvData, this.formFilter.variable);
                        }
                    }
                }
            };

            /**
             * Forecasting
             */
            if (
                forecastingRes &&
                forecastingRes.ok &&
                forecastingRes.data.length
            ) {
                const fcSeries = getForecastingSeries(forecastingRes.data, {
                    serieCopy,
                    areaColor: "#ccc"
                });

                this.variableOption.series.push(...fcSeries);
            }

            /**
             * Simulation
             */
            if (
                simulationRes &&
                simulationRes.ok &&
                simulationRes.data.length
            ) {
                const sData = simulationRes.data.map(
                    ({ _time, _value }: VariableValue) => [
                        +new Date(_time),
                        _value.toFixed(3)
                    ]
                );

                this.variableOption.series.push({
                    ...serieCopy,
                    name: simulationsSeriesname,
                    data: sData,
                    symbol: "none"
                });
            }
        } catch (error) {
            if (error instanceof Error) {
                console.log(error);
            }
        } finally {
            this.loading = false;
        }
    }

    /**
     * Get Yaxis name
     * @return {string}
     */
    getYaxisName(typology): string {
        console.log(typology);

        return getTypologyUnitText(typology);
    }

    /**
     * Get the variable values
     * @param {string} variable Variable code
     * @param {Date} startDate Start date
     * @param {Date} endDate End date
     * @returns {Promise<VariableValue[]>} Variable values
     */
    async getVariableValues(
        variable: string,
        startDate: Date,
        endDate: Date
    ): Promise<VariableValue[] | undefined> {
        const variableValues = await this.$api.getVariablesValues<vvr>(
            [variable],
            startDate,
            endDate
        );
        return variableValues.data;
    }

    /**
     * Simulation ranges options
     */
    get simulationOptions() {
        return Array.from(SIMULATION_RANGE).map(([key, value]) => {
            return {
                value: key,
                text: this.$t(`form.simulations.${value}`)
            };
        });
    }
}
</script>

<style>
.serieName {
    font-weight: bold;
    color: blue;
}
.compareSerieName {
    font-weight: bold;
    color: red;
}
.predictionSerieName {
    font-weight: bold;
    color: black;
}
</style>
