import { createStore, AdditionalReducers } from "@aacesstalk/libs/ts-core"
import { Store } from "@reduxjs/toolkit";
import { MMKVLoader } from "react-native-mmkv-storage";

export interface ClientReducers extends AdditionalReducers {

}

const storage = new MMKVLoader().withEncryption().initialize();

const { store, persistor } = createStore(storage, {})

export { store, persistor }

export type ClientAppState = ReturnType<typeof store.getState>
export type ClientDispatch = typeof store.dispatch