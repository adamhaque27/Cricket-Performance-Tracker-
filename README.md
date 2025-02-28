# Cricket-Performance-Tracker
The app helps users track their performance throughout the season and shows improvements 

## Success Criteria 

### User Authentication & Security 
 
☑ Users can securely register, log in, and log out. 
☑ Passwords are hashed before storage to enhance security. 
☑ Duplicate usernames and emails are prevented during registration. 
☐ Users can securely reset or update their passwords. 

### Club & Season Management 
 
☐ Users can join and switch clubs, with a history of past club memberships. 
☐ The app supports multiple clubs and seasons, allowing players to filter performance by season. 
☐ Admins can manage club details and assign players to clubs. 

### Match & Performance Tracking 
 
☑ Users can log match details, including date, opponent, and venue. 
☑ Batting statistics such as runs, balls faced, strike rate, fours, sixes, and not-out status are recorded. 
☑ Bowling statistics such as overs bowled, wickets, maidens, economy rate, and bowling speed are tracked. 
☐ Over-by-over analysis is available, detailing runs conceded, wickets per over, dot balls, and extras. 

### Database & Data Integrity 
 
☑ The SQLite database reliably stores all users, clubs, seasons, matches, and performance data. 
☑ Foreign key constraints maintain data integrity and prevent orphan records. 
☐ Users can edit and delete their match entries while ensuring database consistency. 

### User Interface & Experience (UI/UX) 
 
☑ The Kivy-based UI is responsive, user-friendly, and compatible with touchscreens. 
☑ A clear and structured navigation system allows easy access to features. 
☐ Data entry forms include validation to prevent errors and ensure accuracy. 
☐ A leader board displays top-performing players based on key stats. 

### Data Visualisation & Analytics 
 
☐ Users can generate interactive performance graphs using Matplotlib. 
☐ Graphs display batting and bowling statistics filtered by match, season, or club. 
☐ Performance trends are visualised using Manhattan graphs, bar charts, and line charts. 

### Additional Features 
 
☐ Users can export their performance data as CSV files. 
☐ Admins have access to an admin panel for managing clubs, matches, and users. 
☐ Real-time calculations for statistics such as strike rate and economy rate are provided. 

### Performance & Compatibility 
 
☑ The app runs smoothly on Windows, using Python and Kivy. 
☑ The app remains lightweight, ensuring fast database queries and UI responsiveness. 
☑ The code follows a well-structured MVC (Model-View-Controller) architecture for maintainability.