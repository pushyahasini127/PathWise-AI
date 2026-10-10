# PathWise Step 4 — Evaluation + Enhanced Dashboard

## Windows VS Code quick start

1. Extract ZIP.
2. Open the **inner `PathWise_Step4_Enhanced` folder**, the one containing `app.py`, in VS Code.
3. Open a terminal there and run:

```powershell
uv run --python 3.13 --with streamlit --with pandas streamlit run app.py
```

Then visit `http://localhost:8501` on the same computer. Keep the terminal open. Stop with Ctrl+C.

**Important:** Do not run from your old `PathWise_AI_Engine_Starter` folder. Check `dir app.py` first.

## Run unit tests and generate evidence

```powershell
uv run --python 3.13 python -m unittest discover -s tests -v
uv run --python 3.13 python evaluate.py
```

The evaluation script creates `reports/evaluation_results.json` and `reports/evaluation_profiles.csv`.

## What's new since Step 3?
- Compare up to four recommended eligible courses; export comparison CSV.
- Evaluation tab with profile-level rule compliance, ranking order and deterministic-output checks.
- Separate evaluation CLI, additional tests and generated evidence files.
- Review 2 technical notes, slide outline and editable Mermaid architecture diagram in `docs/`.

## Important methodological note
This project uses rule-based prerequisite checking and an interpretable content-matching heuristic. It does not train an ML model or measure real-world recommendation accuracy. The course catalogue and student profiles are synthetic.
