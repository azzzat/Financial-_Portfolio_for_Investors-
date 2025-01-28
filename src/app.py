#!/usr/bin/env python3

import os

from flask import Flask, render_template, request

app = Flask(__name__, template_folder='./templates')

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    input_text = request.form.get("user_input", "")
    return render_template('index.html', input_text=input_text)

if __name__ == '__main__':
    app.run(debug=True)
