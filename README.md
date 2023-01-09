# About

- This is a **Quantified Self app** which can tracks daily activities.
- It was a project for the course **Modern Application Development 1** of **BS Degree (4 Yrs)** at **IIT Madras**.

# Features

- Signup for new users and Login for registered users.
- Profile button to fetch basic details of a user.
- Creation of a new tracker and Deletion and Modification of an existing tracker with Timestamp.
- Switch task among three different categories : todo, doing and done.
- Summary page to check the previous logs details.

# How to run the code?

## VS Code
- Download the above code as a zip and extract it.
- Open the extracted folder in VS Code.
- Install necessary dependencies in shell.

` $ pip install -r requirements.txt`
- Open `app.py` file.
- Go to **python** console.
- Run the following commands:
  - `from app import db`
  - `db.create_all()`
  *This will create database with required tables.*
- Run `app.py` file.
- Your application should be up and running at `http://127.0.0.1:5000/`
- Copy the `http://127.0.0.1:5000/` and paste it in browser or press **(ctrl+link)**.

