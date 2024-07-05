import { createStore, CoreAction } from "@aacesstalk/libs/ts-core"
import { MMKVLoader } from "react-native-mmkv-storage";
import parentAudioRecordingReducer from "../features/audio/reducer";
import systemStatusReducer from '../features/system-status/reducer';
import { Action, ThunkAction } from "@reduxjs/toolkit";

const storage = new MMKVLoader().withEncryption().initialize();

const { store, persistor } = createStore(storage, {
    parentAudioRecording: parentAudioRecordingReducer,
    systemStatus: systemStatusReducer
})

export { store, persistor }

export type ClientAppState = ReturnType<typeof store.getState>
export type ClientDispatch = typeof store.dispatch

export type ClientThunk<ReturnType = void, State = ClientAppState, A extends Action = CoreAction> = ThunkAction<
ReturnType,
State,
unknown,
A
>;