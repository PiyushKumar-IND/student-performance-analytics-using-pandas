# Student Performance Analytics Dashboard

## Run locally

1. Install Python.
2. Open a terminal in this folder.
3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the dashboard:

   ```bash
   streamlit run app.py
   ```

The app opens in your browser. It uses `dataset.csv` by default. You can also upload another CSV from the sidebar.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `dataset.csv`.
2. Sign in to Streamlit Community Cloud with GitHub.
3. Choose **New app** and select your repository, branch, and `app.py` as the main file.
4. Deploy.

The original `main.py` can remain in the repository as your command-line Pandas project. Streamlit runs `app.py` as the website entry point.
