@echo off
cd /d "%~dp0"
uv run --python 3.15 --with streamlit --with pandas streamlit run app.py
pause
