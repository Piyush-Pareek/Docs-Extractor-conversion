# app.py
from flask import Flask, render_template, session, redirect, url_for
import os
from flask import request, send_file
from werkzeug.utils import secure_filename
from fpdf import FPDF
import re
from openpyxl import Workbook
import qrcode
from io import BytesIO
app = Flask(__name__)  # main class app obj

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here' #secret key that my server knows only menas my browsers 
#creating Folders
UPLOAD_FOLDER = 'uploads' #simple variables
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)   # uses python os lib to create the folders if exit true then do nothing if not writeen give an error
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Main Navigation Route
@app.route('/login', methods=['GET', 'POST'])  #decorator it tells that if someonr visits login url run this dun
#GET: This is what happens when a user just visits the page (like typing the address or clicking a link). They are getting the page to look

# POST: This is what happens when a user submits the login form. They are posting data (username and password) to the server.
def login():
    if request.method == 'POST': #request is an object that hold the incoming data
        username = request.form['username']
        password = request.form['password']
        
      #  login code here 
        # Save the user's login state in the session
        session['username'] = username # session is an object work as temprory storage box
        
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')
@app.route('/')
def home():
    # The main page of our app is the login
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    # Clear the username from the session
    session.pop('username', None)
    return render_template('logout.html')

@app.route('/about-us')
def about_us():
    return render_template('about_us.html')
@app.route('/txt-to-pdf', methods=['GET', 'POST'])
def txt_to_pdf():
    if request.method == 'POST':
        # 1. Look for 'txt_file', not 'file'
        if 'txt_file' not in request.files:
            return "Error: No file part", 400
        
        # 2. Get the file using the correct name
        file = request.files['txt_file']
        
        if file.filename == '' or not file.filename.endswith('.txt'):
            return "Error: Please upload a .txt file", 400

        if file:
            txt_filename = secure_filename(file.filename)
            txt_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
            file.save(txt_path)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            with open(txt_path, 'r', encoding='utf-8') as f:
                for line in f:
                    pdf.cell(0, 10, txt=line, ln=True)

            pdf_filename = txt_filename.rsplit('.', 1)[0] + '.pdf'
            pdf_path = os.path.join(app.config['DOWNLOAD_FOLDER'], pdf_filename)
            pdf.output(pdf_path)

            os.remove(txt_path)
            return send_file(pdf_path, as_attachment=True)

    return render_template('txt_to_pdf.html')

from PyPDF2 import PdfReader, PdfWriter

#  FEATURE 2: ENCRYPT PDF
@app.route('/encrypt-pdf', methods=['GET', 'POST'])
def encrypt_pdf():
    if request.method == 'POST':
        # 1. Get the file and password from the form
        file = request.files['pdf_file']
        password = request.form['password']

        # 2. Basic validation
        if file and file.filename.endswith('.pdf') and password:
            # 3. Save the uploaded PDF
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(pdf_path)

            # 4. Read the PDF, add encryption, and write to a new file
            reader = PdfReader(pdf_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)
            
            writer.encrypt(password)
            
            encrypted_filename = 'encrypted_' + file.filename
            encrypted_path = os.path.join(app.config['DOWNLOAD_FOLDER'], encrypted_filename)
            with open(encrypted_path, "wb") as f:
                writer.write(f)
            
            # 5. Clean up the original uploaded file
            os.remove(pdf_path)

            # 6. Send the new, encrypted file to the user
            return send_file(encrypted_path, as_attachment=True)
        else:
            return "Error: Please upload a PDF and provide a password.", 400

    # If it's a GET request, just show the HTML page
    return render_template('encrypt_pdf.html')

PREDEFINED_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "date": r"\d{2,4}[/-]\d{2,4}[/-]\d{2,4}"
}

