# Środowisko python
Aby przygotować środowisko env, wykonaj następujące kroki:
1. Zainstaluj uv, korzystając z instrukcji `https://docs.astral.sh/uv/getting-started/installation/`
2. Otwórz folder projektu
3. Uruchom komendę `uv sync`
4. Aktywuj wirtualne środowisko utworzone przez `uv` i użyj polecenia `python main.py` lub uruchom aplikację bezpośrednio `uv run main.py`

# Biblioteki
Aby dodać nową bibliotekę, użyj komendy `uv add`. Na przykład:

```bash
uv add matplotlib
```

# Zmienne środowiskowe
Aby poprawnie załadować sekrety, takie jak `OPENAI_API_KEY`, wykonaj:
1. Utwórz pusty plik `.env` w głównym katalogu projektu. Ten plik jest ignorowany przez `git` i nigdy nie zostanie zacommitowany. Przechowywanie tam sekretów jest znacznie bezpieczniejsze.
2. Dodaj zmienną środowiskową do pliku. Aktualnie używamy tylko `OPENAI_API_KEY`, więc plik powinien wyglądać tak:

    ```YAML
    OPENAI_API_KEY=<key>
    ```

# Uruchomienie

```bash
python -m game.main
```