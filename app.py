import datetime
from flask import Flask, jsonify, request, render_template, redirect,url_for
app = Flask(__name__)

movies = [
  {
    "id": 1,
    "title": "Forrest Gump",
    "director": "Robert Zemeckis",
    "releaseDate": "1994",
    "actors": "Tom Hanks,Robin Wright,Gary Sinise",
    "plot": "An Alabama man with an IQ of 75 who merely wants to be reunited with his childhood sweetheart observes the Kennedy and Johnson presidencies, the Vietnam War, the Watergate crisis, and other historical events.",
  },
  {
    "id": 2,
    "title": "Edward Scissorhands",
    "director": "Tim Burton",
    "releaseDate": "1990",
    "actors": "Johnny Depp,Winona Ryder,Dianne Wiest",
    "plot": "A stunning adolescent lady and an unusually kind young man who just so happens to have scissors for hands fall in love.",
  },
  {
    "id": 3,
    "title": "Home Alone",
    "director": "Chris Columbus",
    "releaseDate": "1990",
    "actors": "Macaulay Culkin, Joe Pesci, Daniel Stern",
    "plot": "Kevin (Macaulay Culkin), a young boy who is inadvertently left at home while his family takes a flight to Paris for vacation, eats whatever he wants and fights robbers, is the star of the absurd film directed by Chris Columbus. ",
  },
  {
    "id": 4,
    "title": "The Sixth Sense",
    "director": "M. Night Shyamalan",
    "releaseDate": "1999",
    "actors": "Bruce Willis,Haley Joel Osment,Toni Collette",
    "plot": "A child psychologist who has lost hope seeks the assistance of a boy who talks with spirits that are unaware that they are dead.",
  }  
]

#cancel the operation and go back to index page
@app.route('/cancel', methods=['GET','POST'])
def cancel():
  return redirect('/')


#curl http://localhost:5000
@app.get('/')
def index():
  return render_template('index.html', user = "Silvia",data = movies)

#curl http://localhost:5000/movies
@app.get('/movies')
def hello():
  return jsonify(movies)

#curl http://localhost:5000/movies/1
@app.get('/movies/<int:id>')
def get_movie(id):
  for movie in movies:
    if movie["id"] == id:
        return jsonify(movie)
  return f'movie with id {id} not found', 404


#curl http://localhost:5000/add_movie --request POST --data '{"id":3,"actors":"aaa","title":"bbb","plot":text}' --header "Content-Type: application/json"
@app.route("/add_movie", methods=['GET','POST'])
def add_movie():
  #data = request.get_json()
  if request.method=="POST":
    new_id = int(datetime.datetime.now().timestamp())
    new_title = request.form['title']
    new_director = request.form['director']
    new_releaseDate = request.form['releaseDate']
    new_actors = request.form['actors']
    new_plot = request.form['plot']
    new_movie = {"id": new_id, "title": new_title, "actors": new_actors, "director": new_director, "releaseDate": new_releaseDate,"plot": new_plot }
    movies.append(new_movie)
    return redirect('/')
  else:
    return render_template('add.html')

#curl http://localhost:5000/update_movie/2 --request POST --data '{"actors":"ccc","title":"ddd","plot":text}' --header "Content-Type: application/json"
@app.route('/update_movie/<int:id>', methods=['GET','POST'])
def update_movie(id):  
  for movie in movies:
    if movie["id"] == id:
        if request.method=="POST":
          movie["id"] = id
          movie["title"] = request.form['title']
          movie["director"] = request.form['director']
          movie["releaseDate"] = request.form['releaseDate']
          movie["actors"] = request.form['actors']
          movie["plot"] = request.form['plot']
          return redirect('/')
        else:
          return render_template('update.html', movie = movie)
  return f'movie with id {id} not found', 404

#curl http://localhost:5000/delete_movie/1 --request DELETE
@app.route('/delete_movie/<int:id>', methods=['GET','POST'])
def delete_movie(id):
  for movie in movies:
    if movie["id"] == id:
        if request.method=="POST":
          movies.remove(movie)
          return redirect('/')
        else:
          return render_template('delete.html', movie = movie)
  return f'movie with id {id} not found', 404

