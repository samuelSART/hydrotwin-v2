import { rest } from "msw";

const loadJsonData = async file => {
    return await import("./responses/" + file).then(module => module.default);
};

export default [
    // rest.post("*/api/corporate/get-piezometers", async (req, res, ctx) => {
    //     const data = await loadJsonData("piezometers.json");
    //     return res(ctx.json(data));
    // })
    // rest.post(
    //     "*/api/corporate/get-piezometers-values",
    //     async (req, res, ctx) => {
    //         const data = await loadJsonData("piezometers-values.json");
    //         return res(ctx.json(data));
    //     }
    // )
];
