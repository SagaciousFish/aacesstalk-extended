import { createStore, AdditionalReducers } from "@aacesstalk/libs/ts-core"
import { Store } from "@reduxjs/toolkit";

export interface ClientReducers extends AdditionalReducers {

}

const store = createStore({})

export {store}

export type ClientAppState = ReturnType<typeof store.getState>
export type ClientDispatch = typeof store.dispatch