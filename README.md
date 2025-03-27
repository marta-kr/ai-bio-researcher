# AI Agents in Bioinformatics

Welcome to the **AI Agents in Bioinformatics** project! This repository contains a system of AI agents that collaborate on a bioinformatics research topic. The agents mine arXiv literature to construct a knowledge graph, analyze the current state of the field, and propose novel research directions. For more insights and related articles, please visit our blog: [My Programming, AI & Mobile Blog](https://collectivemind.blog).


## Cloning the Repository

This repository uses Git submodules to include the modified LightRAG library. To ensure you get everything you need, clone the repository recursively:

```bash
git clone --recursive https://github.com/marta-kr/LightRAG.git
```

If you have already cloned the repository without the submodules, run:

```bash
git submodule update --init --recursive
```

## Setting Up the Python Environment

You can set up the environment using either a virtual environment with `requirements.txt` or with Poetry.

### Option 1: Virtual Environment & requirements.txt

1. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Poetry

1. **Install Poetry**  
   (Follow instructions at [Poetry's documentation](https://python-poetry.org/docs/)).

2. **Install dependencies:**

   ```bash
   poetry install
   ```

3. **Run the project with Poetry:**

   ```bash
   poetry run python main.py
   ```

## Configuring API Keys

The project requires an OpenAI API key. The key is read from the environment variable `OPENAI_API_KEY`. If it is not set, you will be prompted to enter your key. To avoid the prompt, you can manually set the environment variable before running the project:

- **On macOS/Linux:**

  ```bash
  export OPENAI_API_KEY=your_openai_api_key_here
  ```

- **On Windows:**

  ```cmd
  set OPENAI_API_KEY=your_openai_api_key_here
  ```

## Working with the LightRAG Submodule

The modified LightRAG library is included as a submodule under `external/LightRAG`.