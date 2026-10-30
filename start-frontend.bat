@echo off
echo Lancement du frontend Outsiders...
cd /d "%~dp0frontend"
start http://localhost:5173
npm run dev
