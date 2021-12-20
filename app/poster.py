from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import requests
import base64
import imdb
import io


class Text:
    ltrsp = 1; lnsp = 1; lnmax = 2
    colour = (55, 52, 48)
    frame = [50, 550]
    start = [50, 50]; end = [550, 850]

    # constructor
    def __init__(self, text, font):
        self.text = text
        self.font = font
        self.bl = self.font.getsize(" ")[0]
        self.height = self.font.getsize(" ")[1]

    # writes the text
    def write(self, draw, start, end):
        self.start = start
        words = self.text.split()

        level = 1
        posx = start[0]; posy = start[1]
        hor = []; ver = []

        # find spacing for characters
        for word in words:
            wrdsp = []
            wrdsize = 0
            for char in word:
                ltrsize = self.font.getsize(char)[0]*self.ltrsp
                wrdsp.append(wrdsize)
                wrdsize += ltrsize
            if posx+wrdsize > 550:
                posy += self.lnsp*self.height
                posx = self.frame[0]
                level += 1
            if level > self.lnmax or (posx+wrdsize > end and level == self.lnmax):
                del words[len(ver):]
                words.append("...")
                wrdsp = []
                wrdsize = 0
                for char in "...":
                    ltrsize = self.font.getsize(char)[0] * self.ltrsp
                    wrdsp.append(wrdsize)
                    wrdsize += ltrsize
            hor.append([x + posx for x in wrdsp])
            ver.append(posy)
            posx += wrdsize
            posx += self.bl

        # print words
        for j in range(len(words)):
            for i in range(len(words[j])):
                draw.text((hor[j][i], ver[j]), words[j][i], self.colour, self.font)

        self.end = [posx, posy+self.height]


class Poster:
    # fonts
    title_font = ImageFont.truetype(r'fonts/BarlowSemiCondensed-Bold.ttf', 60)
    year_font = ImageFont.truetype(r'fonts/BarlowCondensed-Thin.ttf', 45)
    label_font = ImageFont.truetype(r'fonts/ArchivoNarrow-Regular.ttf', 18)
    list_font = ImageFont.truetype(r'fonts/BarlowCondensed-Regular.ttf', 22)

    def __init__(self, movie_id):
        # make background
        self.background_colour = (232, 229, 221)
        background = Image.new('RGB', (600, 900), color=self.background_colour)

        ia = imdb.IMDb()
        movie = ia.get_movie(movie_id)
        self.movie = movie
        self.type = self.get_type()

        # storing info
        self.head_info = {
            "title": Text(movie["title"].upper(), self.title_font),
            "year": Text(str(movie["year"]), self.year_font)
        }

        if self.type == 'movie':
            try:
                runtime = str(movie['runtimes'][0]) + " minutes"
            except KeyError:
                runtime = "CAN'T BE FOUND"

            try:
                genre = ", ".join(movie['genres'])
            except KeyError:
                genre = "CAN'T BE FOUND"

            self.addt_information = {
                "running time": runtime,
                "genre": genre,
                "directed by": ", ".join(self.get_maker(movie_id))
            }
        elif self.type == 'series':
            try:
                ia.update(movie, 'episodes')
                episodes = movie.data['episodes']
                num_of_seasons = len(episodes)
                num_of_episodes = 0
                for i in episodes.keys():
                    num_of_episodes += len(episodes[i])

                length_str = str(num_of_seasons)
                length_str += " season, " if num_of_seasons == 1 else " seasons, "
                length_str += str(num_of_episodes)
                length_str += " episode" if num_of_episodes == 1 else " episodes"
            except KeyError:
                length_str = "CAN'T BE FOUND"

            try:
                genres = ", ".join(movie['genres'])
            except KeyError:
                genres = "CAN'T BE FOUND"

            self.addt_information = {
                "length": length_str,
                "genre": genres,
                "created by": ", ".join(self.get_maker(movie_id))
            }
        else:
            try:
                genres = ", ".join(movie['genres'])
            except KeyError:
                genres = "CAN'T BE FOUND"

            self.addt_information = {
                "genre": genres
            }

        cast = []
        cast_list = movie.data['cast']
        del cast_list[10:]
        for person in cast_list:
            cast.append(person['name'])
        self.addt_information.update({"starring": ", ".join(cast)})

        self.image = background
        self.change_image(self.movie['full-size cover url'])
        self.print_info()

    def get_type(self):
        try:
            print(self.movie['director'])
            return 'movie'
            print(self.movie['creator'])
            return 'series'
        except KeyError:
            return "can't find"

    def get_maker(self, movie_id):
        ia = imdb.IMDb()
        movie = ia.get_movie(movie_id)
        if self.type == "movie":
            makers = [x['name'] for x in movie['director']]
        elif self.type == "series":
            makers = [x['name'] for x in movie['creator']]
        return makers

    def change_image(self, url):
        if url != "":
            response = requests.get(url)
            picture = Image.open(BytesIO(response.content))

            if picture.width > picture.height:
                side_dif = (picture.width - picture.height) / 2
                picture_cropped = picture.crop((side_dif, 0, picture.width - side_dif, picture.height))
            else:
                side_dif = (picture.height - picture.width) / 2
                picture_cropped = picture.crop((0, side_dif, picture.width, picture.height - side_dif))

            picture_edited = picture_cropped.resize((500, 500))
            self.image.paste(picture_edited, (50, 50))

    def change_cast(self, custom_cast):
        if custom_cast != "":
            self.addt_information['starring'] = custom_cast
            self.print_info()

    def print_info(self):
        background = Image.new('RGB', (500, 350), color=self.background_colour)
        self.image.paste(background, (50, 550))
        canvas = ImageDraw.Draw(self.image)

        # printing head info
        self.head_info["title"].ltrsp = 0.85
        self.head_info["title"].lnsp = 0.90
        self.head_info["title"].write(canvas, (50, 560), 400)
        self.head_info["year"].write(canvas, (self.head_info["title"].end[0], self.head_info["title"].end[1] - self.head_info["year"].height), 550)

        # printing additional info
        info = Text("".upper(), self.list_font)
        info.end[1] = self.head_info["year"].end[1] + info.height * 0.25
        for section in self.addt_information:
            label = Text(section, self.label_font)
            label.write(canvas, (label.frame[0], info.end[1] + 0.5 * label.height), 525)
            info = Text(self.addt_information[section].upper(), self.list_font)
            info.lnsp = 1.05
            info.write(canvas, (label.end[0] + 3, label.end[1] - info.height), 510)

    def encode_image(self):
        data = io.BytesIO()
        self.image.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue())

        return encoded_img_data


def search_movie(term):
    ia = imdb.IMDb()
    search = ia.search_movie(term)
    del search[6:]
    results = {}
    for j in search:
        i = j.movieID
        results[i] = {}
        results[i]['title'] = j['title']
        try:
            results[i]['year'] = j['year']
        except KeyError:
            results[i]['year'] = ['???']
        results[i]['cover'] = j['full-size cover url']
    return results


