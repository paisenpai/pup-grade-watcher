import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Your credentials
STUDNO = os.getenv("STUDNO")
BIRTH_MONTH = os.getenv("BIRTH_MONTH")
BIRTH_DAY = os.getenv("BIRTH_DAY")
BIRTH_YEAR = os.getenv("BIRTH_YEAR")
PASSWORD = os.getenv("PASSWORD")

# URLs
LOGIN_URL = "https://sis1.pup.edu.ph/student/"

# Start session
session = requests.Session()

# Step 1: GET the login page
response = session.get(LOGIN_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Step 2: Extract CSRF token
csrf_input = soup.find("input", {"name": "csrf_token"})
csrf_token = csrf_input["value"] if csrf_input else None

if not csrf_token:
    print("CSRF token not found.")
    exit()

print("CSRF token found:", csrf_token)

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

# Optional: spoof headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": LOGIN_URL,
    "Origin": "https://sis1.pup.edu.ph",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Step 4: Submit login POST request
login_response = session.post(LOGIN_URL, data=payload, headers=headers)

# Step 5: Inspect result
print("Login Status Code:", login_response.status_code)

# Step 6: Access the grades page
grades_url = "https://sis1.pup.edu.ph/student/grades"
grades_response = session.get(grades_url)

# Inspect result
print("Grades Page Status Code:", grades_response.status_code)
print("Grades Page URL:", grades_response.url)
print("Grades Page Length:", len(grades_response.text))

# Save the HTML content
with open("grades_page.html", "w", encoding="utf-8") as f:
    f.write(grades_response.text)

print("Grades page saved to 'grades_page.html'")

# Step 7: Parse grades and save to JSON
soup = BeautifulSoup(grades_response.text, "html.parser")
grades_table = soup.find("table", class_="tbldsp") # First tbldsp for the latest semester grade only

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

    print("Grades extracted and saved to 'grades.json'")
else:
    print("Grades table not found.")

# Delete the HTML file after having a json copy
if os.path.exists("grades_page.html"):
    os.remove("grades_page.html")
    print("Deleted 'grades_page.html'")
else:
    print("'grades_page.html' not found, skipping deletion.")
