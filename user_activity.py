import json
import random
from datetime import datetime, timedelta
import math

num_record = 100_000

user_id_start = 1000000
user_id_end = 1001999
quizz_id_start = 1000000
quizz_id_end = 1000222
cours_id_start = 1000000
cours_id_end = 1000108
chapitre_id_start = 1000000
chapitre_id_end = 1000030

user_activities = []
quizz_scores = []

def main():
    for i in range(num_record):
        user_id = random.randint(user_id_start, user_id_end)
        chapitre_id = random.randint(chapitre_id_start, chapitre_id_end)

        cours_du_chapitre = getCoursChapitre(chapitre_id)
        quizz_du_chapitre = getQuizzChapitre(chapitre_id)

        nb_cours_revise = random.randint(1, len(cours_du_chapitre))
        nb_quizz_fait = get_weighted_quiz_count(len(quizz_du_chapitre))
        
        list_quizz_fait = random.sample(quizz_du_chapitre, nb_quizz_fait)
        list_cours_revise = random.sample(cours_du_chapitre, nb_cours_revise)

        est_assidu = random.choice([True, False])

        generate_one_user_full_session(user_activities, quizz_scores, user_id, chapitre_id, list_quizz_fait, list_cours_revise, est_assidu)

    # Sauvegarde des données dans des fichiers
    save_to_sql_file(quizz_scores, "quiz_scores.sql")
    save_to_json_file(user_activities, "user_interactions.json")


def generate_one_user_full_session(user_activities, quizz_scores, user_id, chapitre_id, list_quizz_fait, list_cours_revise, est_assidu):
    nb_clics_toute_session = 0
    nb_scroll_toute_session = 0
    nb_temps_toute_session = 0
    progression_total = 0

    max_sessions_borne = 100 if est_assidu else 30
    facteur_assiduite = 1 if est_assidu else 0.5
    distraction_factor = random.choice([0.8, 1, 1.2])

    for cours in list_cours_revise:
        max_sessions = random.randint(1, max_sessions_borne)
        chance_arreter = 4 if est_assidu else 10
        progression = 0

        for i in range(max_sessions):
            session_entiere = random.randint(1, 100)
            chance_arreter_iteration = chance_arreter / 2 if progression < 10 else chance_arreter / 3 if progression > 50 else chance_arreter / 4 if progression > 80 else chance_arreter
            arrete = session_entiere < chance_arreter_iteration
            duree_session = random.randint(10000, 180_000) if arrete else 180_000

            clics = round(((random.randint(1, 5) * (duree_session / 60_000)) * facteur_assiduite) * distraction_factor)
            scroll = round(((random.randint(1, 20) * (duree_session / 60_000)) * facteur_assiduite) * distraction_factor)

            # Calculate progression increment
            progression_increment = calculate_progression(progression, max_sessions, i, duree_session, clics, scroll, distraction_factor)
            progression += progression_increment

            # Generate and store interaction
            interaction = generate_user_interaction(user_id, cours, chapitre_id, duree_session, clics, scroll, progression)
            user_activities.append(interaction)

            nb_clics_toute_session += clics
            nb_scroll_toute_session += scroll
            nb_temps_toute_session += duree_session
            progression_total += progression_increment
            if arrete or progression == 100 : break


    moyenne_clics_minute = nb_clics_toute_session / (nb_temps_toute_session / 60_000) if nb_temps_toute_session > 0 else 0
    moyenne_scroll_minute = nb_scroll_toute_session / (nb_temps_toute_session / 60_000) if nb_temps_toute_session > 0 else 0
    progression_moyenne = progression_total / len(list_cours_revise) if list_cours_revise else 0

    i = 0
    for quizz in list_quizz_fait:
        note = generate_note(moyenne_clics_minute, moyenne_scroll_minute, nb_temps_toute_session, progression_moyenne, i)
        quiz_score = generate_quizz_score(user_id, quizz, note)
        quizz_scores.append(quiz_score)
        i += 1


def get_ids_from_sql(file_path, table_name, chapitre_id):
    ids = []
    with open(file_path, 'r') as file:
        for line in file:
            # Ensure the line pertains to the correct table and contains the exact chapitre_id
            if f"INSERT INTO {table_name}" in line:
                # Extract just the value part after 'VALUES ('
                values_part = line.split('VALUES (')[1].split(')')[0]  # Also removing the closing parenthesis
                values = values_part.split(', ')
                
                # Parse the chapitre_id from the correct position based on the table
                chapitre_index = 3 if table_name == 'cours' else 2
                chapitre_value = int(values[chapitre_index].strip())
                
                if chapitre_value == chapitre_id:
                    # Get the ID of the element, which is always the first value in 'values'
                    id_element = int(values[0])
                    ids.append(id_element)
    return ids


def getCoursChapitre(chapitre_id):
    file_path = 'database.sql'
    return get_ids_from_sql(file_path, 'cours', chapitre_id)

