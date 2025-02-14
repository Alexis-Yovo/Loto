import random
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests

# Fonction pour générer les numéros Loto
def generate_loto_numbers(seed):
    random.seed(seed)
    main_numbers = set()
    bonus_number = set()
    while len(main_numbers) < 5:
        number = random.randint(1, 49)
        main_numbers.add(number)
    while len(bonus_number) < 1:
        number = random.randint(1, 10)
        bonus_number.add(number)
    return sorted(main_numbers), sorted(bonus_number)

# Simulation du double pendule
def double_pendulum(t, y, L1, L2, m1, m2):
    theta1, z1, theta2, z2 = y
    c, s = np.cos(theta1 - theta2), np.sin(theta1 - theta2)

    theta1_dot = z1
    z1_dot = (m2 * g * np.sin(theta2) * c - m2 * s * (L1 * z1**2 * c + L2 * z2**2) -
              (m1 + m2) * g * np.sin(theta1)) / L1 / (m1 + m2 * s**2)
    theta2_dot = z2
    z2_dot = ((m1 + m2) * (L1 * z1**2 * s - g * np.sin(theta2) + g * np.sin(theta1) * c) +
              m2 * L2 * z2**2 * s * c) / L2 / (m1 + m2 * s**2)
    return [theta1_dot, z1_dot, theta2_dot, z2_dot]

# Paramètres du double pendule
g = 9.81  # Accélération gravitationnelle
L1 = 1.0  # Longueur du premier segment
L2 = 1.0  # Longueur du deuxième segment
m1 = 1.0  # Masse du premier segment
m2 = 1.0  # Masse du deuxième segment

# Conditions initiales
theta1_init = np.pi - 0.1  # Angle initial du premier segment
theta2_init = np.pi - 0.2  # Angle initial du deuxième segment
z1_init = 0.0  # Vitesse angulaire initiale du premier segment
z2_init = 0.0  # Vitesse angulaire initiale du deuxième segment

# Temps de simulation
t_span = [0, 10]  # De 0 à 10 secondes
t_eval = np.linspace(0, 10, 500)  # Évaluation à 500 points

# Résolution des équations différentielles
solution = solve_ivp(double_pendulum, t_span, [theta1_init, z1_init, theta2_init, z2_init],
                     args=(L1, L2, m1, m2), t_eval=t_eval)

# Extraction des résultats
theta1 = solution.y[0]
theta2 = solution.y[2]

# Calcul des coordonnées x et y des extrémités du pendule
x1 = L1 * np.sin(theta1)
y1 = -L1 * np.cos(theta1)
x2 = x1 + L2 * np.sin(theta2)
y2 = y1 - L2 * np.cos(theta2)

# Générer une graine à partir du mouvement du double pendule
pendulum_seed = int(np.abs(np.sum(x2) * 10000))  # Convertir les coordonnées en entier

# Fonction pour calculer la date du prochain tirage (lundi, mercredi, samedi)
def next_loto_day(chosen_day):
    today = datetime.now()
    weekday = {"lundi": 0, "mercredi": 2, "samedi": 5}[chosen_day]
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:  # Si le jour est déjà passé cette semaine, ajouter 7 jours
        days_ahead += 7
    next_draw_day = today + timedelta(days=days_ahead)
    next_draw_time = datetime.combine(next_draw_day, datetime.strptime("20:15", "%H:%M").time())
    return next_draw_time

