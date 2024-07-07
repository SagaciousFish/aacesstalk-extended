import { Navigate, Outlet, redirect } from "react-router-dom"
import { useVerifyToken } from "../hooks"
import { useCallback, useEffect } from "react"

export const SignedInRoute = () => {

    
    const { verify, isSignedIn } = useVerifyToken()

    useEffect(()=>{
        verify().then(isSignedIn => {
            if(!isSignedIn){
                console.log("Should redirect to login")
            }
        })
    }, [verify])

    if(isSignedIn === true){
        return <Outlet/>
    }else if(isSignedIn == null){
        return <div>Verifying user...</div>
    }else{
        return <Navigate to="/login"/>
    }
}