def getQuizzChapitre(chapitre_id):
    file_path = 'database.sql'
    return get_ids_from_sql(file_path, 'quizz', chapitre_id)

def generate_user_interaction(user_id, cours_id, chapitre_id, dureeSession, clics, scroll, progression):
    # Créer le JSON de l'interaction
    interaction = {
        "userId": user_id,
        "coursId": cours_id,
        "chapitreId": chapitre_id,
        "dureeSession": dureeSession,
        "timestamp": datetime.now().isoformat() + '+00:00',  # Timestamp actuel
        "clics": clics,
        "scrolls": scroll,
        "progression": progression
    }
    return json.dumps(interaction)

def generate_quizz_score(user_id, quizz_id, score):
    # Créer l'INSERT du score
    quizz_score_sql = f"INSERT INTO note_quizz (date, note, id_quizz, id_utilisateur) VALUES ('{datetime.now().isoformat()}', {score}, {quizz_id}, {user_id});"
    return quizz_score_sql

def generate_note(moyenne_clics_minute, moyenne_scroll_minute, nb_temps_toute_session, progression, nb_quizz_lie_passer):
    # Base de la note influencée par le temps et la progression
    base_time_in_hours = nb_temps_toute_session / 3600000  # Convertir en heures
    score_base = random.randint(2,5)
    base_score = min(score_base + 3.5 * math.log(2 + base_time_in_hours), 10) # Score de base de 10, max 16 par le log

    # Influence de la progression sur la note
    progression_score = (progression / 100) * 6  # La progression peut ajouter jusqu'à 4 points

    # Modulation par les clics et les scrolls
    clics_modifier = min(moyenne_clics_minute * 0.1, 3)
    scroll_modifier = min(moyenne_scroll_minute * 0.05, 3)

    # Influence du nombre de quizz du meme chapitre passés
    nb_quizz_modifier = min(nb_quizz_lie_passer * 1, 3)

    # Assemblage de la note finale
    final_score = base_score + progression_score + clics_modifier + scroll_modifier + nb_quizz_modifier

    # Facteur aléatoire (alpha)
    alpha = 0.9  # 90% basé sur le calcul, 10% aléatoire
    random_factor = random.uniform(0.7, 1.3)  # Un petit facteur aléatoire pour simuler la variation de performance
    final_score = (final_score * alpha) + (final_score * (1 - alpha) * random_factor)

    return round(final_score)


def calculate_progression(current_progress, max_sessions, session_index, session_duration, clics, scrolls, distraction_factor):
    # Facteur de fatigue qui augmente avec le nombre de sessions complétées
    fatigue_factor = 1 - (session_index / max_sessions) * 0.2  # Augmente la fatigue de 10% par session

    # Effet d'oubli qui diminue la progression pour chaque session
  
    forgetfulness_factor = 1 - (session_index / max_sessions) * 0.1 # Diminution de la rétention

    # Base progression increment adjusted for session duration and forgetting effect
    base_increment = (100 / max_sessions) * (session_duration / 180000) * fatigue_factor * forgetfulness_factor

    # the distraction factor reduce or increase the base increment
    base_increment = base_increment * distraction_factor

    # Modifiers based on user interaction intensity
    clics_modifier = (clics / 100) * fatigue_factor  # Adjusting clicks influence for fatigue
    scrolls_modifier = (scrolls / 50) * fatigue_factor  # More weight to scrolls, adjusting for fatigue

    # Combine modifiers with base increment
    progression_increment = base_increment + clics_modifier + scrolls_modifier
    
    # Ensure that the total progression does not exceed 100%
    if current_progress + progression_increment > 100:
        progression_increment = 100 - current_progress

    return progression_increment


def save_to_sql_file(data, filename="output.sql"):
    with open(filename, "w") as file:
        for entry in data:
            file.write(entry + "\n")

def save_to_json_file(data, filename="interactions.json"):
    with open(filename, "w") as file:
        for entry in data:
            file.write(entry + "\n")


def get_weighted_quiz_count(available_quizzes):
    if available_quizzes == 0:
        return 0

    if available_quizzes <= 3:
        return random.randint(1, available_quizzes)
    
    if available_quizzes <= 6:
        ranges = [(1, 3), (4, min(available_quizzes, 6))]
        probabilities = [0.8, 0.2]

    elif available_quizzes <= 10:
        ranges = [(1, 3), (4, 5), (6, available_quizzes)]
        probabilities = [0.6, 0.3, 0.1]
    else:
        ranges = [(1, 3), (4, 5), (6, 9), (10, min(20, available_quizzes))]
        probabilities = [0.5, 0.4, 0.075, 0.025]

    # Choose a range based on the defined probabilities
    selected_range = random.choices(ranges, weights=probabilities, k=1)[0]

    # Check to avoid random.randint error if start and end of the range are the same
    if selected_range[0] == selected_range[1]:
        return selected_range[0]
    else:
        return random.randint(*selected_range)


if __name__ == "__main__":
    main()