# Fonction pour obtenir les données météo via l'API OpenWeatherMap
def get_weather_data(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"
    response = requests.get(url)
    return response.json()

# Fonction pour récupérer l'état de vigilance via un input
def get_vigilance_status():
    vigilance = input("Êtes-vous en zone de vigilance (oui/non)? ").lower()
    if vigilance == 'oui':
        color = input("Quelle est la couleur de la vigilance (Jaune, Orange, Rouge)? ").capitalize()
        alert_type = input("Quel type de vigilance (vent violent, orages, avalanches, neige-verglas, canicule, grand froid, pluie-inondation, vagues-submersion)? ").lower()
        return f"Zone de vigilance : {color}, Type : {alert_type}"
    else:
        return "Pas de vigilance."

# Fonction pour obtenir le jour de la semaine
def get_weekday():
    weekday = datetime.now().strftime("%A")
    weekdays = {
        "Monday": "Lun",
        "Tuesday": "Mar",
        "Wednesday": "Mer",
        "Thursday": "Jeu",
        "Friday": "Ven",
        "Saturday": "Sam",
        "Sunday": "Dim"
    }
    return weekdays.get(weekday, "Inconnu")

# Demander à l'utilisateur la ville, le code postal et l'API key
city = input("Entrez la ville : ")
postal_code = input("Entrez le code postal : ")
api_key = "ecec2c207dd869ef770284f8efd147b2"

# Obtenir les données météo
weather_data = get_weather_data(city, api_key)
temperature = weather_data['main']['temp']
humidity = weather_data['main']['humidity']
precipitation = weather_data.get('rain', {}).get('1h', 0)
weather_condition = weather_data['weather'][0]['description']

# Créer une graine unique combinée
weather_seed = str(temperature).replace('.', '') + str(humidity) + str(precipitation) + weather_condition
current_datetime = datetime.now()
current_date = current_datetime.strftime("%d/%m/%Y")
current_time_seed = int(current_datetime.strftime("%d%H%M%S%f"))
combined_seed = int(current_time_seed + int(weather_seed[:5]) + pendulum_seed)

# Initialiser le générateur aléatoire avec la graine combinée
random.seed(combined_seed)

# Demander à l'utilisateur de choisir entre lundi, mercredi et samedi
day_of_week = input("Voulez-vous jouer le lundi, mercredi ou samedi ? (lundi/mercredi/samedi) : ").strip().lower()
if day_of_week not in ["lundi", "mercredi", "samedi"]:
    print("Choix invalide. Veuillez entrer 'lundi', 'mercredi' ou 'samedi'.")
    exit()

# Calculer la date et l'heure du prochain tirage
next_draw_datetime = next_loto_day(day_of_week)

# Générer les numéros de loterie
main_numbers, bonus_number = generate_loto_numbers(combined_seed)

# Demander si l'utilisateur veut participer au second tirage
second_draw = input("Voulez-vous participer au 2nd tirage avec la même grille ? (oui/non) : ").strip().lower()
if second_draw == "oui":
    second_draw_main_numbers = main_numbers
else:
    second_draw_main_numbers = None

# Afficher les résultats
print(f"""
---------------------------------------------------------------------------------------------------------
Jour de la semaine     : {get_weekday()}
Date du jour           : {current_date}
Heure actuelle         : {datetime.now().strftime("%H:%M:%S")}
Prochain tirage        : {get_weekday().capitalize()} {next_draw_datetime.strftime('%d/%m/%Y à %H:%M')}
---------------------------------------------------------------------------------------------------------
Ville                  : {city}, Code Postal : {postal_code}
Conditions météo       : {weather_condition.capitalize()}
Température            : {temperature}°C
Humidité               : {humidity}%
Précipitations         : {precipitation} mm
{get_vigilance_status()}
---------------------------------------------------------------------------------------------------------
Tirage Loto            : {main_numbers}, Numéro chance : {bonus_number}
{f"2nd Tirage avec les mêmes numéros : {second_draw_main_numbers}" if second_draw_main_numbers else ""}
""")

# Visualisation optionnelle du double pendule
plt.figure(figsize=(8, 6))
for i in range(0, len(t_eval), 5):
    plt.cla()
    plt.plot([0, x1[i], x2[i]], [0, y1[i], y2[i]], lw=2, color='black')
    plt.plot(x1[i], y1[i], 'o', color='blue')
    plt.plot(x2[i], y2[i], 'o', color='red')
    plt.xlim(-2, 2)
    plt.ylim(-2, 2)
    plt.title(f"Double Pendulum at t={t_eval[i]:.2f}s")
    plt.pause(0.01)

plt.show()
