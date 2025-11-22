"Prosty symulator inwestowania - work still in progress"

# Biblioteki 
Następujące biblioteki są wymagane do uruchomienia projektu
* `dotenv>=0.9.9`
* `pyside6>=6.10.0`
* `openai>=2.7.2`

Lista wszystkich bibliotek znajduje się w pliku `pyproject.toml`


# Środowisko python
To set up the env do the following:
1. Install uv using guide `https://docs.astral.sh/uv/getting-started/installation/`
2. Open project folder
3. Run `uv sync` command
4. Activate virtual env created by `uv` and use `python main.py` command or use `uv run main.py` directly


# Zmienne środowiskowe
To correctly load secrets like `OPENAI_API_KEY` to the app do the following:
1. Create an empty `.env` file in the root directory of a project. This file will be ignored by `git` and will never be commited. It is much safer to store secrets in such file in order to not commit it by accident.
2. Add env variable to the file. For now we only use `OPENAI_API_KEY` to safely load key to env, therefore file should look like this:

    ```YAML
    OPENAI_API_KEY=<key>
    ```
3. ??????
4. PROFIT


# Uruchomienie

```bash
python main.py
```