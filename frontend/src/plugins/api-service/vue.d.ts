import Vue from "vue";
import { APIService } from "./api.service";

declare module "vue/types/vue" {
    interface Vue {
        $api: APIService;
    }

    interface VueConstructor {
        $api: APIService;
    }
}
