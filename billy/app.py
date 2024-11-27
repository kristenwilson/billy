from flask import Flask, request, render_template, flash, redirect, url_for
import billy

app = Flask(__name__)
app.secret_key = '23425'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    email = request.form['email']
    filename = request.form['filename']
    pickup = request.form['pickup']
    test_mode = request.form['test_mode']
    
    try:
        # Call the modified main function from billy.py
        billy.main(email, filename, pickup, test_mode)
        flash('Processing complete.', 'success')
    
    except billy.BillyError as e:
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('index'))
    

if __name__ == '__main__':
    app.run(debug=True)