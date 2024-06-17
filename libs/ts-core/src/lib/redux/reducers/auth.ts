import { Dyad, ParentType } from '../../model-types';
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { CoreState, CoreThunk } from '../store';
import { Http } from '../../net/http';
import { jwtDecode } from "jwt-decode";
import { Axios, AxiosError } from 'axios';
import { AACessTalkErrors } from '../../errors';

export interface AuthState {
  isAuthorizing: boolean;
  jwt?: string;
  dyadInfo?: Dyad;
  error?: string;
}

const INITIAL_AUTH_STATE: AuthState = {
  isAuthorizing: false
};

const authSlice = createSlice({
  name: 'auth',
  initialState: INITIAL_AUTH_STATE,
  reducers: {
    initialize: () => {
      return { ...INITIAL_AUTH_STATE };
    },

    _authorizingFlagOn: (state) => {
      state.isAuthorizing = true;
      state.dyadInfo = undefined;
      state.jwt = undefined;
    },

    _authorizingFlagOff: (state) => {
      state.isAuthorizing = false;
    },

    _setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
    },

    _setSignedInUser: (state, action: PayloadAction<{ dyad: Dyad, token: string }>) => {
      state.isAuthorizing = false;
      state.dyadInfo = action.payload.dyad;
      state.jwt = action.payload.token;
      state.error = undefined;
    }
  }
});

export function loginDyadThunk(code: string): CoreThunk {
  return async (dispatch, getState) => {
    dispatch(authSlice.actions._authorizingFlagOn());

    try {
      const tokenResponse = await Http.axios.post(Http.ENDPOINT_DYAD_ACCOUNT_LOGIN,
        { code }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });

      const { jwt } = tokenResponse.data

      const decoded = jwtDecode<{
        sub: string,
        alias: string,
        child_name: string,
        parent_type: ParentType,
        iat: number,
        exp: number}>(jwt)


      dispatch(authSlice.actions._setSignedInUser({
        dyad: {
          id: decoded.sub,
          child_name: decoded.child_name,
          parent_type: decoded.parent_type,
          alias: decoded.alias
        },
        token: jwt
      }));

    } catch (ex) {
      let error = AACessTalkErrors.UnknownError 
      if(ex instanceof AxiosError){
        if(ex.code == AxiosError.ERR_NETWORK){
          error = AACessTalkErrors.ServerNotResponding
        }else if (ex.response?.status == 400){
          error = AACessTalkErrors.WrongCredential
        }
      }
      dispatch(authSlice.actions._setError(error))
    } finally {
      dispatch(authSlice.actions._authorizingFlagOff())
    }
  };
}

export function signOutDyadThunk(): CoreThunk {
  return async (dispatch, getState) => {
    dispatch(authSlice.actions.initialize())
  }
}


export default authSlice.reducer;
