
@echo off
cd /d "c:\Users\ramana naveen kumar\AI_Travel_Planner"
"C:\Program Files\Git\cmd\git.exe" config user.name "Ramana Naveen"
"C:\Program Files\Git\cmd\git.exe" config user.email "rnaveenkumar-ds@gmail.com"
"C:\Program Files\Git\cmd\git.exe" pull origin main --allow-unrelated-histories
"C:\Program Files\Git\cmd\git.exe" push -u origin main --force
pause
