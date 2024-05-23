import authReducer from './reducers/auth'
import sessionReducer from './reducers/session'
import { Action, ThunkAction } from '@reduxjs/toolkit';

export type CoreState = {
  auth: ReturnType<typeof authReducer>,
  session: ReturnType<typeof sessionReducer>
}

export type CoreThunk<ReturnType = void, State = CoreState> = ThunkAction<
  ReturnType,
  State,
  unknown,
  Action<string>
>;


export function createStore<>(additionalReducers?: {[key:string]: })