# --- FEATURE 3: FIND BY PATTERN (IMPROVED) ---
@app.route('/find-by-pattern', methods=['GET', 'POST'])
def find_by_pattern():
    if request.method == 'POST':
        file = request.files['input_file']
        # 1. Get the user's CHOICE from the new dropdown menu
        choice = request.form['pattern_choice']

        # 2. Look up the actual REGEX pattern from our dictionary
        pattern = PREDEFINED_PATTERNS.get(choice)

        if file and pattern:
            # (The rest of the logic remains exactly the same)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(filepath)
            
            text_content = ""
            if file.filename.endswith('.pdf'):
                reader = PdfReader(filepath)
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
            elif file.filename.endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            
            found_matches = re.findall(pattern, text_content)

            wb = Workbook()
            ws = wb.active
            ws.title = "Pattern Matches"
            ws.append(["Matches Found for: " + choice.capitalize()])
            for match in found_matches:
                ws.append([match])
            
            excel_filename = 'patterns_found.xlsx'
            excel_path = os.path.join(app.config['DOWNLOAD_FOLDER'], excel_filename)
            wb.save(excel_path)
            
            os.remove(filepath)
            return send_file(excel_path, as_attachment=True)
        else:
            return "Error: Please upload a file and select a valid pattern.", 400

    return render_template('find_by_pattern.html')

@app.route('/create-verifiable-pdf', methods=['GET', 'POST'])
def create_verifiable_pdf():
    if request.method == 'POST':
        # 1. Get the text and URL from the form
        circular_text = request.form['circular_text']
        source_url = request.form['source_url']

        if circular_text and source_url:
            # 2. Create a PDF object
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Use multi_cell for better handling of long paragraphs
            pdf.multi_cell(0, 10, txt=circular_text)
            
            # 3. Generate the QR code image in memory
            qr_img = qrcode.make(source_url)
            
            # Save the image to a temporary memory buffer
            qr_bytes = BytesIO()
            qr_img.save(qr_bytes, format='PNG')
            qr_bytes.seek(0) # Go to the beginning of the buffer
            
            # 4. Add the QR code image to the PDF
            # We place it below the text, with a little margin
            pdf.image(qr_bytes, x=10, y=pdf.get_y() + 10, w=40)
            
            # 5. Define the output path and save the PDF
            pdf_path = os.path.join(app.config['DOWNLOAD_FOLDER'], 'verifiable_circular.pdf')
            pdf.output(pdf_path)
            
            # 6. Send the new, verifiable PDF to the user
            return send_file(pdf_path, as_attachment=True)
        else:
            return "Error: Please provide both the text and a source URL.", 400

    # If it's a GET request, just show the HTML page
    return render_template('create_verifiable_pdf.html')

# ===============================================
# --- Route for Our Stretch Goal Feature ---
# ===============================================

@app.route('/decrypt-pdf', methods=['GET', 'POST'])
def decrypt_pdf():
    if request.method == 'POST':
        # 1. Get the file and password from the form
        file = request.files['pdf_file']
        password = request.form['password']

        # 2. Basic validation
        if file and file.filename.endswith('.pdf') and password:
            # 3. Save the uploaded PDF
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(pdf_path)

            try:
                # 4. Attempt to open and decrypt the PDF
                reader = PdfReader(pdf_path)
                
                # This is the key step: try to decrypt
                if reader.is_encrypted:
                    if reader.decrypt(password) == 0:
                        # If decrypt() returns 0, the password was wrong
                        os.remove(pdf_path) # Clean up
                        return "Error: Incorrect password.", 400
                
                # 5. Create a new PDF writer and copy the pages
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)

                # 6. Save the new, decrypted PDF
                decrypted_filename = 'decrypted_' + file.filename
                decrypted_path = os.path.join(app.config['DOWNLOAD_FOLDER'], decrypted_filename)
                with open(decrypted_path, "wb") as f:
                    writer.write(f)

                # 7. Clean up and send the file
                os.remove(pdf_path)
                return send_file(decrypted_path, as_attachment=True)

            except Exception as e:
                os.remove(pdf_path) # Clean up
                print(f"An error occurred: {e}")
                return "An error occurred during decryption. The file might be corrupted or use an unsupported encryption type.", 500
        else:
            return "Error: Please upload a PDF and provide its password.", 400

    # For GET request, just show the HTML page
    return render_template('decrypt_pdf.html')


if __name__ == '__main__':
    app.run(debug=True)