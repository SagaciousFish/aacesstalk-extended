/* eslint-disable jsx-a11y/accessible-emoji */
import React, { useEffect, useRef, useState } from 'react';
import { Provider } from 'react-redux';
import { store, persistor } from '../redux/store';
import { Text, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { NativeStackNavigationOptions, createNativeStackNavigator } from '@react-navigation/native-stack';
import { SignInScreen } from '../features/auth/screens/SignInScreen';
import { useSelector } from '../redux/hooks';
import { MainNavigator } from '../navigation/main';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { PersistGate } from 'redux-persist/integration/react';
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { Http } from '@aacesstalk/libs/ts-core';
import { getTimeZone } from 'react-native-localize';
import { useKeepAwake } from '@sayem314/react-native-keep-awake';

const Stack = createNativeStackNavigator()

const screenOptions: NativeStackNavigationOptions = {
  headerShown: false,
}

const GlobalNavigator = () => {

  const isSignedIn = useSelector(state => {
    return state.auth.jwt != null
  })

  return <Stack.Navigator screenOptions={screenOptions}>
  {
    isSignedIn ? (<Stack.Screen name="Home" component={MainNavigator}/>) : 
    (<Stack.Screen name="Auth" component={SignInScreen}/>)
  }
</Stack.Navigator>
}

export const App = () => {

  useKeepAwake()

  useEffect(()=>{
    Http.initialize(async () => {return getTimeZone()})
  }, [])


  return <Provider store={store}>
    <PersistGate persistor={persistor}>
      <SafeAreaProvider>
        <GestureHandlerRootView className="flex-1">
        <NavigationContainer>
            <GlobalNavigator/>
        </NavigationContainer>
        </GestureHandlerRootView>
      </SafeAreaProvider>
    </PersistGate>
  </Provider>
};

export default App;
