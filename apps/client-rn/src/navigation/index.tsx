import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { HomeScreen } from "../features/home/screens/HomeScreen";

const screenOptions = {headerShown: false}

const Stack = createNativeStackNavigator()

export const HomeNavigator = () => {
    return <Stack.Navigator screenOptions={screenOptions}>
        <Stack.Screen name="home" component={HomeScreen}/>
    </Stack.Navigator>
}