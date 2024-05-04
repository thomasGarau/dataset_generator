import random

def generate_data(num_users):
    # Initialize data lists
    utilisateur_data, utilisateur_valide_data = [], []
    ue_data, chapitre_data, cours_data, quizz_data = [], [], [], []

    # Starting IDs
    id_utilisateur_start = 1000000
    id_ue_start = 1000000
    id_chapitre_start = 1000000
    id_cours_start = 1000000
    id_quizz_start = 1000000

    # Used to ensure unique num_etudiant values
    unique_num_etudiant = set()

    # Generate user data
    for user_id in range(id_utilisateur_start, id_utilisateur_start + num_users):
        # Ensure unique num_etudiant
        while True:
            num_etudiant = f"40{random.randint(100000, 999999)}"
            if num_etudiant not in unique_num_etudiant:
                unique_num_etudiant.add(num_etudiant)
                break
        utilisateur_data.append((user_id, "password123", num_etudiant))
        utilisateur_valide_data.append(
            (num_etudiant, f"Nom{user_id}", f"Prenom{user_id}", f"user{user_id}@example.com",
             "student", random.randint(1, 10), f"{random.randint(1970, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}")
        )

    # Generate academic data
    for ue_id in range(id_ue_start, id_ue_start + 5):
        ue_data.append((ue_id, f"UE Label {ue_id}", f"/path/to/ue{ue_id}"))
        num_chapitres = random.randint(2, 10)
        for chapitre_id in range(id_chapitre_start, id_chapitre_start + num_chapitres):
            chapitre_data.append((chapitre_id, f"Chapitre Label {chapitre_id}", ue_id))
            num_cours = random.randint(2, 5)
            for cours_id in range(id_cours_start, id_cours_start + num_cours):
                cours_data.append((cours_id, f"Cours Label {cours_id}", "Contenu of Cours", chapitre_id))
                num_quizz = random.randint(1, 3)
                for quizz_id in range(id_quizz_start, id_quizz_start + num_quizz):
                    quizz_data.append((quizz_id, f"Quizz Label {quizz_id}", cours_id, chapitre_id, "normal", random.randint(id_utilisateur_start, id_utilisateur_start + num_users - 1)))
                id_quizz_start += num_quizz
            id_cours_start += num_cours
        id_chapitre_start += num_chapitres

    return utilisateur_valide_data, utilisateur_data, ue_data, chapitre_data, cours_data, quizz_data

def write_to_file(filename, data):
    with open(filename, 'w') as file:
        for entry in data:
            file.write(entry + "\n")

# Generate data
num_users = 1000
utilisateur_valide_data, utilisateur_data, ue_data, chapitre_data, cours_data, quizz_data = generate_data(num_users)

# Prepare SQL statements
sql_statements = []
sql_statements.extend([f"INSERT INTO utilisateur_valide (num_etudiant, nom, prenom, mail_utilisateur, role, id_universite, date_naissance) VALUES ('{uv[0]}', '{uv[1]}', '{uv[2]}', '{uv[3]}', '{uv[4]}', {uv[5]}, '{uv[6]}');" for uv in utilisateur_valide_data])
sql_statements.extend([f"INSERT INTO utilisateur (id_utilisateur, mdp, num_etudiant) VALUES ({u[0]}, '{u[1]}', '{u[2]}');" for u in utilisateur_data])
sql_statements.extend([f"INSERT INTO ue (id_ue, label, path) VALUES ({ue[0]}, '{ue[1]}', '{ue[2]}');" for ue in ue_data])
sql_statements.extend([f"INSERT INTO chapitre (id_chapitre, label, id_ue) VALUES ({chap[0]}, '{chap[1]}', {chap[2]});" for chap in chapitre_data])
sql_statements.extend([f"INSERT INTO cours (id_cours, label, contenu, id_chapitre) VALUES ({c[0]}, '{c[1]}', '{c[2]}', {c[3]});" for c in cours_data])
sql_statements.extend([f"INSERT INTO quizz (id_quizz, label, id_chapitre, type, id_utilisateur) VALUES ({q[0]}, '{q[1]}', {q[3]}, '{q[4]}', {q[5]});" for q in quizz_data])

# Write to SQL file
write_to_file("database.sql", sql_statements)
