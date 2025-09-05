import requests
from icalendar import Calendar
import subprocess
import os

# ------------- CONFIG -------------
GIT_PATH = "/usr/bin/git"
REPO_PATH = "/home/arthur/App/batchs/edt_LiU_Swedish_Courses"  # chemin du repo
ICS_URL = "https://cloud.timeedit.net/liu/web/schema/s/s.ics?i=60Z956X35Z04Q6Z76g8Y00y6036Y59n04gQY6Q547395Q14"  # URL du fichier ICS original
LOCAL_ICS = "/home/arthur/App/batchs/edt_LiU_Swedish_Courses/edt_filtre.ics"           # fichier local
GIT_COMMIT_MSG = "Mise à jour de l'emploi du temps filtré"
FILTER_KEYWORD = "Grupp F"             # mot-clé pour filtrer les événements
# ----------------------------------

# 1️⃣ Télécharger le fichier ICS depuis le lien
print("Téléchargement du fichier ICS...")
response = requests.get(ICS_URL)
if response.status_code != 200:
    raise Exception(f"Erreur lors du téléchargement : {response.status_code}")

# Sauvegarde du fichier téléchargé
with open(LOCAL_ICS, "wb") as f:
    f.write(response.content)
print("Fichier téléchargé et sauvegardé.")

# 2️⃣ Filtrer les événements
print("Filtrage des événements...")
with open(LOCAL_ICS, "rb") as f:
    gcal = Calendar.from_ical(f.read())

new_cal = Calendar()
new_cal.add('prodid', '-//Agenda filtré//')
new_cal.add('version', '2.0')

for component in gcal.walk():
    if component.name == "VEVENT":
        summary = str(component.get('summary'))
        if FILTER_KEYWORD.lower() in summary.lower():
            new_cal.add_component(component)

# Écraser le fichier local avec le calendrier filtré
with open(LOCAL_ICS, "wb") as f:
    f.write(new_cal.to_ical())
print(f"Fichier filtré sauvegardé : {LOCAL_ICS}")

# 3️⃣ Commit + push automatique sur Git
print("Synchronisation avec GitHub...")
try:
    # Ajouter le fichier
    subprocess.run([GIT_PATH, "-C", REPO_PATH, "add", f"{REPO_PATH}/*"], check=True)
    # Commit
    subprocess.run([GIT_PATH, "-C", REPO_PATH, "commit", "-m", GIT_COMMIT_MSG])
    # Push
    subprocess.run([GIT_PATH, "-C", REPO_PATH, "push"], check=True)

except subprocess.CalledProcessError as e:
    print("Erreur Git :", e)
    print("Peut-être qu'il n'y a pas de changements à committer.")

print("Terminé ✅")


# 53 16 * * * /usr/bin/python3 /home/arthur/Applis/batchs/edt_LiU_Swedish_Courses/filtre.py >> /home/arthur/Applis/batchs/cron.log 2>&1