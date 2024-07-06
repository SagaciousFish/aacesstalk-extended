import { NativeStackNavigationOptions, createNativeStackNavigator } from "@react-navigation/native-stack";
import { HomeScreen } from "../features/home/screens/HomeScreen";
import { SessionScreen } from "../features/session/screens/SessionScreen";
import { MainRoutes } from ".";
import { SessionMenuPopupScreen } from "../features/session/screens/SessionMenuPopupScreen";
import { SessionClosingScreen } from "../features/session/screens/SessionClosingScreen";
import { StarListScreen } from "../features/home/screens/StarListScreen";
import { FreeTopicSelectionScreen } from "../features/home/screens/FreeTopicSelectionScreen";

const screenOptions = {headerShown: false, gestureEnabled: false}

const sharedScreenOptions: NativeStackNavigationOptions = {statusBarHidden: true, gestureEnabled: false}

const sessionScreenOptions: NativeStackNavigationOptions = {...sharedScreenOptions, animation: 'fade'}
const sessionClosingScreenOptions: NativeStackNavigationOptions = {...sharedScreenOptions, animation: 'none'}
const sessionMenuScreenOptions: NativeStackNavigationOptions = {...sharedScreenOptions, presentation: 'transparentModal', animation: 'fade'}

const Stack = createNativeStackNavigator<MainRoutes.MainNavigatorParamList>()

export const MainNavigator = () => {
    return <Stack.Navigator screenOptions={screenOptions} initialRouteName={MainRoutes.ROUTE_HOME}>
        <Stack.Screen name={MainRoutes.ROUTE_HOME} component={HomeScreen} options={sharedScreenOptions}/>
        <Stack.Screen name={MainRoutes.ROUTE_STAR_LIST} component={StarListScreen} options={sessionMenuScreenOptions}/>
        <Stack.Screen name={MainRoutes.ROUTE_SESSION} component={SessionScreen} options={sessionScreenOptions}/>
        <Stack.Screen name={MainRoutes.ROUTE_SESSION_CLOSING} component={SessionClosingScreen} options={sessionClosingScreenOptions}/>
        <Stack.Screen name={MainRoutes.ROUTE_SESSION_MENU} component={SessionMenuPopupScreen} options={sessionMenuScreenOptions}/>
        <Stack.Screen name={MainRoutes.ROUTE_FREE_TOPIC_SELECTION} component={FreeTopicSelectionScreen} options={sessionMenuScreenOptions}/>
    </Stack.Navigator>
}