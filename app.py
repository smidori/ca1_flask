import datetime
from flask import Flask, jsonify, request, render_template, redirect,url_for
app = Flask(__name__)

movies = [
  {
    "id": 1,
    "title": "Forrest Gump",
    "description": "An Alabama man with an IQ of 75 who merely wants to be reunited with his childhood sweetheart observes the Kennedy and Johnson presidencies, the Vietnam War, the Watergate crisis, and other historical events.",
    "genres": "Drama, Romance"
  },
  {
    "id": 2,
    "title": "Edward Scissorhands",
    "description": "A stunning adolescent lady and an unusually kind young man who just so happens to have scissors for hands fall in love.",
    "genres": "Drama, Fantasy, Romance" 
  },
  {
    "id": 3,
    "title": "Home Alone",
    "description": "Kevin (Macaulay Culkin), a young boy who is inadvertently left at home while his family takes a flight to Paris for vacation, eats whatever he wants and fights robbers, is the star of the absurd film directed by Chris Columbus. ",
    "genres": "Comedy, Family" 
  },
  {
    "id": 4,
    "title": "The Sixth Sense",
    "description": "A child psychologist who has lost hope seeks the assistance of a boy who talks with spirits that are unaware that they are dead.",
    "genres": "Drama, Mystery, Thriller" 
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

#curl http://localhost:5000/movie/1
@app.get('/movie/<int:id>')
def get_movie(id):
  for movie in movies:
    if movie["id"] == id:
        return jsonify(movie)
  return f'movie with id {id} not found', 404

#curl http://localhost:5000/add_movie --request POST --data '{"id":3,"genres":"aaa","title":"bbb","description":text}' --header "Content-Type: application/json"
@app.post("/add_movie")
def add_movie():
  #data = request.get_json()
  new_id = int(datetime.datetime.now().timestamp())
  new_title = request.form['title']
  new_genres = request.form['genres']
  new_description = request.form['description']
  new_movie = {"id": new_id, "title": new_title, "genres": new_genres, "description": new_description }
  movies.append(new_movie)
  return redirect('/')
  

#curl http://localhost:5000/update_movie/2 --request POST --data '{"genres":"ccc","title":"ddd","description":text}' --header "Content-Type: application/json"
@app.route('/update_movie/<int:id>', methods=['GET','POST'])
def update_movie(id):  
  for movie in movies:
    if movie["id"] == id:
        if request.method=="POST":
          movie["id"] = id
          movie["title"] = request.form['title']
          movie["genres"] = request.form['genres']
          movie["description"] = request.form['description']
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

