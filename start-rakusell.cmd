@echo off
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

wt.exe ^
 new-tab --title "ChromaDB" --startingDirectory "%BACKEND%" cmd.exe /k ".\venv\Scripts\chroma.exe run --host 0.0.0.0 --port 8001" ^
 ; new-tab --title "Backend" --startingDirectory "%BACKEND%" cmd.exe /k ".\venv\Scripts\python.exe -m daphne -b 0.0.0.0 -p 8000 core.asgi:application" ^
 ; new-tab --title "Celery" --startingDirectory "%BACKEND%" cmd.exe /k ".\venv\Scripts\python.exe -m celery -A core worker -l info -Q default,messages,ai --pool=solo" ^
 ; new-tab --title "Frontend" --startingDirectory "%FRONTEND%" cmd.exe /k "npm run dev -- --host 0.0.0.0 --port 3000" ^
 ; new-tab --title "ngrok + webhook" --startingDirectory "%BACKEND%" cmd.exe /k "start /b ngrok http 8000 & timeout /t 8 /nobreak >nul & .\venv\Scripts\python.exe .\scripts\sync_green_webhook.py"
