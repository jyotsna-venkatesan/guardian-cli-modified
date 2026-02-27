# Guardian CLI 

This project is based on [zakirkun/guardian-cli](https://github.com/zakirkun/guardian-cli).

---

#### Setup


> **Note 1:** Make sure Docker Desktop (or Docker Engine) is running before executing any build or run commands.
> **Note 2:** If you are running the code from Hong Kong, you must use a VPN, as LLMs are banned in Hong Kong and will not work without one.

##### 1. Add .env file
Create a file at `config/.env` and add your `OPENROUTER_API_KEY`:

```
OPENROUTER_API_KEY=your_api_key_here
```

##### 2. Build Docker Image
Open PowerShell (Administrator) and run:

```
cd C:\Users\KPMGcyberdefense01\Documents\guardian-cli-test\guardian-cli
docker build -t guardian-cli .
```

##### 3. Run Guardian CLI
To run all_tools workflow:

```
cd C:\Users\KPMGcyberdefense01\Documents\guardian-cli-test
docker run --rm -v "${PWD}:/guardian" guardian-cli workflow run --name all_tools --target https://dvwa.csalab.app
```
---

#### File Structure
This repository contains guardian-cli-test as the main project directory.


 - Testing and workflow execution environment
 - Storage for tool outputs, dependencies, and environment files required for certain tools
 - The guardian-cli directory (inside guardian-cli-test) contains the core CLI code and logic

---

#### Getting Started 
 - Review the guardian-cli/README.md for CLI usage and workflow details
 - Make sure your .env file is set up before running any workflow
 - Use the provided Docker commands for building and running workflows
 - Outputs and reports are stored in guardian-cli-test directories for easy access
 - For troubleshooting, check logs/ and reports/ folders

---

#### Next Steps
 - Change the AI model from claude-sonnet-4-5 to google/gemini-2.5-flash for lower token usage. This will enable us to get detailed technical explanations for all 60 vulnerabilities that are generated for dvwa. 