from application import application

from flask import Flask, render_template

@application.errorhandler(500)
def server_error(e):
    return render_template("500.html", server_error = e)