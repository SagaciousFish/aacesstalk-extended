import authReducer from './reducers/auth'
import sessionReducer from './reducers/session'
import { Action, Reducer, Store, ThunkAction, combineReducers, configureStore } from '@reduxjs/toolkit';

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


export type AdditionalReducers = {
  [key:string]: Reducer<any, Action>
}

export type RootState<Additional extends AdditionalReducers = {}> = CoreState & {
  [K in keyof Additional]: ReturnType<Additional[K]>
}

export function createStore<Additional extends AdditionalReducers>(additionalReducers?: Additional): Store<RootState<Additional>> {
  const rootReducer = combineReducers({
    auth: authReducer,
    session: sessionReducer,
    ...additionalReducers
  } as any) as any
  
  return configureStore({
    reducer: rootReducer
  })
}
