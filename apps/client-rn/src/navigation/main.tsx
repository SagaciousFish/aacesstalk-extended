import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { HomeScreen } from "../features/home/screens/HomeScreen";
import { SessionScreen } from "../features/session/screens/SessionScreen";
import { MainRoutes } from ".";

const screenOptions = {headerShown: false}

const Stack = createNativeStackNavigator<MainRoutes.MainNavigatorParamList>()

export const MainNavigator = () => {
    return <Stack.Navigator screenOptions={screenOptions} initialRouteName={MainRoutes.ROUTE_HOME}>
        <Stack.Screen name={MainRoutes.ROUTE_HOME} component={HomeScreen}/>
        <Stack.Screen name={MainRoutes.ROUTE_SESSION} component={SessionScreen}/>
    </Stack.Navigator>
}