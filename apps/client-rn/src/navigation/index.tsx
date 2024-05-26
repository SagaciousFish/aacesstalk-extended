import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { HomeScreen } from "../features/home/screens/HomeScreen";

const Stack = createNativeStackNavigator()

export const HomeNavigator = () => {
    return <Stack.Navigator>
        <Stack.Screen name="home" component={HomeScreen}/>
    </Stack.Navigator>
}