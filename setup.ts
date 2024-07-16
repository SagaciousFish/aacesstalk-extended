import inquirer, { Question, QuestionCollection } from 'inquirer'
import fs from 'fs-extra'
import dotenv from 'dotenv'
import path from 'path'
import axios from 'axios'

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


    // Handle loading image

    const loadingImageDirPath = path.resolve(process.cwd(), "apps/client-rn/src/assets/images/loading")
    const loadingImageCodePath = path.resolve(process.cwd(), "apps/client-rn/src/components/loading-images.js")
    const loadingImageCodeSamplePath = path.resolve(process.cwd(), "apps/client-rn/src/components/loading-images.sample.js")
    if(fs.existsSync(loadingImageCodePath) == false){
        const loadingImagesGoogleDriveId: string | undefined = (await inquirer.prompt({
            type: 'input',
            name: "gdrive",
            message: 'Insert Google drive ID to initialize loading image:'
        }))['gdrive']
        if(loadingImagesGoogleDriveId != null && loadingImagesGoogleDriveId.length > 0){
            const initialUrl = `https://drive.google.com/uc?export=download&id=${loadingImagesGoogleDriveId}`;
            const response = await axios.get(initialUrl, { responseType: 'stream' });
            const zipFileDownloadPath = path.resolve(process.cwd(), ".temp.loading-images.zip")
            const writer = fs.createWriteStream(zipFileDownloadPath);
            response.data.pipe(writer);
            writer.on('finish', () => {
                console.log('Download complete');
                const unzipper = require('unzipper');
                fs.createReadStream(zipFileDownloadPath).pipe(unzipper.Extract({ path: loadingImageDirPath }))
                    .on('close', () => {
                        console.log('Unzipping complete');
                        fs.rmSync(zipFileDownloadPath)
                        const filenames = fs.readdirSync(loadingImageDirPath).filter(name => name.endsWith(".gif") || name.endsWith(".png")  || name.endsWith(".jpg"))
                        console.log(filenames)
                        if(filenames.length > 0){
                            let jsFileContent = "module.exports=["

                            jsFileContent += filenames.map(name  => `\n\trequire('../assets/images/loading/${name}')`).join(",")

                            jsFileContent += "\n]"
                            console.log(jsFileContent)
                            fs.writeFileSync(loadingImageCodePath, jsFileContent)
                        }
                    });
                });
        }else{
            console.log("No Google Drive ID provided. set dummy code.")
            fs.copyFileSync(loadingImageCodeSamplePath, loadingImageCodePath)
        }
    }

}

setup().then()