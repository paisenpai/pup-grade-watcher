# PUPSIS Grade Watcher

If you study at PUP, you probably know the story of how it goes every time the semester ends lol.  
Walang katapusang pag-visit sa SIS site, just to see that wala pa ring grades sa ibang subject.  

And that is why I made this system, so you won't need to check the SIS site every day manually.
It checks PUPSIS for you every hour, and emails you **as soon as** there is updates regarding your grades.

All done via **GitHub Actions**, meaning:

- ✅ No setup on your local machine
- 🔐 Your credentials stay secure (they're stored only in your repo secrets and are not visible to anyone else)
- 💤 Set it once, then forget it — auto-checks hourly!

---

## ⚙️ Prerequisites

Before setting up, you need:

1. A GitHub account  
2. Your **PUPSIS login credentials**
3. A free email API key from [Resend](https://resend.com)

---

## 🔧 Setup

1. **Fork this repo** to your GitHub account.

2. Go to your forked repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

3. Add the following secrets:

| Secret Name       | Description                                         | Sample Value                        |
|-------------------|-----------------------------------------------------|-------------------------------------|
| `STUDNO`          | Your student number                                 | `2021-00123-MN-0`                   |
| `BIRTH_MONTH`     | Birth month (number only, no leading zero)         | `1 (for January)`                                 |
| `BIRTH_DAY`       | Birth day (number only, no leading zero)           | `2`                                 |
| `BIRTH_YEAR`      | Birth year                                          | `2005`                              |
| `PASSWORD`        | Your PUPSIS password                                | `XXXXXXX`                          |
| `RESEND_API_KEY`  | API key from [Resend](https://resend.com)          | `re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `EMAIL`           | Where the grade alerts will be sent                | `youremail@gmail.com`              |

4. That’s it! Every hour, GitHub will automatically run the script.  
   Every time there is a new grade update, you’ll get an email.

5. Once **all grades are complete**, you’ll receive a **final email**:  
   _"All grades have been released. No more updates will be sent."_

---

## 🧠 Ethical Note

This project is designed with consideration for PUP’s systems.  
Once all your grades are released, the script **automatically stops checking**,  so we avoid unnecessary load on the SIS servers.  
Please don’t use this for mass scraping, be a responsible student 🙏

---

Made for fellow PUPians like me na sawa na sa kakarefresh sa SIS site : ).
