import inquirer, { Question, QuestionCollection } from 'inquirer'
import fs from 'fs-extra'
import dotenv from 'dotenv'
import path from 'path'

const envPath = path.resolve(process.cwd(), ".env")

if(fs.existsSync(envPath) == false){
    fs.createFileSync(envPath)
}

async function setup(){

    const env = dotenv.config({path: envPath})

    const questions: Array<Question> = []

    if(env.parsed?.["BACKEND_ADDRESS"] == null){
        questions.push({
                type: 'input',
                name: 'hostname',
                message: 'Insert Backend hostname including port number (e.g., http://0.0.0.0:3000)',
                validate: (input: string) => {
                    if(input == null || input.trim().length == 0){
                        return "Please enter valid hostname."
                    }else{
                        return true
                    }
                }
            })
    }

    const newObj: {[key:string]:string} = env.parsed as any

    if(questions.length > 0){
        const answers = await inquirer.prompt(questions)
        newObj["BACKEND_ADDRESS"] = answers["hostname"]
    }

    for(const key of Object.keys(newObj)){
        if(key.startsWith("VITE_") == false){
            newObj[`VITE_${key}`] = newObj[key]
        }
    }

    const envFileContent = Object.entries(newObj)
        .map(([key, value]) => `${key}=${value}`)
        .join('\n');

    fs.writeFileSync(envPath, envFileContent, {encoding:'utf-8'})

    fs.copyFileSync(envPath, path.join(process.cwd(), "/apps/client-rn", ".env"))
    fs.copyFileSync(envPath, path.join(process.cwd(), "/apps/admin-web", ".env"))
}

setup().then()