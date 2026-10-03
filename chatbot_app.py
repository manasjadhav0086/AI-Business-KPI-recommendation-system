"""
InsightIQ - AI Decision Intelligence Platform - Entrypoint
Preserves backward compatibility for `streamlit run chatbot_app.py`
"""
import runpy
import sys

if __name__ == "__main__" or "streamlit" in sys.modules:
    runpy.run_module("app", run_name="__main__")
