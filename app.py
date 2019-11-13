from flask import Flask, render_template

app = Flask(__name__, template_folder='template')

@app.route('/')
def hello_world():
  SVG_EmptyShelf = './static/shelves.svg'
  return render_template('homepage.html', SVG_EmptyShelf=SVG_EmptyShelf)

if __name__ == '__main__':
    app.run(5000, debug=True)