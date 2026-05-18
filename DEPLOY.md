# Deploy en Streamlit Community Cloud

1. Sube este proyecto a un repositorio de GitHub.
2. Entra a `https://share.streamlit.io`.
3. Crea una nueva app desde tu repositorio.
4. Main file path: `app.py`.
5. En `App settings > Secrets`, agrega:

```toml
DEEPSEEK_API_KEY = "tu_api_key_deepseek"
GEMINI_API_KEY = "tu_api_key_gemini_opcional"
```

6. Deploy.

Notas:

- No subas claves API al repositorio.
- La base local `database/spc_quality.db` queda ignorada por `.gitignore`.
- El archivo `logo imagen.png` debe permanecer en la raiz del proyecto porque la app lo usa en el sidebar.
