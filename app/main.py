from flask import Flask, render_template, request
from .forms import SearchForm, DetailsForm
from .poster import search_movie, Poster
app = Flask(__name__)
app.config['SECRET_KEY'] = 'polaroidposter'


@app.route('/', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    results = {}
    if form.is_submitted():
        search_term = request.form
        results = search_movie(search_term['search'])
    return render_template('search.html', form=form, results=results)


@app.route('/<int:movie_id>', methods=['GET', 'POST'])
def get_poster(movie_id):
    form = DetailsForm()
    poster = Poster(movie_id)
    title = poster.head_info['title'].text
    if form.is_submitted():
        url = request.form['image_url']
        poster.change_image(url)
        cast = request.form['cast_list']
        poster.change_cast(cast)
    encoded_img_data = poster.encode_image()
    return render_template('poster.html', form=form, title=title, img_data=encoded_img_data.decode('utf-8'))


if __name__ == '__main__':
    app.run()
