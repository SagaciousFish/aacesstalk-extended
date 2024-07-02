export class Env{
    static readonly KEY_BACKEND_ADDRESS: string = "BACKEND_ADDRESS"

    private static _instance: Env | null = null

    static get instance(): Env {
        if(this._instance == null){
            this._instance = new Env()
        }

        return this._instance
    }

    private envVars: {[key: string] : string} = {}

    private constructor(){
        const obj = require('../env.json')
        console.log(obj)
        this.envVars = obj
    }

    public getVariable(key: string): string | undefined {
        return this.envVars[key]
    }
}