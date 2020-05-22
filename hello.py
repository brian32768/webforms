from flask import Flask, render_template
app = Flask(__name__)
@app.route("/")
def fun():
    return "hello"
app.run()
