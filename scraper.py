import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import os
from jinja2 import Environment, FileSystemLoader
import resend

load_dotenv()

# Your credentials
STUDNO = os.getenv("STUDNO")
BIRTH_MONTH = os.getenv("BIRTH_MONTH")
BIRTH_DAY = os.getenv("BIRTH_DAY")
BIRTH_YEAR = os.getenv("BIRTH_YEAR")
PASSWORD = os.getenv("PASSWORD")

# API KEY
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL = os.getenv("EMAIL")

LOGIN_URL = "https://sis1.pup.edu.ph/student/"
GRADES_URL = "https://sis1.pup.edu.ph/student/grades"

session = requests.Session()

def grades_fully_released(grades):
    return all(g.get("final_grade", "").strip() != "" for g in grades)

# Step 1: GET login page
response = session.get(LOGIN_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Step 2: Extract CSRF token
csrf_input = soup.find("input", {"name": "csrf_token"})
csrf_token = csrf_input["value"] if csrf_input else None

if not csrf_token:
    print("CSRF token not found.")
    exit()

# Step 3: Prepare login payload
payload = {
    "csrf_token": csrf_token,
    "studno": STUDNO,
    "SelectMonth": BIRTH_MONTH,
    "SelectDay": BIRTH_DAY,
    "SelectYear": BIRTH_YEAR,
    "password": PASSWORD,
    "Login": "Sign in"
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": LOGIN_URL,
    "Origin": "https://sis1.pup.edu.ph",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Step 4: Submit login
login_response = session.post(LOGIN_URL, data=payload, headers=headers)
print("Login Status Code:", login_response.status_code)

# Step 5: Access grades page
grades_response = session.get(GRADES_URL)
print("Grades Page Status Code:", grades_response.status_code)

# Step 6: Parse and extract grades
soup = BeautifulSoup(grades_response.text, "html.parser")
grades_table = soup.find("table", class_="tbldsp")
grades = []

if grades_table:
    rows = grades_table.find("tbody").find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 8:
            grades.append({
                "subject_code": cols[1].get_text(strip=True),
                "description": cols[2].get_text(strip=True),
                "faculty_name": cols[3].get_text(strip=True),
                "units": cols[4].get_text(strip=True),
                "section_code": cols[5].get_text(strip=True),
                "final_grade": cols[6].get_text(strip=True),
                "grade_status": cols[7].get_text(strip=True),
            })

    with open("grades.json", "w", encoding="utf-8") as f:
        json.dump(grades, f, indent=2, ensure_ascii=False)

    print("Grades saved to 'grades.json'")

    # Check if all grades are complete
    if grades_fully_released(grades):
        print("All grades have been finalized.")
        with open(".done", "w") as f:
            f.write("Grades complete.")

        # Send final email notice that this service will end
        final_message = """
        <p><strong>All your grades have been released!</strong></p>
        <p>This is the final notification from the PUPSIS Grade Alert system. No further grade checks will be performed.</p>
        <p>If more grades are added or you want to restart monitoring, delete the <code>.done</code> file in the repo or reset the cache.</p>
        <hr>
        <p>Thank you for using this service!</p>
        """

        resend.api_key = RESEND_API_KEY

        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": EMAIL,
            "subject": "All Grades Released — Monitoring Complete",
            "html": final_message
        })

        print("Final notification email sent. Monitoring ended.")
        exit(0)

else:
    print("Grades table not found.")
    exit()

# Step 7: Compare with previous grades
prev_file = "previous-grades.json"
changes = []

if os.path.exists(prev_file):
    with open(prev_file, "r", encoding="utf-8") as f:
        previous_grades = json.load(f)

    for curr in grades:
        match = next((p for p in previous_grades if p["subject_code"] == curr["subject_code"]), None)
        if not match:
            changes.append(f"New subject added: {curr['subject_code']} - {curr['description']}")
        elif curr["final_grade"] != match["final_grade"]:
            changes.append(f"Grade updated for {curr['description']}: {match['final_grade']} -> {curr['final_grade']}")
        elif curr["grade_status"] != match["grade_status"]:
            changes.append(f"Status changed for {curr['description']}: {match['grade_status']} -> {curr['grade_status']}")

    if changes:
        print("\nChanges detected:")
        for c in changes:
            print("-", c)

        def calculate_gwa(grades):
            excluded_codes = {"CWTS 001", "PATHFIT 1", "PATHFIT 2", "PATHFIT 3", "PATHFIT 4"}
            total_units = 0
            total_weighted = 0

            for g in grades:
                code = g["subject_code"].upper().strip()
                if code in excluded_codes:
                    continue
                try:
                    units = float(g["units"])
                    grade = float(g["final_grade"])
                    total_units += units
                    total_weighted += grade * units
                except ValueError:
                    continue

            return round(total_weighted / total_units, 2) if total_units > 0 else None

        gwa = calculate_gwa(grades)
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("template.html")
        rendered_html = template.render(grades=grades, gwa=gwa)

        with open("rendered_grades.html", "w", encoding="utf-8") as f:
            f.write(rendered_html)

        print("Rendered grade report saved as 'rendered_grades.html'")

        with open("rendered_grades.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        change_summary = "<p><strong>The following grade updates were detected:</strong></p><ul>"
        for c in changes:
            change_summary += f"<li>{c}</li>"
        change_summary += "</ul>"
        change_summary += "<p>For context, here's your full grade report:</p><hr>"

        full_html = change_summary + html_content

        resend.api_key = RESEND_API_KEY

        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": EMAIL,
            "subject": "Grade Update Alert from PUPSIS!",
            "html": full_html
        })

        print("Email sent! Resend response:", response)

    else:
        print("\nNo changes in grades.")
else:
    print("No previous grades found. Creating baseline...")

# Step 8: Update previous-grades.json
with open(prev_file, "w", encoding="utf-8") as f:
    json.dump(grades, f, indent=2, ensure_ascii=False)

# Cleanup
for file in ["grades_page.html", "rendered_grades.html"]:
    if os.path.exists(file):
        os.remove(file)
