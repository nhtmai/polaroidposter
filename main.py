from PIL import Image, ImageFont, ImageDraw


class Text:
    ltrsp = 1; lnsp = 1; lnmax = 2
    colour = (55, 52, 48)
    frame = [50, 550]

    def __init__(self, text, font):
        self.text = text
        self.font = font
        self.bl = self.font.getsize(" ")[0]
        self.height = self.font.getsize(" ")[1]

    def write(self, draw, start, end):
        words = self.text.split()

        level = 1; leave = 0
        posx = start[0]; posy = start[1]
        hor = []; ver = []

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

        for j in range(len(words)):
            for i in range(len(words[j])):
                draw.text((hor[j][i], ver[j]), words[j][i], self.colour, self.font)

        return [posx, posy+self.height]


background = Image.new('RGB', (600, 900), color=(232, 229, 221))
movie = Image.open("gatsby.jpg")

title_font = ImageFont.truetype(r'fonts/BarlowSemiCondensed-Bold.ttf', 65)
year_font = ImageFont.truetype(r'fonts/BarlowCondensed-Thin.ttf', 45)
label_font = ImageFont.truetype(r'fonts/ArchivoNarrow-Regular.ttf', 18)
list_font = ImageFont.truetype(r'fonts/BarlowCondensed-Regular.ttf', 22)

if movie.width > movie.height:
    side_dif = (movie.width - movie.height)/2
    movie_cropped = movie.crop((side_dif, 0, movie.width-side_dif, movie.height))
else:
    side_dif = (movie.height - movie.width) / 2
    movie_cropped = movie.crop((0, side_dif, movie.width, movie.height-side_dif))

movie_edited = movie_cropped.resize((500, 500))
background.paste(movie_edited, (50, 50))

canvas = ImageDraw.Draw(background)

main_information = {
    "title": Text("the great gatsby".upper(), title_font),
    "year": Text("2013", year_font)
}

main_information["title"].ltrsp = 0.85
main_information["title"].lnsp = 0.90
pt_coor = main_information["title"].write(canvas, (50, 560), 400)
pt_coor = main_information["year"].write(canvas, (pt_coor[0], pt_coor[1]-main_information["year"].height), 550)
pt_coor[1] += 6

addt_information = [
    ["running time", "143 minutes"],
    ["directed by", "baz luhrmann"],
    ["produced by", "Baz luhrmann, Catherine martin, barrie m. osborne, Lucy Fisher, Catherine Knapman, Douglas Wick"],
    ["starring", "Leonardo DiCaprio, Carey Mulligan, Joel Edgerton, Tobey Maguire, Elizabeth Debicki"]
]
for section in addt_information:
    label = Text(section[0], label_font)
    coor = label.write(canvas, (label.frame[0], pt_coor[1] + 0.5*label.height), 525)
    info = Text(section[1].upper(), list_font)
    info.lnsp = 1.05
    pt_coor.clear()
    pt_coor = info.write(canvas, (coor[0]+3, coor[1]-info.height), 510)

background.save("test.jpg")
