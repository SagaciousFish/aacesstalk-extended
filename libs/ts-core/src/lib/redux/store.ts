import authReducer from './reducers/auth'
import sessionReducer from './reducers/session'
import dyadStatusReducer from './reducers/dyad-status'
import { Action, Reducer, Store, ThunkAction, ThunkDispatch, combineReducers, configureStore } from '@reduxjs/toolkit';
import {FLUSH, PAUSE, PERSIST, PURGE, Persistor, REGISTER, REHYDRATE, persistReducer, persistStore} from 'redux-persist'

export type CoreState = {
  auth: ReturnType<typeof authReducer>,
  session: ReturnType<typeof sessionReducer>,
  dyadStatus: ReturnType<typeof dyadStatusReducer>
}

export type CoreAction = Action<string>;

export type CoreThunk<ReturnType = void, State = CoreState, A extends Action = CoreAction> = ThunkAction<
  ReturnType,
  State,
  unknown,
  A
>;


type AdditionalReducers = {
  [key:string]: Reducer<any, Action>
}

export type RootState<Additional extends AdditionalReducers = {}> = CoreState & {
  [K in keyof Additional]: ReturnType<Additional[K]>
}

export function createStore<Additional extends AdditionalReducers, A extends Action = CoreAction>(
    persistStorage: any,
    additionalReducers?: Additional,
  ): {store: Store<RootState<Additional>, A> & {dispatch: ThunkDispatch<RootState<Additional>, unknown, A>}, persistor: Persistor} {
  const rootReducer = combineReducers({
    auth: persistReducer({
      key: 'root',
      storage: persistStorage,
      whitelist: ['jwt', 'dyadInfo', 'freeTopicDetailEntityState']
    }, authReducer),
    session: sessionReducer,
    dyadStatus: dyadStatusReducer,
    ...additionalReducers
  } as any) as any
  
  const store = configureStore({
    reducer: rootReducer,
    middleware: (getDefaultMiddleware) => getDefaultMiddleware({
      serializableCheck: {
          ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    })
  }) as any

  const persistor = persistStore(store)

  return {store, persistor}
}
