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

kivy.require('2.0.0')

# Database initialization
def init_db():
    conn = sqlite3.connect('cricket_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clubs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seasons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_id INTEGER,
        name TEXT NOT NULL,
        FOREIGN KEY (club_id) REFERENCES clubs(id)
    )
    ''')
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
    conn.commit()
    conn.close()

# Secure password hashing
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# Login Screen
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
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(login_button)
        layout.add_widget(register_button)
        self.add_widget(layout)

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

    def register(self, instance):
        self.manager.current = 'register'

# Register Screen
class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super(RegisterScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.username = TextInput(hint_text='Username', multiline=False)
        self.password = TextInput(hint_text='Password', password=True, multiline=False)
        register_button = Button(text='Register')
        register_button.bind(on_press=self.register)
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(register_button)
        self.add_widget(layout)

    def register(self, instance):
        conn = sqlite3.connect('cricket_tracker.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (self.username.text, hash_password(self.password.text)))
            conn.commit()
            self.manager.current = 'login'
        except sqlite3.IntegrityError:
            popup = Popup(title='Registration Failed', content=Label(text='Username already exists'), size_hint=(None, None), size=(400, 200))
            popup.open()
        conn.close()

# Dashboard Screen
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Welcome to the Cricket Performance Tracker'))
        self.add_widget(layout)
        

# Screen Manager
class CricketApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

if __name__ == '__main__':
    init_db()
    CricketApp().run()