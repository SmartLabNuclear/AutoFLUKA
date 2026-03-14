# AutoFLUKA-MS
- AutoFLUKA is a locally deployable, domain-intelligent LLM agent framework that streamlines and automates Monte Carlo radiation workflows in FLUKA.
- It includes grounded document analysis to deliver accurate, context-aware assistance.
- All processing runs locally, so your documents, inputs, and simulation data remain in your environment.

## Highlights
- AutoFLUKA broadly impacts engineering, energy, nuclear science, and medical physics.
- AutoFLUKA is an AI-driven tool that automates complex Monte Carlo workflows, integrating seamlessly with FLUKA.
- It reduces human intervention and minimizes errors by automating input generation, simulation execution, and post-processing.
- A GUI improves accessibility and shortens the learning curve.
- AutoFLUKA introduces JSON-based data outputs, enabling easier downstream analysis compared to traditional manual approaches.
- The framework includes a Retrieval Augmented Generation (RAG) assistant, helping users address common FLUKA challenges by providing quick, context-specific guidance.

The original paper can be found [here](https://www.sciencedirect.com/science/article/pii/S2666546825000874)


---

## Quick Start: Run with Docker

### Prerequisites: API Keys

You will need the following API keys:

- Get OpenAI API key [here](https://platform.openai.com/api-keys) OR Gemini API key (free API for `gemini-1.5`) [here](https://aistudio.google.com/app/apikey) 
- LangChain (LangSmith) API key (optional, for tracing/logs) [here](https://www.langchain.com/langsmith) 
- Google Custom Search API key [here](https://developers.google.com/custom-search/v1/introduction) 
- Google Custom Search Engine ID [here](https://programmablesearchengine.google.com/controlpanel/overview?cx=f69ad3c244dca4170)
- HF_API_KEY (required for document parsing / RAG) [here](https://huggingface.co/settings/tokens)

### Pull the Docker Image (No `.tar` Needed)

No need to download a tarball or submit a form. Pull AutoFLUKA directly from Docker Hub.

1) Install Docker Desktop (Windows/macOS) or Docker Engine (Linux) [here](https://www.docker.com/products/docker-desktop)

2) Pull image from Docker Hub (public):
```
docker pull zev94/autofluka-2.0:2.0
```

### .env Configuration

3) Create a `.env` file in your run directory and set required API keys/secrets.
   A key-only template is provided at `AutoFLUKA-2.0/fluka_skills/.env.example` (copy and fill values).

Your `.env` file must have the following keys (see the links above). 
**No space between the `=` and your key values**
- OPENAI_API_KEY=<your_key_value>
- GEMINI_API_KEY=<your_key_value>
- LANGCHAIN_API_KEY=<your_key_value>
- CUSTOM_SEARCH_ENGINE_API_KEY=<your_key_value>
- CUSTOM_SEARCH_ENGINE_ID=<your_key_value>
- HF_API_KEY=<your_key_value>

4) Prepare local folders:
- Download `fluka_skills` folder (from this repository: `AutoFLUKA-2.0/fluka_skills`)
- `AutoFLUKA_logs` (runtime logs)
- your simulation work directory (mounted to `/host`)

---

## Installation & Run (Windows PowerShell, WSL, and Linux)

Use image:
- `zev94/autofluka-2.0:2.0` fixed version (recommended )
- `zev94/autofluka-2.0:latest` (rolling tag). Updates will be added to this version 

### 1) Navigate to your run directory

Windows PowerShell:
```
cd C:\path\to\run-directory
```

WSL / Linux:
```
cd /path/to/run-directory
```

Your run directory should contain:
- `.env`
- `fluka_skills/`
- `AutoFLUKA_logs/` (can be empty)

### 2A) Run WITH FLUKA (full simulation mode)

- Use this mode if you want AutoFLUKA to execute FLUKA jobs and decrypt results. 
- You must mount a Linux FLUKA installation and provide `FLUKADATA` and `RFLUKA_BIN`.
- **IMPORTANT**. **AutoFLUKA Does NOT have a Pre-build FLUKA package installed**. Users wanting to use this mode must install FLUKA from the official [website](https://fluka.cern/documentation/installation). 

Windows PowerShell:
```
docker run -d --name autofluka-app `
  -p 8050:8000 `
  --env-file ".env" `
  -e FLUKADATA=/usr/local/fluka/data `
  -e RFLUKA_BIN=/usr/local/fluka/bin/rfluka `
  -v "\\wsl$\Ubuntu\usr\local\fluka:/usr/local/fluka:ro" `
  -v "${PWD}\fluka_skills:/autofluka/fluka_skills" `
  -v "${PWD}\AutoFLUKA_logs:/autofluka/AutoFLUKA_logs" `
  -v "C:\path\to\your\simulation-data:/host" `
  zev94/autofluka-2.0:2.0
```

WSL / Linux:
```
docker run -d --name autofluka-app \
  -p 8050:8000 \
  --env-file .env \
  -e FLUKADATA=/usr/local/fluka/data \
  -e RFLUKA_BIN=/usr/local/fluka/bin/rfluka \
  -v /usr/local/fluka:/usr/local/fluka:ro \
  -v "$PWD/fluka_skills:/autofluka/fluka_skills" \
  -v "$PWD/AutoFLUKA_logs:/autofluka/AutoFLUKA_logs" \
  -v "/mnt/c/path/to/your/simulation-data:/host" \
  zev94/autofluka-2.0:2.0
```

### 2B) Run WITHOUT FLUKA (chatbot/RAG mode)

Use this mode if you only need AI chat, document-grounded Q&A, and input authoring/editing support.
No FLUKA installation mount is required.

Windows PowerShell:
```
docker run -d --name autofluka-app `
  -p 8050:8000 `
  --env-file ".env" `
  -v "${PWD}\fluka_skills:/autofluka/fluka_skills" `
  -v "${PWD}\AutoFLUKA_logs:/autofluka/AutoFLUKA_logs" `
  -v "C:\path\to\your\working-directory:/host" `
  zev94/autofluka-2.0:2.0
```

WSL / Linux:
```
docker run -d --name autofluka-app \
  -p 8050:8000 \
  --env-file .env \
  -v "$PWD/fluka_skills:/autofluka/fluka_skills" \
  -v "$PWD/AutoFLUKA_logs:/autofluka/AutoFLUKA_logs" \
  -v "/mnt/c/path/to/your/working-directory:/host" \
  zev94/autofluka-2.0:2.0
```

### 3) Verify and open UI

Check container:
```
docker ps
docker logs -f autofluka-app
```

Open UI:
```
http://localhost:8050
```

### 4) Stop / remove

```
docker stop autofluka-app
docker rm autofluka-app
```

---
## Troubleshooting

- **pull access denied / repository does not exist**  
  Run `docker load -i ./autofluka-1.0.0-alpha2.tar` again and use the name/tag Docker prints.

- **invalid reference format**  
  Line continuations or quoting are wrong. In PowerShell use backticks ` `` `, in WSL/Linux use `\`. Quote paths with spaces.

- **Jobs start but terminate instantly; no `_fort.xx` files**  
  FLUKA not mounted or wrong binary path. Mount entire `/usr/local/fluka` and set `RFLUKA_BIN` and `FLUKADATA`.

- **Exec format error**  
  You mounted a Windows FLUKA binary. The container needs the Linux build.

- **Cannot access WSL paths from PowerShell**  
  Use UNC paths like `\\wsl$\Ubuntu\usr\local\fluka` and enable WSL integration in Docker Desktop.

---

## Citation

BibTeX:
```
@article{ndum2025automating,
  title={Automating Monte Carlo simulations in nuclear engineering with domain knowledge-embedded large language model agents},
  author={Ndum, Zavier Ndum and Tao, Jian and Ford, John and Liu, Yang},
  journal={Energy and AI},
  pages={100555},
  year={2025},
  publisher={Elsevier}
}
```







