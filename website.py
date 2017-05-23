from flask import Flask, render_template
import tempInversion
app = Flask(__name__)

@app.route('/')
def homepage():
	author = "David Fisher"
	name = "Temperature Inversion"
	results = tempInversion.main()
	return render_template('index.html', results=results)

if __name__ == '__main__':
	app.run()
