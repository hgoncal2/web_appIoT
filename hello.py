from flask import Flask,render_template

app=Flask(__name__)
@app.route("/")
def index():
	return render_template("sidebar.html")

@app.route("/user/<name>")
def user(name):
	return render_template("user.html",name=name)



@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html")

@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
