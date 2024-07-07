import { useCallback, useState } from "react";
import { useSelector } from "../../redux/hooks";
import { Http } from "@aacesstalk/libs/ts-core";

export function useVerifyToken(): {verify: ()=>Promise<boolean>, isSignedIn: boolean | null} {
    const token = useSelector(state => state.auth.jwt)
    const [isSignedIn, setIsSignedIn] = useState<boolean|null>(null)

    const verify = useCallback(async ()=>{
        if(token != null){
            try{
                const resp = await Http.axios.get(Http.ENDPOINT_ADMIN_ACCOUNT_VERIFY, {
                    headers: await Http.getSignedInHeaders(token)
                })
                if(resp.status === 200){
                    setIsSignedIn(true)
                    return true
                }else return false
            }catch(ex){
                console.log(ex)
                setIsSignedIn(false)
                return false
            }
        }else{
            setIsSignedIn(false)
            return false
        }
    }, [token])

    return {
        verify, isSignedIn
    }
}