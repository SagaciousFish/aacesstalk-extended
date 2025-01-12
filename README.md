# AACessTalk: Tablet application for fostering communication between parents and minimally verbal autistic children

This repo is an artifact of research paper:

**AACessTalk: Fostering Communication between Minimally Verbal Autistic Children and Parents with Contextual Guidance and Card Recommendation**

Dasom Choi,
SoHyun Park,
Kyungah Lee,
Hwajung Hong,
and Young-Ho Kim

## Tech Stack
* **Workspace:** NX CI Monorepo (https://nx.dev/ci/intro/ci-with-nx)
* **Mobile client:** React Native (Written in TypeScript)
* **Backend:** FastAPI (Written in Python)
* **Intelligence:** OpenAI API


## Get Started
### Prerequisite
* Node >= 22 (Recommend using `nvm` https://github.com/nvm-sh/nvm)
* Install `NX` 
    ```sh
    > npm i nx -g nx
    ```
* Python ^= 3.11.8 (Recommend using `pyenv` https://github.com/pyenv/pyenv)
* Install `Poetry` (https://python-poetry.org/)
* In the repository root, install dependencies for further actions.
  ```sh
  > npm install
  > nx run backend:install
  ```
* Prepare API credentials in advance:
  * **OpenAI API Key** - used to run the AI pipelines.
  * **CLOVA Voice API** (https://api.ncloud-docs.com/docs/en/ai-naver-clovavoice) - used to generate voice-over for child cards.
    * `API key`
    * `Secret`
  * (Only for Korean) **CLOVA Speech Recognition API** (https://api.ncloud-docs.com/docs/en/ai-naver-clovaspeechrecognition) - Optional. Yields reliable performance in recognizing Korean. `OpenAI Whisper` will be used as a fallback.
    * `Invoke URL`
    * `Secret`
  * (Only for Korean) DeepL translation API (https://developers.deepl.com/docs)
    * `API key`

### Installation
1. Run frontend installation script
   ```sh
   > npm run setup-js
   ```

1. Run backend installation script
   ```sh
   > nx run backend:setup
   ```

### Running Backend server
* Development mode
   ```
   > nx run backend:run-dev
   ```
* Production mode (Uses Guicorn deamon https://gunicorn.org/)
  ```
  > nx run backend:run-prod
  ```

### Running Mobile Client (Tablet or Emulator)
* Android (Tested via user study)
  ```
  > nx run client-rn:run-android
  ```
* iOS (Not tested)
   ```
   > nx run client-rn:run-ios
   ```


## Code maintainer
Young-Ho Kim (Research scientist at NAVER AI Lab. http://younghokim.net)
