
export async function finishAfterMinimumDelay<T>(promise: Promise<T>, minDelay: number): Promise<T> {
    return new Promise(async (resolve, reject) => {
        const tStart = Date.now()

        const result = await promise
    
        const tEnd = Date.now()
    
        const leftTime = minDelay - (tEnd-tStart)
        console.log("Left time:", leftTime)
        if(leftTime>0){
            setTimeout(()=>{ resolve(result) }, leftTime)
        }else{
            return resolve(result)
        }
    })
}