import requests
from icalendar import Calendar
import subprocess
import os
import re

# ------------- CONFIG -------------
GIT_PATH = "/usr/bin/git"
REPO_PATH = "/home/arthur/App/batchs/edt_LiU_Swedish_Courses"  # chemin du repo
ICS_URL = "https://cloud.timeedit.net/liu/web/schema/s/s.ics?i=60Z956X35Z04Q6Z76g8Y00y6036Y59n04gQY6Q547395Q14"  # URL du fichier ICS original
LOCAL_ICS = "edt_filtre"           # fichier local
GIT_COMMIT_MSG = "Mise à jour de l'emploi du temps filtré"
# ----------------------------------

# 1️⃣ Télécharger le fichier ICS depuis le lien
print("Téléchargement du fichier ICS...")
response = requests.get(ICS_URL)
if response.status_code != 200:
    raise Exception(f"Erreur lors du téléchargement : {response.status_code}")

# Sauvegarde du fichier téléchargé
with open(f"{REPO_PATH}/{LOCAL_ICS}_complet.ics", "wb") as f:
    f.write(response.content)
print("Fichier téléchargé et sauvegardé.")


# recuperer les groupes
print("Récupération des groupes...")
with open(f"{REPO_PATH}/{LOCAL_ICS}_complet.ics", "rb") as f:
    gcal = Calendar.from_ical(f.read())

lettres = []
for component in gcal.walk():
    if component.name == "VEVENT":
        summary = str(component.get('summary'))
        match = re.search(r"grupp (\w)".lower(), summary.lower())
        if match:
            lettre = match.group(1)
            if lettre not in lettres:
                lettres.append(lettre)
lettres.sort()
print(f"Groupes trouvés : {lettres}")



for lettre in lettres:
    # 2️⃣ Filtrer les événements
    print("Filtrage des événements...")
    with open(f"{REPO_PATH}/{LOCAL_ICS}_complet.ics", "rb") as f:
        gcal = Calendar.from_ical(f.read())

    new_cal = Calendar()
    new_cal.add('prodid', '-//Agenda filtré//')
    new_cal.add('version', '2.0')

    for component in gcal.walk():
        if component.name == "VEVENT":
            summary = str(component.get('summary'))
            if lettre.lower() in summary.lower():
                new_cal.add_component(component)

    # Écraser le fichier local avec le calendrier filtré
    with open(f"{REPO_PATH}/{LOCAL_ICS}_{lettre.upper()}.ics", "wb") as f:
        f.write(new_cal.to_ical())
    print(f"Fichier filtré sauvegardé : {f"{REPO_PATH}/{LOCAL_ICS}_{lettre.upper()}.ics"}")





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