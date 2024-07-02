import { Http } from "@aacesstalk/libs/ts-core";
import NetInfo, {NetInfoConfiguration, NetInfoState, useNetInfo} from "@react-native-community/netinfo";

export const backendReachabilityConfiguration: Partial<NetInfoConfiguration> = {
    reachabilityUrl: Http.axios.defaults.baseURL + Http.ENDPOINT_PING,
    reachabilityTest: async (response) => response.status == 204,
    useNativeReachability: false
}

NetInfo.configure(backendReachabilityConfiguration)