export const mapConfig = {
    accessToken: process.env.VUE_APP_MAPBOX_TOKEN || "{{ MAPBOX_TOKEN }}",
    style: "mapbox://styles/mapbox/light-v10",
    environmentFlow: {
        colors: {
            negative: "#E05726",
            positive: "#0B6694",
            noData: "#454A4D"
        },
        timer: {
            timeout: 1000 * 60 * 10 // fetch variables last values every 10 min
        },
        dateReference: process.env.VUE_APP_ENV_FLOW_DATE_REF || null // Mon Jun 20 2022 09:55:00 GMT+0200 || null = current time
    },
    dam: {
        colors: {
            lessMin: "#facb5c",
            betweenMinMax: "#0388fc",
            greatherMax: "#e34f4f",
            noData: "#454A4D"
        },
        outlineColors: {
            lessMin: "#f5bd3b",
            betweenMinMax: "#0981eb",
            greatherMax: "#e33030",
            noData: "#454A4D"
        },
        timer: {
            timeout: 1000 * 60 * 10 // fetch variables last values every 10 min
        }
    },
    marmenor: {
        timer: {
            timeout: 1000 * 60 * 10 // fetch variables last values every 10 min
        }
    },
    co2: {
        colors: ["#7DF266", "#7ABD7E", "#F8D66D", "#F7AC40", "#FF6961"],
        outlineColors: ["#72D65E", "#68A36C", "#F0CF6C", "#E8A23C", "#E8625A"]
    },
    saica: {
        timer: {
            timeout: 1000 * 60 * 10 // fetch variables last values every 10 min
        }
    },
    hydroEconomic: {
        noDataColor: "#454A4D",
        noDataOutlineColor: "#454A4D",
        colors: ["#7DF266", "#7ABD7E", "#F8D66D", "#F7AC40", "#FF6961"],
        outlineColors: ["#72D65E", "#68A36C", "#F0CF6C", "#E8A23C", "#E8625A"]
    },
    rasterUDAStats: {
        noDataColor: "#454A4D",
        noDataOutlineColor: "#454A4D",
        outlineColor: "#454A4D"
    },
    waterMeter: {
        timer: {
            timeout: 1000 * 60 * 10 // fetch variables last values every 10 min
        }
    }
};
