import { NativeStackNavigationOptions, createNativeStackNavigator } from "@react-navigation/native-stack";
import { HomeScreen } from "../features/home/screens/HomeScreen";
import { SessionScreen } from "../features/session/screens/SessionScreen";
import { MainRoutes } from ".";
import { SessionMenuPopupScreen } from "../features/session/screens/SessionMenuPopupScreen";

const screenOptions = {headerShown: false}

const sharedScreenOptions: NativeStackNavigationOptions = {statusBarHidden: true}

const sessionScreenOptions: NativeStackNavigationOptions = {...sharedScreenOptions, animation: 'fade'}
const sessionMenuScreenOptions: NativeStackNavigationOptions = {...sharedScreenOptions, presentation: 'transparentModal', animation: 'fade'}

const Stack = createNativeStackNavigator<MainRoutes.MainNavigatorParamList>()

export const MainNavigator = () => {
    return <Stack.Navigator screenOptions={screenOptions} initialRouteName={MainRoutes.ROUTE_HOME}>
        <Stack.Screen name={MainRoutes.ROUTE_HOME} component={HomeScreen} options={sharedScreenOptions}/>
        <Stack.Screen name={MainRoutes.ROUTE_SESSION} component={SessionScreen} options={sessionScreenOptions}/>
        <Stack.Screen name={MainRoutes.ROUTE_SESSION_MENU} component={SessionMenuPopupScreen} options={sessionMenuScreenOptions}/>
    </Stack.Navigator>
}