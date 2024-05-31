import { SessionTopicInfo } from "@aacesstalk/libs/ts-core"

export namespace MainRoutes{
    export const ROUTE_HOME = "home"
    export const ROUTE_SESSION = "session"

    export type MainNavigatorParamList = {
        [ROUTE_HOME]: undefined,
        [ROUTE_SESSION]: {topic: SessionTopicInfo}
    }
}