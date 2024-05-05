import json

def load_chapter_course_counts(sql_file):
    chapter_course_counts = {}
    with open(sql_file, 'r') as file:
        for line in file:
            if "INSERT INTO cours" in line:
                parts = line.split("VALUES")[1].strip().strip("();")
                cours_id, label, contenu, chapitre_id = eval(parts)
                if chapitre_id in chapter_course_counts:
                    chapter_course_counts[chapitre_id] += 1
                else:
                    chapter_course_counts[chapitre_id] = 1
    return chapter_course_counts

def process_json(input_file, output_file, chapter_course_counts):
    user_data = {}

    with open(input_file, 'r') as file:
        for line in file:
            item = json.loads(line.strip())
            user_chap_key = (item["userId"], item["chapitreId"])
            if user_chap_key not in user_data:
                user_data[user_chap_key] = {
                    "DureeTotal": 0,
                    "totalScrolls": 0,
                    "totalClicks": 0,
                    "coursProgression": {},
                    "chapitreProgression": 0  # Initial chapitre progression
                }

            data = user_data[user_chap_key]
            data["DureeTotal"] += item["dureeSession"]
            data["totalScrolls"] += item["scrolls"]
            data["totalClicks"] += item["clics"]

            cours_id = item["coursId"]
            progression = item["progression"]
            data["coursProgression"][cours_id] = progression  # Store progression for each course

    clean_data = []
    for key, values in user_data.items():
        chapter_id = key[1]
        total_progression = sum(values["coursProgression"].values())
        course_count = chapter_course_counts.get(chapter_id, 1)
        values["chapitreProgression"] = total_progression / course_count

        clean_data.append({
            "id_utilisateur": key[0],
            "id_chapitre": chapter_id,
            "DureeTotal": values["DureeTotal"],
            "scrollMinute": values["totalScrolls"] * 60000 / values["DureeTotal"],
            "clicksMinute": values["totalClicks"] * 60000 / values["DureeTotal"],
            "coursProgressions": [{"coursId": k, "progression": v} for k, v in values["coursProgression"].items()],
            "chapitreProgression": values["chapitreProgression"]
        })

    # Write cleaned data to a new JSON file
    with open(output_file, 'w') as f:
        json.dump(clean_data, f, indent=4)

# Load chapter and course counts from the SQL file
chapter_course_counts = load_chapter_course_counts('database.sql')

# Process the JSON data
process_json('user_interactions.json', 'clean_dataset.json', chapter_course_counts)
