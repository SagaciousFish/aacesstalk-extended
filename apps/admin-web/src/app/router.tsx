import { Route, Routes, Link, redirect, Navigate } from 'react-router-dom';
import { Http, createAdminStore } from '@aacesstalk/libs/ts-core'

import { BrowserRouter } from 'react-router-dom';
import { SignInPage } from '../features/auth/pages/SignInPage';
import { DyadListPage } from '../features/dyads/pages/DyadListPage';
import { DyadDetailPage } from '../features/dyads/pages/DyadDetailPage';
import { useVerifyToken } from '../features/auth/hooks';
import { useCallback, useEffect } from 'react';
import { SignedInRoute } from '../features/auth/components/SignedInRoute';
import { DyadSessionsPage } from '../features/dyads/pages/DyadSessionsPage';
import { CustomCardsPage } from '../features/dyads/pages/CustomCardsPage';
import { FreeTopicSettingsPage } from '../features/dyads/pages/FreeTopicSettingsPage';

export const MainRouter = () => {

    return <BrowserRouter basename='/admin'>
    <Routes>
        <Route path="login" element={<SignInPage/>}/>
        <Route element={<SignedInRoute/>}>
            <Route index element={<Navigate to={"dyads"}/>}/>
            <Route path="dyads">
                <Route index element={<DyadListPage/>}/>
                <Route path=":id" element={<DyadDetailPage/>}>
                    <Route index element={<Navigate to={"sessions"}/>}/>
                    <Route path="sessions" element={<DyadSessionsPage/>}/>
                    <Route path="custom-cards" element={<CustomCardsPage/>}/>
                    <Route path="free-topics" element={<FreeTopicSettingsPage/>}/>
                </Route>
            </Route>
        </Route>
    </Routes>
</BrowserRouter>
}