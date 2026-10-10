# PathWise — Step 5 (Academic Roadmap + What-if + Grounded Assistant)

## Start the web app (Windows / VS Code)

Open the **inner `PathWise_Step5_Enhanced`** folder containing `app.py` in VS Code. Run:

```powershell
uv python install 3.13
uv run --python 3.13 --with streamlit --with pandas streamlit run app.py
```

Open the **Local URL** displayed in the terminal (typically `http://localhost:8501`). Keep the terminal running. Stop with Ctrl+C.

## Run tests

```powershell
uv run --python 3.13 python -m unittest discover -s tests -v
uv run --python 3.13 python evaluate.py
```

## Features

- All Step 4 features: student profiles, AI recommendations, eligibility, skill gaps, compare, evaluation, explainability.
- **Roadmap:** hypothetical course prerequisite learning sequence with explicit unresolved prerequisites.
- **What-if Lab:** compare baseline and hypothetical profiles, including newly eligible/blocked courses.
- **Grounded assistant:** offline constrained FAQ using course data and existing engine, not an LLM.

See `docs/STEP5_TECHNICAL_GUIDE.md` for algorithms, limitations, and demo script.

**Caution:** Data and students are synthetic. Verify all real institutional prerequisites. Suitability scores are not success probabilities. No trained ML model or external generative AI is used.
