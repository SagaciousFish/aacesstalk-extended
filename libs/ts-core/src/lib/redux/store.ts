import authReducer from './reducers/auth'
import sessionReducer from './reducers/session'
import { Action, Reducer, Store, ThunkAction, ThunkDispatch, combineReducers, configureStore } from '@reduxjs/toolkit';

export type CoreState = {
  auth: ReturnType<typeof authReducer>,
  session: ReturnType<typeof sessionReducer>
}

export type CoreAction = Action<string>;

export type CoreThunk<ReturnType = void, State = CoreState, A extends Action = CoreAction> = ThunkAction<
  ReturnType,
  State,
  unknown,
  A
>;


export type AdditionalReducers = {
  [key:string]: Reducer<any, Action>
}

export type RootState<Additional extends AdditionalReducers = {}> = CoreState & {
  [K in keyof Additional]: ReturnType<Additional[K]>
}

export function createStore<Additional extends AdditionalReducers, A extends Action = CoreAction>(additionalReducers?: Additional): Store<RootState<Additional>, A> & {dispatch: ThunkDispatch<RootState<Additional>, unknown, A>} {
  const rootReducer = combineReducers({
    auth: authReducer,
    session: sessionReducer,
    ...additionalReducers
  } as any) as any
  
  return configureStore({
    reducer: rootReducer
  })
}
