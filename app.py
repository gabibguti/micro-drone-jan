from flask import Flask, render_template

app = Flask(__name__, template_folder='template', static_folder='static')

@app.route('/')
def hello_world():
  SVG_EmptyShelf = './static/shelves.svg'
  SVG_Package = './static/box_package_color_qrcode_f.svg'
  return render_template('homepage.html', SVG_EmptyShelf=SVG_EmptyShelf, SVG_Package=SVG_Package)

if __name__ == '__main__':
    app.run(debug=True)