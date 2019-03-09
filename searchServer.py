# main.py
from flask import flash, render_template, request, redirect
from flask import Flask, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
 
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class ReusableForm(Form):
	search = TextField('search:', validators=[validators.required()])

@app.route('/', methods=['GET', 'POST'])
def index():
    search = ReusableForm(request.form)
    if request.method == 'POST':
    	# print search.data['search']
        return search_results(search)
 
    return render_template('index.html', form=search)
 
 
@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']
   
    if search.data['search'] == '':
    	flash('you need to input something')
        return redirect('/')
 
    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        return render_template('search_result.html', results=results)
 
if __name__ == '__main__':
    app.run()