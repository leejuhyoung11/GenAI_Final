

# **How to Run This Project (Reproducibility Guide)**

Follow the steps below to fully reproduce the results in this repository.


## 1. Set up API keys

Create a .env file in the project root directory and add your API keys as follows

```markdown
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxx

```

## 2. How to run

To run streamlit app env,

```markdown
uv run streamlit run src/ui/app.py
```

To run main.py
```markdown
uv run main.py
```