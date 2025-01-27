# AACessTalk: Tablet application for fostering communication between parents and minimally verbal autistic children

This is a monorepo of an artifact of research paper, "**AACessTalk: Fostering Communication between Minimally Verbal Autistic Children and Parents with Contextual Guidance and Card Recommendation**" at ACM CHI 2025.

Website: https://naver-ai.github.io/aacesstalk

<img src="https://github.com/naver-ai/aacesstalk-monorepo/blob/main/aacesstalk_demo_loop.gif"/>

## Tech Stack

* **Workspace:** NX CI Monorepo (https://nx.dev/ci/intro/ci-with-nx)
* **Mobile client:** React Native (Written in TypeScript)
* **Backend:** FastAPI (Written in Python)
* **Intelligence:** OpenAI API


## Get Started

### Prerequisite

* Node >= 22 (Recommend using `nvm` https://github.com/nvm-sh/nvm)

  ```sh
  > nvm instal --lts
  ```
* Install `NX`

  ```sh
  > npm i nx -g nx
  ```
* Python ^= 3.11.8 (Recommend using `pyenv` https://github.com/pyenv/pyenv)

  (Using Homebrew on MacOS)

  ```
  > brew install pyenv
  ... //set up script in shell configuration
  > pyenv install 3.11.8
  ```
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
2. Run backend installation script

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


## Cite AACessTalk

### ACM Citation

Dasom Choi, SoHyun Park, Kyungah Lee, Hwajung Hong, and Young-Ho Kim. 2025. AACessTalk: Fostering Communication between Minimally Verbal Autistic Children and Parents with Contextual Guidance and Card Recommendation. In CHI Conference on Human Factors in Computing Systems (CHI ’25), April 26-May 1, 2025, Yokohama, Japan. ACM, New York, NY, USA, 25 pages. <https://doi.org/10.1145/3706598.3713792>

### BibTex

```bibtex
  @inproceedings{choi2025aacesstalk,
    title={AACessTalk: Fostering Communication between Minimally Verbal Autistic Children and Parents with Contextual Guidance and Card Recommendation},
    author={Dasom Choi and SoHyun Park and Kyungah Lee and Hwajung Hong and Young-Ho Kim},
    year = {2025},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    url = {https://doi.org/10.1145/3706598.3713792},
    doi = {10.1145/3706598.3713792},
    booktitle = {Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems},
    location = {Yokohama, Japan},
    series = {CHI '25}
  }
```

## Research Team (In the order of paper authors)
* Dasom Choi (PhD Candidate at KAIST) https://dasomchoi.com/
* SoHyun Park (Researcher at NAVER Cloud)
* Kyungah Lee (Licensed Counselor at Dodakim Child Development Center)
* Hwajung Hong (Associate Professor at KAIST) https://hwajunghong.com
* Young-Ho Kim (Research Scientist at NAVER AI Lab) http://younghokim.net *Corresponding author

## Code maintainer

* Young-Ho Kim (Research Scientist at NAVER AI Lab) http://younghokim.net
