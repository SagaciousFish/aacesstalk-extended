import {TypedUseSelectorHook, useDispatch as stockUseDispatch, useSelector as stockUseSelector} from "react-redux";
import {ClientDispatch, ClientAppState} from "./store";

export const useDispatch = stockUseDispatch<ClientDispatch>
export const useSelector: TypedUseSelectorHook<ClientAppState> = stockUseSelector