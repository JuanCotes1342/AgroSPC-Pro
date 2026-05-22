# Deploy AgroSPC Pro en Railway

Esta configuracion mantiene la app Streamlit lista para Railway usando `railway.json`.

## 1. Conectar GitHub

1. Entra a `https://railway.app`.
2. Inicia sesion con GitHub.
3. Clic en `New Project`.
4. Selecciona `Deploy from GitHub repo`.
5. Autoriza Railway si lo pide.
6. Escoge el repo `JuanCotes1342/AgroSPC-Pro`.
7. Selecciona la rama `main`.

## 2. Variables de entorno

En el servicio creado, entra a `Variables` y agrega:

```text
DEEPSEEK_API_KEY=tu_api_key_de_deepseek
GEMINI_API_KEY=tu_api_key_de_gemini_opcional
```

`DEEPSEEK_API_KEY` es la principal. `GEMINI_API_KEY` es opcional como respaldo.

No agregues estas variables:

```text
PORT
STREAMLIT_SERVER_PORT
```

Si existen y alguna tiene valor `$PORT`, borralas. El contenedor usa internamente el puerto `8080` y ademas limpia `STREAMLIT_SERVER_PORT` al iniciar para evitar ese error.

Tambien revisa `Settings > Deploy > Start Command`: debe estar vacio. Railway debe usar el `Dockerfile` del repositorio.

## 3. Deploy

Railway usara el `Dockerfile` del repositorio e instalara `requirements.txt`.

El comando de arranque para Railway esta aislado en `railway_start.py`:

```bash
python railway_start.py
```

El contenedor expone el puerto `8080`. Si Railway pide puerto al generar dominio, usa `8080`.

## 4. Generar URL publica

1. Entra al servicio de Railway.
2. Ve a `Settings`.
3. Busca `Networking`.
4. Clic en `Generate Domain`.
5. Abre el dominio generado.

## 5. Mantener Activa Para La Presentacion

Railway no funciona igual que Streamlit Community Cloud, pero revisa el plan y creditos disponibles para evitar suspension por cuota.

Recomendado para la semana de presentacion:

1. Verifica que el proyecto tenga creditos o plan activo.
2. Abre la URL 15 minutos antes.
3. Prueba `Registro`, `Variables`, `Atributos`, `Pareto`, `Ishikawa` y `Reportes`.
4. Mantén tambien una copia local lista como respaldo:

```bash
python -m streamlit run app.py --server.port 8502
```

## Nota Sobre SQLite

El almacenamiento temporal SQLite funciona en Railway, pero si el servicio se reconstruye o reinicia en un entorno sin volumen persistente, la base puede perderse.

Para una demo esta bien. Para produccion estable, usar una base externa como Supabase o Postgres.
