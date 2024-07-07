import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { CoreThunk } from '../../store';
import { Http } from '../../../net/http';
import { jwtDecode } from "jwt-decode";
import { AxiosError } from 'axios';
import { AACessTalkErrors } from '../../../errors';

export interface AdminAuthState {
    isAuthorizing: boolean;
    jwt?: string;
    error?: string;
}

const INITIAL_STATE: AdminAuthState = {
    isAuthorizing: false,
    jwt: undefined,
    error: undefined
};

const authSlice = createSlice({
    name: 'auth',
    initialState: INITIAL_STATE,
    reducers: {
        initialize: () => {
            return { ...INITIAL_STATE };
        },

        _authorizingFlagOn: (state) => {
            state.isAuthorizing = true;
            state.jwt = undefined;
        },

        _authorizingFlagOff: (state) => {
            state.isAuthorizing = false;
        },

        _setError: (state, action: PayloadAction<string>) => {
            state.error = action.payload;
        },

        _setSignedInUser: (state, action: PayloadAction<{ token: string }>) => {
            state.isAuthorizing = false;
            state.jwt = action.payload.token;
            state.error = undefined;
        },
    }
});

export function loginAdminThunk(password: string): CoreThunk {
    return async (dispatch, getState) => {
        dispatch(authSlice.actions._authorizingFlagOn());

        try {
            const tokenResponse = await Http.axios.post(Http.ENDPOINT_ADMIN_ACCOUNT_LOGIN,
                { password }, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const { jwt } = tokenResponse.data

            const decoded = jwtDecode<{
                sub: string,
                iat: number,
                exp: number
            }>(jwt)

            console.log("Signed in with admin id", decoded.sub)

            dispatch(authSlice.actions._setSignedInUser({
                token: jwt
            }))

        } catch (ex) {
            let error = AACessTalkErrors.UnknownError
            if (ex instanceof AxiosError) {
                if (ex.code == AxiosError.ERR_NETWORK) {
                    error = AACessTalkErrors.ServerNotResponding
                } else if (ex.response?.status == 400) {
                    error = AACessTalkErrors.WrongCredential
                }
            }
            dispatch(authSlice.actions._setError(error))
        } finally {
            dispatch(authSlice.actions._authorizingFlagOff())
        }
    };
}

export function signOutAdminThunk(): CoreThunk {
    return async (dispatch, getState) => {
        dispatch(authSlice.actions.initialize())
    }
}

export default authSlice.reducer;
