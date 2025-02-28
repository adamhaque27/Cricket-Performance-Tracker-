#Cricket Performance Tracker 
#Author Adam Haque 
#Start date: 07/02/2024
# Import necessary modules from Kivy and other libraries
import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
import sqlite3
from hashlib import sha256
import uuid
import smtplib
from email.mime.text import MIMEText

# Ensure the Kivy version is at least 2.0.0
kivy.require('2.0.0')

# Database initialisation function
def init_db():
    # Connect to the SQLite database
    conn = sqlite3.connect('cricket_tracker.db')
    cursor = conn.cursor()
    
    # Create the users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Create the clubs table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clubs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')
    
    # Create the seasons table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seasons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_id INTEGER,
        name TEXT NOT NULL,
        FOREIGN KEY (club_id) REFERENCES clubs(id)
    )
    ''')
    
    # Create the matches table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        season_id INTEGER,
        date TEXT NOT NULL,
        opponent TEXT NOT NULL,
        venue TEXT NOT NULL,
        winning_team TEXT NOT NULL,
        team_scores TEXT NOT NULL,
        FOREIGN KEY (season_id) REFERENCES seasons(id)
    )
    ''')
    
    # Create the batting_stats table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS batting_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        user_id INTEGER,
        runs INTEGER,
        balls INTEGER,
        strike_rate REAL,
        fours INTEGER,
        sixes INTEGER,
        not_out INTEGER,
        FOREIGN KEY (match_id) REFERENCES matches(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # Create the bowling_stats table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bowling_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        user_id INTEGER,
        overs REAL,
        runs_conceded INTEGER,
        wickets INTEGER,
        maidens INTEGER,
        economy_rate REAL,
        FOREIGN KEY (match_id) REFERENCES matches(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # Create the over_stats table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS over_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bowling_stat_id INTEGER,
        over_number INTEGER,
        dot_balls INTEGER,
        extras INTEGER,
        wickets INTEGER,
        FOREIGN KEY (bowling_stat_id) REFERENCES bowling_stats(id)
    )
    ''')
    
    # Create the reset_tokens table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reset_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        token TEXT NOT NULL
    )
    ''')
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Function to hash passwords using SHA-256
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# Function to add a user to the database
def add_user(username, password):
    conn = sqlite3.connect('cricket_tracker.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hash_password(password)))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Username already exists")
    conn.close()

# Function to retrieve a user from the database
def get_user(username):
    conn = sqlite3.connect('cricket_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to get user by email
def get_user_by_email(email):
    conn = sqlite3.connect('cricket_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to print the contents of a table
def print_table(table_name):
    conn = sqlite3.connect('cricket_tracker.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()
    conn.close()
    print(f"Contents of {table_name}:")
    for row in rows:
        print(row)

# Function to print the contents of all tables
def print_all_tables():
    tables = ['users', 'clubs', 'seasons', 'matches', 'batting_stats', 'bowling_stats', 'over_stats']
    for table in tables:
        print_table(table)

# Function to add match results to the database
def add_match_result(season_id, date, opponent, venue, winning_team, team_scores, batting_stats, bowling_stats):
    conn = sqlite3.connect('cricket_tracker.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO matches (season_id, date, opponent, venue, winning_team, team_scores) VALUES (?, ?, ?, ?, ?, ?)',
                   (season_id, date, opponent, venue, winning_team, team_scores))
    match_id = cursor.lastrowid
    for stat in batting_stats:
        cursor.execute('INSERT INTO batting_stats (match_id, user_id, runs, balls, strike_rate, fours, sixes, not_out) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                       (match_id, stat['user_id'], stat['runs'], stat['balls'], stat['strike_rate'], stat['fours'], stat['sixes'], stat['not_out']))
    for stat in bowling_stats:
        cursor.execute('INSERT INTO bowling_stats (match_id, user_id, overs, runs_conceded, wickets, maidens, economy_rate) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (match_id, stat['user_id'], stat['overs'], stat['runs_conceded'], stat['wickets'], stat['maidens'], stat['economy_rate']))
    conn.commit()
    conn.close()

# Function to generate a reset token
def generate_reset_token(email):
    token = str(uuid.uuid4())
    conn = sqlite3.connect('cricket_tracker.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reset_tokens (email, token) VALUES (?, ?)', (email, token))
    conn.commit()
    conn.close()
    return token

# Function to send a reset email
def send_reset_email(email, token):
    reset_link = f"http://yourdomain.com/reset_password?token={token}"
    msg = MIMEText(f"Click the link to reset your password: {reset_link}")
    msg['Subject'] = 'Password Reset'
    msg['From'] = 'performancecricketstats@gmail.com'
    msg['To'] = email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('performancecricketstats@gmail.com', 'yourpassword')
        server.sendmail(msg['From'], [msg['To']], msg.as_string())

# Function to validate reset token
def validate_reset_token(token):
    conn = sqlite3.connect('cricket_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reset_tokens WHERE token=?', (token,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Function to get email by token
def get_email_by_token(token):
    conn = sqlite3.connect('cricket_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM reset_tokens WHERE token=?', (token,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Function to update password
def update_password(email, new_password):
    hashed_password = hash_password(new_password)
    conn = sqlite3.connect('cricket_tracker.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password=? WHERE email=?', (hashed_password, email))
    conn.commit()
    conn.close()

# Function to clear all data in the database
def clear_db():
    conn = sqlite3.connect('cricket_tracker.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users')
    cursor.execute('DELETE FROM clubs')
    cursor.execute('DELETE FROM seasons')
    cursor.execute('DELETE FROM matches')
    cursor.execute('DELETE FROM batting_stats')
    cursor.execute('DELETE FROM bowling_stats')
    cursor.execute('DELETE FROM over_stats')
    cursor.execute('DELETE FROM reset_tokens')
    conn.commit()
    conn.close()

# Class for the login screen
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.username = TextInput(hint_text='Username', multiline=False)
        self.password = TextInput(hint_text='Password', password=True, multiline=False)
        login_button = Button(text='Login')
        login_button.bind(on_press=self.login)
        register_button = Button(text='Register')
        register_button.bind(on_press=self.register)
        reset_password_button = Button(text='Forgot Password')
        reset_password_button.bind(on_press=self.reset_password)
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(login_button)
        layout.add_widget(register_button)
        layout.add_widget(reset_password_button)
        self.add_widget(layout)

    # Function to handle login
    def login(self, instance):
        conn = sqlite3.connect('cricket_tracker.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (self.username.text, hash_password(self.password.text)))
        user = cursor.fetchone()
        conn.close()
        if user:
            self.manager.current = 'dashboard'
        else:
            popup = Popup(title='Login Failed', content=Label(text='Invalid username or password'), size_hint=(None, None), size=(400, 200))
            popup.open()

    # Function to switch to the registration screen
    def register(self, instance):
        self.manager.current = 'register'

    # Function to switch to the reset password screen
    def reset_password(self, instance):
        self.manager.current = 'reset_password'

# Class for the registration screen
class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super(RegisterScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.username = TextInput(hint_text='Username', multiline=False)
        self.email = TextInput(hint_text='Email', multiline=False)
        self.password = TextInput(hint_text='Password', password=True, multiline=False)
        register_button = Button(text='Register')
        register_button.bind(on_press=self.register)
        layout.add_widget(self.username)
        layout.add_widget(self.email)
        layout.add_widget(self.password)
        layout.add_widget(register_button)
        self.add_widget(layout)

    # Function to handle registration
    def register(self, instance):
        conn = sqlite3.connect('cricket_tracker.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                           (self.username.text, self.email.text, hash_password(self.password.text)))
            conn.commit()
            self.manager.current = 'login'
        except sqlite3.IntegrityError:
            popup = Popup(title='Registration Failed', content=Label(text='Username or email already exists'), size_hint=(None, None), size=(400, 200))
            popup.open()
        conn.close()

# Class for the reset password screen
class ResetPasswordScreen(Screen):
    def __init__(self, **kwargs):
        super(ResetPasswordScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.email = TextInput(hint_text='Email', multiline=False)
        reset_button = Button(text='Reset Password')
        reset_button.bind(on_press=self.reset_password)
        layout.add_widget(self.email)
        layout.add_widget(reset_button)
        self.add_widget(layout)

    # Function to handle password reset
    def reset_password(self, instance):
        email = self.email.text
        user = get_user_by_email(email)
        if user:
            token = generate_reset_token(email)
            send_reset_email(email, token)
            popup = Popup(title='Success', content=Label(text='Password reset email sent'), size_hint=(None, None), size=(400, 200))
        else:
            popup = Popup(title='Error', content=Label(text='Email not found'), size_hint=(None, None), size=(400, 200))
        popup.open()

# Class for the new password screen
class NewPasswordScreen(Screen):
    def __init__(self, **kwargs):
        super(NewPasswordScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.token = TextInput(hint_text='Reset Token', multiline=False)
        self.new_password = TextInput(hint_text='New Password', password=True, multiline=False)
        reset_button = Button(text='Set New Password')
        reset_button.bind(on_press=self.set_new_password)
        layout.add_widget(self.token)
        layout.add_widget(self.new_password)
        layout.add_widget(reset_button)
        self.add_widget(layout)

    # Function to handle setting a new password
    def set_new_password(self, instance):
        token = self.token.text
        new_password = self.new_password.text
        if validate_reset_token(token):
            email = get_email_by_token(token)
            update_password(email, new_password)
            popup = Popup(title='Success', content=Label(text='Password updated successfully'), size_hint=(None, None), size=(400, 200))
        else:
            popup = Popup(title='Error', content=Label(text='Invalid token'), size_hint=(None, None), size=(400, 200))
        popup.open()

# Class for the dashboard screen
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Welcome to the Cricket Performance Tracker'))

        # Section to visualise the database
        visualise_button = Button(text='Visualise Database')
        visualise_button.bind(on_press=self.visualise_database)
        layout.add_widget(visualise_button)

        # Section to enter game results
        self.season_id = TextInput(hint_text='Season ID', multiline=False)
        self.date = TextInput(hint_text='Date', multiline=False)
        self.opponent = TextInput(hint_text='Opponent', multiline=False)
        self.venue = TextInput(hint_text='Venue', multiline=False)
        self.winning_team = TextInput(hint_text='Winning Team', multiline=False)
        self.team_scores = TextInput(hint_text='Team Scores', multiline=False)
        self.batting_stats = TextInput(hint_text='Batting Stats (JSON)', multiline=False)
        self.bowling_stats = TextInput(hint_text='Bowling Stats (JSON)', multiline=False)
        add_result_button = Button(text='Add Match Result')
        add_result_button.bind(on_press=self.add_match_result)
        layout.add_widget(self.season_id)
        layout.add_widget(self.date)
        layout.add_widget(self.opponent)
        layout.add_widget(self.venue)
        layout.add_widget(self.winning_team)
        layout.add_widget(self.team_scores)
        layout.add_widget(self.batting_stats)
        layout.add_widget(self.bowling_stats)
        layout.add_widget(add_result_button)

        self.add_widget(layout)

    # Function to visualise the database
    def visualise_database(self, instance):
        print_all_tables()

    # Function to add match results
    def add_match_result(self, instance):
        season_id = int(self.season_id.text)
        date = self.date.text
        opponent = self.opponent.text
        venue = self.venue.text
        winning_team = self.winning_team.text
        team_scores = self.team_scores.text
        batting_stats = eval(self.batting_stats.text)
        bowling_stats = eval(self.bowling_stats.text)
        add_match_result(season_id, date, opponent, venue, winning_team, team_scores, batting_stats, bowling_stats)
        popup = Popup(title='Success', content=Label(text='Match result added successfully'), size_hint=(None, None), size=(400, 200))
        popup.open()

# Main application class
class CricketApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(ResetPasswordScreen(name='reset_password'))
        sm.add_widget(NewPasswordScreen(name='new_password'))
        return sm

# Entry point of the application
if __name__ == '__main__':
    init_db()  # Initialise the database
    clear_db()  # Clear any existing data in the database
    CricketApp().run()  # Run the Kivy application
    print_all_tables()  # Print all tables in the database