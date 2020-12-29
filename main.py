from PIL import Image, ImageFont, ImageDraw
import cgi
import imdb


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


# fonts
title_font = ImageFont.truetype(r'fonts/BarlowSemiCondensed-Bold.ttf', 65)
year_font = ImageFont.truetype(r'fonts/BarlowCondensed-Thin.ttf', 45)
label_font = ImageFont.truetype(r'fonts/ArchivoNarrow-Regular.ttf', 18)
list_font = ImageFont.truetype(r'fonts/BarlowCondensed-Regular.ttf', 22)

# make background
background = Image.new('RGB', (600, 900), color=(232, 229, 221))

ia = imdb.IMDb()

search = ia.search_movie("the great gatsby")
movie = ia.get_movie(search[0].movieID)

# storing info
head_info = {
    "title": Text(movie["title"].upper(), title_font),
    "year": Text(str(movie["year"]), year_font)
}

director = []
directorlist = movie['director']
for i in directorlist:
    director.append(i['name'])

cast = []
castlist = movie.data['cast']
'''
for i in range(len(castlist)):
    print("{0}. {1}".format(i, castlist[i]['name']))
castchoicein = input("\nInput cast choices:")
'''
castchoicein = "11 31 40 12 10 15"
castchoicestr = castchoicein.split()
castchoice = [int(x) for x in castchoicestr]
for i in castchoice:
    cast.append(castlist[i]['name'])

runtime = str(movie['runtimes'][0])+" minutes"

"""
10. Elizabeth Debicki
11. Leonardo DiCaprio
12. Joel Edgerton
31. Tobey Maguire
15. Isla Fisher
40. Carey Mulligan

11 31 40 12 10 15
"""

addt_information = [
    ["running time", runtime],
    ["genre", ", ".join(movie['genres'])],
    ["directed by", ", ".join(director)],
    ["starring", ", ".join(cast)]
]

# find and crop image
picture = Image.open("gatsby.jpg")
if picture.width > picture.height:
    side_dif = (picture.width - picture.height)/2
    picture_cropped = picture.crop((side_dif, 0, picture.width-side_dif, picture.height))
else:
    side_dif = (picture.height - picture.width) / 2
    picture_cropped = picture.crop((0, side_dif, picture.width, picture.height-side_dif))

# print image onto the background
picture_edited = picture_cropped.resize((500, 500))
background.paste(picture_edited, (50, 50))
canvas = ImageDraw.Draw(background)

# printing head info
head_info["title"].ltrsp = 0.85
head_info["title"].lnsp = 0.90
head_info["title"].write(canvas, (50, 560), 400)
head_info["year"].write(canvas, (head_info["title"].end[0], head_info["title"].end[1]-head_info["year"].height), 550)

# printing additional info
info = Text("".upper(), list_font)
info.end[1] = head_info["year"].end[1] + info.height*0.25
for section in addt_information:
    label = Text(section[0], label_font)
    label.write(canvas, (label.frame[0], info.end[1] + 0.5*label.height), 525)
    info = Text(section[1].upper(), list_font)
    info.lnsp = 1.05
    info.write(canvas, (label.end[0]+3, label.end[1]-info.height), 510)

# saves image
background.save(movie['title']+'.jpg')
