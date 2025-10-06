# app.py
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# This will be the main entry point to our app
@app.route('/')
def home():
    # Let's make the login page the first thing users see
    return redirect(url_for('login'))

# This route will handle both showing the login page and processing the login form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # --- THIS IS WHERE YOUR LOGIN LOGIC WILL GO ---
        # For now, we'll just get the data from the form and print it
        username = request.form['username']
        password = request.form['password']
        print(f"Attempting login with Username: {username} and Password: {password}")
        
        # After a successful login, we redirect to the dashboard
        return redirect(url_for('dashboard'))
    
    # If the method is GET, we just show the login page
    return render_template('login.html')

# This route shows the main dashboard after login
@app.route('/dashboard')
def dashboard():
    # Later, we will protect this route so only logged-in users can see it
    return render_template('dashboard.html')

# This route handles the logout link
@app.route('/logout')
def logout():
    # Later, this will clear the user's session
    print("User logged out.")
    return redirect(url_for('login'))


# --- Placeholder Routes for Dashboard Links ---
# These make the links on the dashboard clickable without causing an error

@app.route('/event-extractor')
def event_extractor():
    return "<h1>AI Event Extractor Page</h1><p>The form for this tool will be here.</p>"

@app.route('/pdf-to-word')
def pdf_to_word():
    return "<h1>Convert PDF to Word Page</h1><p>The form for this tool will be here.</p>"

@app.route('/image-to-text')
def image_to_text():
    return "<h1>Extract Text from Image Page</h1><p>The form for this tool will be here.</p>"

# You can add the other routes (merge-pdf, split-pdf, etc.) in the same way


if __name__ == '__main__':
    app.run(debug=True)