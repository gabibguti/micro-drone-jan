from flask import Flask, render_template

app = Flask(__name__, template_folder='template')

@app.route('/')
def hello_world():
  return render_template('homepage.html')

if __name__ == '__main__':
    app.run(5000, debug=True)