import { createStore, CoreAction } from "@aacesstalk/libs/ts-core"
import { MMKV } from "react-native-mmkv";
import parentAudioRecordingReducer from "../features/audio/reducer";
import systemStatusReducer from '../features/system-status/reducer';
import { Action, ThunkAction } from "@reduxjs/toolkit";
import { Storage } from "redux-persist";

const storage = new MMKV()

export const reduxStorage: Storage = {
    setItem: (key, value) => {
      storage.set(key, value)
      return Promise.resolve(true)
    },
    getItem: (key) => {
      const value = storage.getString(key)
      return Promise.resolve(value)
    },
    removeItem: (key) => {
      storage.delete(key)
      return Promise.resolve()
    },
  }

const { store, persistor } = createStore(reduxStorage, {
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