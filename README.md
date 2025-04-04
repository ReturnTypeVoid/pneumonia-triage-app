
# Flask App Setup

This is a Flask app for managing patient and user data. To get started, follow these steps:

### 1. **Install Python venv**

If you don't have Python's `venv` module installed, you can install it by running:

  ```bash
  sudo apt-get install python3-venv python3-pip
  ```

### 2. **Clone the Repository**

First, clone the repository to your local machine. Run the following command in your terminal:

```bash
git clone <repository_url>
```

### 3. **Change Directory**

Move into the downloaded git repository.:

```bash
cd pneumonia-triage-app
```


### 4. **Create a Virtual Environment**

Create a virtual environment for the project. You can use Python's built-in `venv` module:

```bash
python3 -m venv .venv
```

### 5. **Activate the Virtual Environment**

Activate the virtual environment using the following command:

  ```bash
  source .venv/bin/activate
  ```

### 6. **Install Dependencies**

With the virtual environment activated, install the required Python packages by running:

```bash
pip3 install -r requirements.txt
```

### 7. **Set Up the Database**

Run the following command to set up the database and create sample credentials:

```bash
python ./db-init.py
```

This will generate sample credentials and set up the database. The credentials to log into the app will be displayed in the console output.


### 8. **Run the Application**

Finally, start the Flask app by running:

```bash
python app.py
```

The app will be accessible at `http://127.0.0.1:5000` in your web browser.


This should help you get up and running with the Flask app. Let me know if you need more details!

---

### 9. **Work on a New Branch**

**Important**: All group members must create a new branch for their work. **DO NOT** make changes directly on the `main` branch. Any work done on the `main` branch will **NOT** be merged.

To create and switch to a new branch:

```bash
git checkout -b <branch_name>
```

After finishing your work, you can commit your changes and push them to the repository. When you're ready, open a **pull request** to merge your branch into the `main` branch
