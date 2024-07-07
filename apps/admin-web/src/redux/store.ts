import { createAdminStore, AdminCoreAction } from "@aacesstalk/libs/ts-core"
import { Action, ThunkAction } from "@reduxjs/toolkit";
import localStorage from 'redux-persist/es/storage';

const { store, persistor } = createAdminStore(localStorage)

export { store, persistor }

export type AdminReduxState = ReturnType<typeof store.getState>
export type AdminDispatch = typeof store.dispatch

export type AdminThunk<ReturnType = void, State = AdminReduxState, A extends Action = AdminCoreAction> = ThunkAction<
ReturnType,
State,
unknown,
A
>;