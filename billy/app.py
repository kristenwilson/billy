from flask import Flask, request, render_template, flash, redirect, url_for, session
import billy
import logging

app = Flask(__name__)
app.secret_key = '23425'

# Configure logging to output to both a file and stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("billy.log"),
        logging.StreamHandler()
    ]
)

@app.route('/')
def index():
    email = request.args.get('email', '')
    return render_template('index.html', email=email)

@app.route('/submit', methods=['POST'])
def submit():
    email = request.form['email']
    filename = request.form['filename']
    pickup = request.form['pickup']
    test_mode = request.form.get('test_mode') == 'on'  # Convert checkbox value to boolean
    
    try:
        # Call the modified main function from billy.py and get messages
        messages = billy.main(email, filename, pickup, test_mode)
        session['messages'] = messages  # Store messages in session for later use
        session['email'] = email  # Store email in session
        logging.info('Processing complete.')
    except billy.BillyError as e:
        flash(f'Error: {str(e)}', 'danger')
        logging.error({str(e)})
        session['messages'] = [str(e)]
        session['email'] = email
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        logging.error(f'Error: {str(e)}')
        session['messages'] = [f'Error: {str(e)}']
        session['email'] = email

    # Redirect to the results page and pass the messages
    return redirect(url_for('results'))

@app.route('/results')
def results():
    # Retrieve messages and email from session
    messages = session.get('messages', [])
    email = session.get('email', '')
    # Clear messages from session after displaying
    session.pop('messages', None)
    return render_template('results.html', messages=messages, email=email)

if __name__ == '__main__':
    app.run(debug=True)