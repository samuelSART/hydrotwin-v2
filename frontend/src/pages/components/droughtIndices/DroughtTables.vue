<template>
    <div class="my-5">
        <v-row class="d-flex justify-center ma-0">
            <v-col class="my-0 py-0" xs="4" sm="4" md="3">
                <v-autocomplete
                    dense
                    v-model="state"
                    :items="states"
                    :label="$t('droughtIndices.state')"
                ></v-autocomplete>
            </v-col>
            <v-col class="my-0 py-0" xs="4" sm="4" md="3">
                <CalendarInput
                    v-model="month"
                    @change="formatMonth"
                    type="month"
                    :availableDates="[]"
                />
            </v-col>
            <v-col class="my-0 py-0" xs="4" sm="4" md="3">
                <v-btn
                    color="secondary"
                    class="white--text"
                    @click="fetchDroughtIndices"
                    block
                >
                    {{ $t("droughtIndices.generateTable") }}
                    <v-icon right dark>mdi-refresh</v-icon>
                </v-btn>
            </v-col>
        </v-row>
        <v-row class="d-flex justify-center ma-0">
            <v-col v-if="state == states[0]" xs="12" sm="10" md="8">
                <v-card>
                    <v-card-title>{{ this.state }}</v-card-title>
                    <v-simple-table>
                        <thead>
                            <tr>
                                <th>
                                    {{
                                        this.$t(
                                            "droughtIndices.territorialUnit"
                                        )
                                    }}
                                </th>
                                <th>{{ this.$t("droughtIndices.index") }}</th>
                                <th>
                                    {{ this.$t("droughtIndices.situation") }}
                                </th>
                                <th>{{ this.$t("droughtIndices.scenary") }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>
                                    UTE I Principal
                                    <v-tooltip bottom color="white">
                                        <template
                                            v-slot:activator="{ on, attrs }"
                                        >
                                            <v-btn
                                                v-bind="attrs"
                                                v-on="on"
                                                class="mx-2 float-right"
                                                fab
                                                x-small
                                                dark
                                                color="indigo darken-3"
                                            >
                                                <v-icon dark>
                                                    mdi-plus
                                                </v-icon>
                                            </v-btn>
                                        </template>
                                        <v-simple-table>
                                            <tbody>
                                                <tr
                                                    v-if="
                                                        this.tableData.CUENCA >=
                                                            0.5
                                                    "
                                                    class="light-green accent-4"
                                                >
                                                    <td>
                                                        {{
                                                            this.tableData
                                                                .CUENCA
                                                        }}
                                                    </td>
                                                    <td>CUENCA</td>
                                                </tr>
                                                <tr
                                                    v-if="
                                                        this.tableData.CUENCA <
                                                            0.5 &&
                                                            this.tableData
                                                                .CUENCA >= 0.3
                                                    "
                                                    class="yellow"
                                                >
                                                    <td>
                                                        {{
                                                            this.tableData
                                                                .CUENCA
                                                        }}
                                                    </td>
                                                    <td>CUENCA</td>
                                                </tr>
                                                <tr
                                                    v-if="
                                                        this.tableData.CUENCA <
                                                            0.3 &&
                                                            this.tableData
                                                                .CUENCA >= 0.15
                                                    "
                                                    class="orange lihgten-1"
                                                >
                                                    <td>
                                                        {{
                                                            this.tableData
                                                                .CUENCA
                                                        }}
                                                    </td>
                                                    <td>CUENCA</td>
                                                </tr>
                                                <tr
                                                    v-if="
                                                        this.tableData.CUENCA !=
                                                            null &&
                                                            this.tableData
                                                                .CUENCA < 0.15
                                                    "
                                                    class="red daken-1"
                                                >
                                                    <td>
                                                        {{
                                                            this.tableData
                                                                .CUENCA
                                                        }}
                                                    </td>
                                                    <td>CUENCA</td>
                                                </tr>
                                                <tr
                                                    v-if="
                                                        this.tableData
                                                            .TRASVASE >= 0.5
                                                    "
                                                    class="light-green accent-4"
                                                >
                                                    <td>
                                                        {{
                                                            this.tableData
                                                                .TRASVASE
                                                        }}
                                                    </td>
                                                    <td>TRASVASE</td>
                                                </tr>
                                                <tr
                                                    v-if="
                                                        this.tableData
                                                            .TRASVASE < 0.5 &&
                                                            this.tableData
                                                                .TRASVASE >= 0.3
                                                    "
                                                    class="yellow"
                                                >
                                                    <td>
                                                        {{
                                                            this.tableData
                                                                .TRASVASE
                                                        }}
                                                    </td>
                                                    <td>TRASVASE</td>
                                                </tr>
                                                <tr
                                                    v-if="
                                                        this.tableData
                                                            .TRASVASE < 0.3 &&
                                                            this.tableData
                                                                .TRASVASE >=
                                                                0.15
                                                    "
                                                    class="orange lighten-1"
                                                >
                                                    <td>
                                                        {{
                                                            this.tableData
                                                                .TRASVASE
                                                        }}
                                                    </td>
                                                    <td>TRASVASE</td>
                                                </tr>
                                                <tr
                                                    v-if="
                                                        this.tableData
                                                            .TRASVASE != null &&
                                                            this.tableData
                                                                .TRASVASE < 0.15
                                                    "
                                                    class="red darken-1"
                                                >
                                                    <td>
                                                        {{
                                                            this.tableData
                                                                .TRASVASE
                                                        }}
                                                    </td>
                                                    <td>TRASVASE</td>
                                                </tr>
                                            </tbody>
                                        </v-simple-table>
                                    </v-tooltip>
                                </td>
                                <td
                                    v-if="this.tableData.GLOBAL >= 0.5"
                                    class="light-green accent-4"
                                >
                                    {{ this.tableData.GLOBAL }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.GLOBAL < 0.5 &&
                                            this.tableData.GLOBAL >= 0.3
                                    "
                                    class="yellow"
                                >
                                    {{ this.tableData.GLOBAL }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.GLOBAL < 0.3 &&
                                            this.tableData.GLOBAL >= 0.15
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.tableData.GLOBAL }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.GLOBAL != null &&
                                            this.tableData.GLOBAL < 0.15
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.tableData.GLOBAL }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Situacion === null
                                    "
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Situacion ==
                                            'Normalidad'
                                    "
                                    class="light-green accent-4"
                                >
                                    {{ this.$t("droughtIndices.normality") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Situacion ==
                                            'Prealerta'
                                    "
                                    class="yellow"
                                >
                                    {{ this.$t("droughtIndices.preAlert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Situacion ==
                                            'Alerta'
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.$t("droughtIndices.alert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Situacion ==
                                            'Emergencia'
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.$t("droughtIndices.emergency") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Escenario === null
                                    "
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Escenario ==
                                            'Normalidad'
                                    "
                                    class="light-green accent-4"
                                >
                                    {{ this.$t("droughtIndices.normality") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Escenario ==
                                            'Prealerta'
                                    "
                                    class="yellow"
                                >
                                    {{ this.$t("droughtIndices.preAlert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Escenario ==
                                            'Alerta'
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.$t("droughtIndices.alert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Escenario ==
                                            'Emergencia'
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.$t("droughtIndices.emergency") }}
                                </td>
                            </tr>
                            <tr>
                                <td>UTE II Cabecera</td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Cabecera === null
                                    "
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="this.tableData.UTE_II_Cabecera >= 0.5"
                                    class="light-green accent-4"
                                >
                                    {{ this.tableData.UTE_II_Cabecera }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Cabecera < 0.5 &&
                                            this.tableData.UTE_II_Cabecera >=
                                                0.3
                                    "
                                    class="yellow"
                                >
                                    {{ this.tableData.UTE_II_Cabecera }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Cabecera < 0.3 &&
                                            this.tableData.UTE_II_Cabecera >=
                                                0.15
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.tableData.UTE_II_Cabecera }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Cabecera !=
                                            null &&
                                            this.tableData.UTE_II_Cabecera <
                                                0.15
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.tableData.UTE_II_Cabecera }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Situacion === null
                                    "
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Situacion ==
                                            'Normalidad'
                                    "
                                    class="light-green accent-4"
                                >
                                    {{ this.$t("droughtIndices.normality") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Situacion ==
                                            'Prealerta'
                                    "
                                    class="yellow"
                                >
                                    {{ this.$t("droughtIndices.preAlert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Situacion ==
                                            'Alerta'
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.$t("droughtIndices.alert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Situacion ==
                                            'Emergencia'
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.$t("droughtIndices.emergency") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Escenario === null
                                    "
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Escenario ==
                                            'Normalidad'
                                    "
                                    class="light-green accent-4"
                                >
                                    {{ this.$t("droughtIndices.normality") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Escenario ==
                                            'Prealerta'
                                    "
                                    class="yellow"
                                >
                                    {{ this.$t("droughtIndices.preAlert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Escenario ==
                                            'Alerta'
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.$t("droughtIndices.alert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_II_Escenario ==
                                            'Emergencia'
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.$t("droughtIndices.emergency") }}
                                </td>
                            </tr>
                            <tr>
                                <td>UTE III Ríos MI</td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_RiosMI === null
                                    "
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="this.tableData.UTE_III_RiosMI >= 0.5"
                                    class="light-green accent-4"
                                >
                                    {{ this.tableData.UTE_III_RiosMI }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_RiosMI < 0.5 &&
                                            this.tableData.UTE_III_RiosMI >= 0.3
                                    "
                                    class="yellow"
                                >
                                    {{ this.tableData.UTE_III_RiosMI }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_RiosMI < 0.3 &&
                                            this.tableData.UTE_III_RiosMI >=
                                                0.15
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.tableData.UTE_III_RiosMI }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_RiosMI != null &&
                                            this.tableData.UTE_III_RiosMI < 0.15
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.tableData.UTE_III_RiosMI }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_Situacion ===
                                            null
                                    "
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_Situacion ==
                                            'Normalidad'
                                    "
                                    class="light-green accent-4"
                                >
                                    {{ this.$t("droughtIndices.normality") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_Situacion ==
                                            'Prealerta'
                                    "
                                    class="yellow"
                                >
                                    {{ this.$t("droughtIndices.preAlert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_Situacion ==
                                            'Alerta'
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.$t("droughtIndices.alert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_Situacion ==
                                            'Emergencia'
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.$t("droughtIndices.emergency") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_Escenario ===
                                            null
                                    "
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_Escenario ==
                                            'Normalidad'
                                    "
                                    class="light-green accent-4"
                                >
                                    {{ this.$t("droughtIndices.normality") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_Escenario ==
                                            'Prealerta'
                                    "
                                    class="yellow"
                                >
                                    {{ this.$t("droughtIndices.preAlert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_Escenario ==
                                            'Alerta'
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.$t("droughtIndices.alert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_III_Escenario ==
                                            'Emergencia'
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.$t("droughtIndices.emergency") }}
                                </td>
                            </tr>
                            <tr>
                                <td>UTE IV Ríos MD</td>
                                <td
                                    v-if="this.tableData.UTE_IV_RiosMD === null"
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="this.tableData.UTE_IV_RiosMD >= 0.5"
                                    class="light-green accent-4"
                                >
                                    {{ this.tableData.UTE_IV_RiosMD }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_RiosMD < 0.5 &&
                                            this.tableData.UTE_IV_RiosMD >= 0.3
                                    "
                                    class="yellow"
                                >
                                    {{ this.tableData.UTE_IV_RiosMD }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_RiosMD < 0.3 &&
                                            this.tableData.UTE_IV_RiosMD >= 0.15
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.tableData.UTE_IV_RiosMD }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_RiosMD != null &&
                                            this.tableData.UTE_IV_RiosMD < 0.15
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.tableData.UTE_IV_RiosMD }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_Situacion === null
                                    "
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_Situacion ==
                                            'Normalidad'
                                    "
                                    class="light-green accent-4"
                                >
                                    {{ this.$t("droughtIndices.normality") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_Situacion ==
                                            'Prealerta'
                                    "
                                    class="yellow"
                                >
                                    {{ this.$t("droughtIndices.preAlert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_Situacion ==
                                            'Alerta'
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.$t("droughtIndices.alert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_Situacion ==
                                            'Emergencia'
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.$t("droughtIndices.emergency") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_Escenario === null
                                    "
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_Escenario ==
                                            'Normalidad'
                                    "
                                    class="light-green accent-4"
                                >
                                    {{ this.$t("droughtIndices.normality") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_Escenario ==
                                            'Prealerta'
                                    "
                                    class="yellow"
                                >
                                    {{ this.$t("droughtIndices.preAlert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_Escenario ==
                                            'Alerta'
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.$t("droughtIndices.alert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_IV_Escenario ==
                                            'Emergencia'
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.$t("droughtIndices.emergency") }}
                                </td>
                            </tr>
                            <tr class="font-weight-bold">
                                <td>GLOBAL</td>
                                <td
                                    v-if="this.tableData.GLOBAL >= 0.5"
                                    class="light-green accent-4 "
                                >
                                    {{ this.tableData.GLOBAL }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.GLOBAL < 0.5 &&
                                            this.tableData.GLOBAL >= 0.3
                                    "
                                    class="yellow"
                                >
                                    {{ this.tableData.GLOBAL }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.GLOBAL < 0.3 &&
                                            this.tableData.GLOBAL >= 0.15
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.tableData.GLOBAL }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.GLOBAL != null &&
                                            this.tableData.GLOBAL < 0.15
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.tableData.GLOBAL }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Situacion === null
                                    "
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Situacion ==
                                            'Normalidad'
                                    "
                                    class="light-green accent-4"
                                >
                                    {{ this.$t("droughtIndices.normality") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Situacion ==
                                            'Prealerta'
                                    "
                                    class="yellow"
                                >
                                    {{ this.$t("droughtIndices.preAlert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Situacion ==
                                            'Alerta'
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.$t("droughtIndices.alert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Situacion ==
                                            'Emergencia'
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.$t("droughtIndices.emergency") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Escenario === null
                                    "
                                >
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Escenario ==
                                            'Normalidad'
                                    "
                                    class="light-green accent-4"
                                >
                                    {{ this.$t("droughtIndices.normality") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Escenario ==
                                            'Prealerta'
                                    "
                                    class="yellow"
                                >
                                    {{ this.$t("droughtIndices.preAlert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Escenario ==
                                            'Alerta'
                                    "
                                    class="orange lighten-1"
                                >
                                    {{ this.$t("droughtIndices.alert") }}
                                </td>
                                <td
                                    v-if="
                                        this.tableData.UTE_I_Escenario ==
                                            'Emergencia'
                                    "
                                    class="red darken-1"
                                >
                                    {{ this.$t("droughtIndices.emergency") }}
                                </td>
                            </tr>
                        </tbody>
                    </v-simple-table>
                </v-card>
            </v-col>
            <v-col v-if="state == states[1]" xs="12" sm="10" md="8">
                <v-card>
                    <v-card-title>{{ this.state }}</v-card-title>
                    <v-simple-table>
                        <thead>
                            <tr>
                                <th>
                                    {{
                                        this.$t(
                                            "droughtIndices.territorialUnit"
                                        )
                                    }}
                                </th>
                                <th>{{ this.$t("droughtIndices.index") }}</th>
                                <th>
                                    {{ this.$t("droughtIndices.situation") }}
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <th>SEGURA</th>
                                <th></th>
                                <th></th>
                            </tr>
                        </tbody>
                        <tbody>
                            <tr
                                v-if="
                                    this.tableData.UTS_I_Principal_Situacion ===
                                        null
                                "
                            >
                                <td>UTS I Principal</td>
                                <td>{{ this.tableData.UTS_I_Principal }}</td>
                                <td>
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.UTS_I_Principal_Situacion ==
                                        'Sequía prolongada'
                                "
                                class="orange lighten-4"
                            >
                                <td>UTS I Principal</td>
                                <td>{{ this.tableData.UTS_I_Principal }}</td>
                                <td>
                                    {{
                                        this.$t(
                                            "droughtIndices.prolongedDrought"
                                        )
                                    }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.UTS_I_Principal_Situacion ==
                                        'Ausencia de sequía prolongada'
                                "
                                class="light-blue lighten-4"
                            >
                                <td>UTS I Principal</td>
                                <td>{{ this.tableData.UTS_I_Principal }}</td>
                                <td>
                                    {{
                                        this.$t(
                                            "droughtIndices.noProlongedDrought"
                                        )
                                    }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.UTS_II_Cabecera_Situacion ===
                                        null
                                "
                            >
                                <td>UTS II Cabecera</td>
                                <td>{{ this.tableData.UTE_II_Cabecera }}</td>
                                <td>
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.UTS_II_Cabecera_Situacion ==
                                        'Sequía prolongada'
                                "
                                class="orange lighten-4"
                            >
                                <td>UTS II Cabecera</td>
                                <td>{{ this.tableData.UTE_II_Cabecera }}</td>
                                <td>
                                    {{
                                        this.$t(
                                            "droughtIndices.prolongedDrought"
                                        )
                                    }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.UTS_II_Cabecera_Situacion ==
                                        'Ausencia de sequía prolongada'
                                "
                                class="light-blue lighten-4"
                            >
                                <td>UTS II Cabecera</td>
                                <td>{{ this.tableData.UTE_II_Cabecera }}</td>
                                <td>
                                    {{
                                        this.$t(
                                            "droughtIndices.noProlongedDrought"
                                        )
                                    }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.UTS_III_RiosMI_Situacion ===
                                        null
                                "
                            >
                                <td>UTS III Ríos MI</td>
                                <td>{{ this.tableData.UTE_III_RiosMI }}</td>
                                <td>
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.UTS_III_RiosMI_Situacion ==
                                        'Sequía prolongada'
                                "
                                class="orange lighten-4"
                            >
                                <td>UTS III Ríos MI</td>
                                <td>{{ this.tableData.UTE_III_RiosMI }}</td>
                                <td>
                                    {{
                                        this.$t(
                                            "droughtIndices.prolongedDrought"
                                        )
                                    }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.UTS_III_RiosMI_Situacion ==
                                        'Ausencia de sequía prolongada'
                                "
                                class="light-blue lighten-4"
                            >
                                <td>UTS III Ríos MI</td>
                                <td>{{ this.tableData.UTE_III_RiosMI }}</td>
                                <td>
                                    {{
                                        this.$t(
                                            "droughtIndices.noProlongedDrought"
                                        )
                                    }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.UTS_IV_RiosMD_Situacion ===
                                        null
                                "
                            >
                                <td>UTS IV Ríos MD</td>
                                <td>{{ this.tableData.UTE_IV_RiosMD }}</td>
                                <td>
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.UTS_IV_RiosMD_Situacion ==
                                        'Sequía prolongada'
                                "
                                class="orange lighten-4"
                            >
                                <td>UTS IV Ríos MD</td>
                                <td>{{ this.tableData.UTE_IV_RiosMD }}</td>
                                <td>
                                    {{
                                        this.$t(
                                            "droughtIndices.prolongedDrought"
                                        )
                                    }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.UTS_IV_RiosMD_Situacion ==
                                        'Ausencia de sequía prolongada'
                                "
                                class="light-blue lighten-4"
                            >
                                <td>UTS IV Ríos MD</td>
                                <td>{{ this.tableData.UTE_IV_RiosMD }}</td>
                                <td>
                                    {{
                                        this.$t(
                                            "droughtIndices.noProlongedDrought"
                                        )
                                    }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData
                                        .UTS_Global_Segura_Situacion === null
                                "
                            >
                                <td>GLOBAL SEGURA</td>
                                <td>{{ this.tableData.UTS_GlobalSegura }}</td>
                                <td>
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData
                                        .UTS_Global_Segura_Situacion ==
                                        'Sequía prolongada'
                                "
                                class="orange lighten-4 font-weight-bold"
                            >
                                <td>GLOBAL SEGURA</td>
                                <td>{{ this.tableData.UTS_GlobalSegura }}</td>
                                <td>
                                    {{
                                        this.$t(
                                            "droughtIndices.prolongedDrought"
                                        )
                                    }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData
                                        .UTS_Global_Segura_Situacion ==
                                        'Ausencia de sequía prolongada'
                                "
                                class="light-blue lighten-4 font-weight-bold"
                            >
                                <td>GLOBAL SEGURA</td>
                                <td>{{ this.tableData.UTS_GlobalSegura }}</td>
                                <td>
                                    {{
                                        this.$t(
                                            "droughtIndices.noProlongedDrought"
                                        )
                                    }}
                                </td>
                            </tr>
                            <tr>
                                <th>ALTO TAJO</th>
                                <th></th>
                                <th></th>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.Alto_Tajo_Situacion === null
                                "
                            >
                                <td>ALTO TAJO</td>
                                <td>{{ this.tableData.Alto_Tajo }}</td>
                                <td>
                                    {{ this.$t("droughtIndices.noData") }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.Alto_Tajo_Situacion ==
                                        'Sequía prolongada'
                                "
                                class="orange lighten-4 font-weight-bold"
                            >
                                <td>ALTO TAJO</td>
                                <td>{{ this.tableData.Alto_Tajo }}</td>
                                <td>
                                    {{
                                        this.$t(
                                            "droughtIndices.prolongedDrought"
                                        )
                                    }}
                                </td>
                            </tr>
                            <tr
                                v-if="
                                    this.tableData.Alto_Tajo_Situacion ==
                                        'Ausencia de sequía prolongada'
                                "
                                class="light-blue lighten-4 font-weight-bold"
                            >
                                <td>ALTO TAJO</td>
                                <td>{{ this.tableData.Alto_Tajo }}</td>
                                <td>
                                    {{
                                        this.$t(
                                            "droughtIndices.noProlongedDrought"
                                        )
                                    }}
                                </td>
                            </tr>
                        </tbody>
                    </v-simple-table>
                </v-card>
            </v-col>
        </v-row>
    </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { mapMutations } from "vuex";

import { DroughtIndicesResponse } from "@/interfaces";
import * as types from "@/store/types";

@Component({
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    },
    components: {
        CalendarInput: () => import("@/components/layout/CalendarInput.vue")
    }
})
export default class ConjuncturalShortageTable extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    tableData = {};
    month = "2022-10";
    formattedMonth = "";
    states = [
        this.$t("droughtIndices.conjuncturalShortage"),
        this.$t("droughtIndices.prolongedDrought")
    ];

    state = this.states[0];

    //get actual month
    actualMonth() {
        const date = new Date();
        const year = date.getFullYear();
        const month = date.getMonth();
        this.month = `${year}-${month < 10 ? "0" + month : month}`;
    }

    mounted() {
        this.actualMonth();
        this.formatMonth();
    }

    formatMonth() {
        this.formattedMonth = this.month + "-01";
    }

    async fetchDroughtIndices() {
        try {
            this.setProgressBar(true);
            const allData = {
                type: "day",
                date: [this.formattedMonth]
            };

            const droughtIndices = await this.$api.getDroughtIndices<
                DroughtIndicesResponse
            >(allData);

            if (droughtIndices.ok) {
                this.tableData = droughtIndices.data[0];
            }
        } catch (error) {
            this.setInfoMessage({
                shown: true,
                text: this.$t("droughtIndices.noData").toString()
            });
        } finally {
            this.setProgressBar(false);
        }
    }

    /**
     * Show error message
     * @param {string} error Error message
     * @return {void}
     */
    showError(error: string): void {
        this.setInfoMessage({ shown: true, text: error });
    }
}
</script>
<style lang="scss" scoped>
tr:nth-child(even) {
    filter: brightness(97%);
}

tr:hover {
    filter: brightness(95%);
}

thead {
    tr {
        background-color: #e9e9e9;
    }
}
</style>
