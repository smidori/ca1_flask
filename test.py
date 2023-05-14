import datetime


def get_timestamp(index):
    return str(int( datetime.datetime.now().timestamp() + index))

movies = [
    {
        "id": get_timestamp(0),
        "title": "Becoming",
        "author": "Michelle Obama",
        "price": 22.99
    },
    {
        "id": get_timestamp(1),
        "title": "Humans of New York",
        "author": "Brandon Stanton",
        "price": 19.99
    }
]

for movie in movies:
    movie["id"] = get_timestamp()

for movie in movies:
    print(movie)
