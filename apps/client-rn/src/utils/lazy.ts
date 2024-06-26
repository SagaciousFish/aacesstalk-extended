export class Lazy<T>{
    
    private instance: T = null
    
    constructor(private readonly factory: ()=>T) {}

    get(): T{
        if(this.instance == null){
            this.instance = this.factory()
        }

        return this.instance!!
    }
}