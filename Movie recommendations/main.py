import tkinter as tk
import urllib.parse
import io
from PIL import Image, ImageTk
from imdb import IMDb
import pandas as pd
import operator
import random
from os import path
from tkinter import ttk
from ttkthemes import ThemedTk
from ML import getSuggestedGeneresFromAgeAndGender

Image_Width, Image_Height = 126, 188
Frame_Width, Frame_Height = (Image_Width + 100), (Image_Height + 50)
FramesList = []
MaxMoviesFrame = 18

UserAge = 19
UserGender = "Male"

GeneresList = [
    'None',
    'Adventure',
    'Animation',
    'Children',
    'Comedy',
    'Fantasy',
    'Romance',
    'Drama',
    'Action',
    'Crime',
    'Thriller',
    'Horror',
    'Mystery',
    'Sci-Fi',
    'War',
    'Musical',
    'IMAX',
    'Western',
    'Film-Noir',
    'Documentary',
]

ia = IMDb()  # Starting IMDB

# Dealing with dataset

movies = pd.read_csv("Dataset/MoviesDataframe.csv")


def getMovieIDifNotAddedBeforeFromList(search):
    for i in movies["imdbId"]:
        if i == int(search):
            return True


def addMovieToDataSet(MovieName):
    global movies
    search = ia.search_movie(MovieName)
    if len(search) != 0:
        search = [movie.movieID for movie in search]
        MovieID = getMovieIDifNotAddedBeforeFromList(search[0])
        if not MovieID:
            MovieData = ia.get_movie(search[0])
            if MovieData["title"] and MovieData["year"] and MovieData["genres"] and MovieData["votes"] and MovieData[
                "rating"] and MovieData["cover url"]:
                Title = MovieData["title"]
                ReleaseYear = MovieData["year"]
                MovieGenres = '|'.join(map(str, MovieData["genres"]))
                TotalVotes = MovieData["votes"]
                Rate = (MovieData["rating"] / 2)

                new_row = {'movieId': "N/A", 'title': Title, 'genres': MovieGenres, 'imdbId': MovieID, 'tmdbId': "N/A",
                           'Release Date': ReleaseYear, 'Rate': Rate, 'Total Votes': TotalVotes}
                movies = movies.append(new_row, ignore_index=True)

                movies.to_csv('Dataset/MoviesDataframe.csv', index=False)
                return Title + "Had been added"
            else:
                return "Movie has missing data"
        else:
            return "Movie Found before at dataset"
    else:
        return "Nothing at database match what you have entered"


def suggestMovies(Genre1, Genre2=None, Genre3=None):
    # 0 counter for how many Genere is this film same the user like
    # 1 Index of movie at dataset
    # 3 Movie Rate
    # 4 Movie total Votes
    # 5 Release Date
    PriorityList = []

    for Index, v in enumerate(movies["genres"]):
        Counter = 0
        if "|" in v:
            for Text in v.split("|"):
                if Genre1 == Text or Genre2 == Text or Genre3 == Text:
                    Counter += 1

        elif Genre1 == v or Genre2 == v or Genre3 == v:
            Counter = 1

        if Counter > 0:
            PriorityList.append([Counter, Index, str(movies["Rate"][Index]), str(movies["Total Votes"][Index]),
                                 movies["Release Date"][Index]])

        # print(v)

    PriorityList = sorted(PriorityList, reverse=True,
                          key=operator.itemgetter(0, 2, 4, 3))  # Prio Counter , Rate ,Relase Date, Votes

    return PriorityList


def isImageWithIDExist(ID):
    return path.exists("Images/" + str(ID) + ".png")


def displayMovies(List):
    Range = len(List) if len(List) < MaxMoviesFrame else MaxMoviesFrame

    for i in range(MaxMoviesFrame):
        FramesList[i][3].set("")
        FramesList[i][1].configure(image=None)
        FramesList[i][1].image = None
        FramesList[i][6] = None
        FramesList[i][2] = None
        FramesList[i][7] = None
        Rate_Label_Var.set("")
        RelaseData_Var.set("")
        Genere_Var.set("")

    for i in range(Range):
        # Dealing with images
        image2 = None
        if isImageWithIDExist(movies["imdbId"][List[i][1]]):
            image2 = ImageTk.PhotoImage(Image.open("Images/" + str(movies["imdbId"][List[i][1]]) + ".png"))
            print(movies["title"][List[i][1]], "Already found at images dataset")
        else:
            try:
                img_url = ia.get_movie(movies["imdbId"][List[i][1]]).data['cover url']
                raw_data = urllib.request.urlopen(img_url).read()
                im = Image.open(io.BytesIO(raw_data))
                im = im.resize((Image_Width, Image_Height), Image.ANTIALIAS)
                im.save("Images/" + str(movies["imdbId"][List[i][1]]) + ".png")
                image2 = ImageTk.PhotoImage(im)
                print(movies["title"][List[i][1]], img_url)
            except:
                image2 = ErrorImage
                print(movies["title"][List[i][1]], "ERROR COULD NOT FINE THE IMAGE LINK")

        FramesList[i][1].configure(image=image2)
        FramesList[i][1].image = image2

        # Dealing with Label
        FramesList[i][3].set(movies["title"][List[i][1]])

        # Rate
        FramesList[i][6] = round(movies["Rate"][List[i][1]], 1)

        # Release Date
        FramesList[i][2] = int(movies["Release Date"][List[i][1]])

        # Movie genres
        FramesList[i][7] = movies["genres"][List[i][1]]


# Check button

def check_button():
    if variable1.get() != "None" or variable2.get() != "None" or variable3.get() != "None":
        List = suggestMovies(variable1.get(), variable2.get(), variable3.get())
        displayMovies(List)


# Check_Button['command'] = check_button


# Entry Search

def getMoviesFromChars(Chars):
    MoviesFromChars = []
    counter = 0
    for Index, v in enumerate(movies["title"]):
        if Chars in v.lower():
            if counter <= MaxMoviesFrame:
                MoviesFromChars.append([None, Index, None, None])
            else:
                break

    return MoviesFromChars


def SearchChange(sv):
    if sv.get() != "":
        List = getMoviesFromChars(sv.get().lower())
        displayMovies(List)


# Enter Frame

def getFrameIndexFromXandY():
    x = window.winfo_pointerx() - window.winfo_rootx()
    y = window.winfo_pointery() - window.winfo_rooty()
    for i in range(MaxMoviesFrame):
        Frame_X, Frame_Y = FramesList[i][4], FramesList[i][5]
        if (Frame_X <= x and x <= (Frame_Width + Frame_X)) and (Frame_Y <= y and y <= (Frame_Height + Frame_Y)):
            return i


# Get Age and gender window

askWindow = ThemedTk(theme="equilux")
askWindow.geometry("320x240")
askWindow.tk.call('wm', 'iconphoto', askWindow._w, tk.PhotoImage(file='Images/Icon.png'))
askWindow.title("User Info Window")
askWindow.resizable(False, False)

# askWindow frame

askWindowFrame = ttk.Frame(askWindow, width=640, height=480)
askWindowFrame.place(x=0, y=0)

# Drop down menu for age and gender

Age_Var_Label = tk.StringVar()
Age_Label = ttk.Label(askWindowFrame, textvariable=Age_Var_Label, foreground="white")
Age_Label.place(x=15, y=12)
Age_Var_Label.set("Age")

Age_Var_Entry = tk.StringVar()
Age_Entry = ttk.Entry(askWindowFrame, width=30, textvariable=Age_Var_Entry, validate="focusout")
Age_Entry.place(x=50, y=10)
Age_Var_Entry.set(19)

GenderList = ["Male", "Female"]

GenderListVariable = tk.StringVar(askWindowFrame)

GenderListDrowDownMenu = ttk.OptionMenu(askWindowFrame, GenderListVariable, GenderList[0], *GenderList)
GenderListDrowDownMenu.place(x=250, y=5)

# Guide

Guide_Var_Label = tk.StringVar()
Guide_Label = ttk.Label(askWindowFrame, textvariable=Guide_Var_Label, foreground="white")
Guide_Label.place(x=15, y=65)
Guide_Var_Label.set('''
    Once you pick your own age and gender the movie 
    recommendation system starts picking movies based 
    on your stats. By default if you didn't set your
    stats the system set your age as 19 and your gender
    as male.
''')


# End button

def FinishUserInfoButton():
    global UserGender, UserAge
    UserGender = GenderListVariable.get()
    if (Age_Entry.get()).isnumeric():
        if int(Age_Entry.get()) >= 0 and int(Age_Entry.get()) >= 100:
            UserAge = Age_Entry.get()

    askWindow.destroy()


Finish_Button = ttk.Button(askWindowFrame, text="Finish", command=FinishUserInfoButton, width=46)
Finish_Button.place(x=10, y=200)

askWindow.mainloop()

# Window

window = ThemedTk(theme="equilux")
window.tk.call('wm', 'iconphoto', window._w, tk.PhotoImage(file='Images/Icon.png'))
window.geometry("1360x788")
window.title("Movie Recommendations")
window.resizable(False, False)

CurrentIndex = None


def EnterFrameFunc(event):
    global CurrentIndex
    Index = getFrameIndexFromXandY()

    if CurrentIndex != None:
        Rate_Label_Var.set("")
        RelaseData_Var.set("")
        Genere_Var.set("")

    if Index != None:
        CurrentIndex = Index
        Rate_Label_Var.set("Rate: " + str(FramesList[Index][6]))
        RelaseData_Var.set("Release Date: " + str(FramesList[Index][2]))
        FramesList[Index][7] = FramesList[Index][7].replace("|", " , ")
        Genere_Var.set("Genres: " + FramesList[Index][7])


UpperFrame = ttk.Frame(window, width=1356, height=55)  # , highlightthickness=1,highlightbackground="black")
UpperFrame.place(x=2, y=0)

# Search


Search_Label_Var = tk.StringVar()
Search_Label = ttk.Label(UpperFrame, textvariable=Search_Label_Var, foreground="white")
Search_Label.place(x=10, y=15)
Search_Label_Var.set("Search")

Search_Var = tk.StringVar()
Search_Entry = ttk.Entry(UpperFrame, width=30, textvariable=Search_Var, validate="focusout", validatecommand=None)
Search_Entry.place(x=50, y=10)
Search_Var.trace("w", lambda name, index, mode, sv=Search_Var: SearchChange(Search_Var))

# Drop down menu

variable1 = tk.StringVar(UpperFrame)

Genere1 = ttk.OptionMenu(UpperFrame, variable1, GeneresList[0], *GeneresList)
Genere1.place(x=1050, y=10)

variable2 = tk.StringVar(UpperFrame)

Genere2 = ttk.OptionMenu(UpperFrame, variable2, GeneresList[0], *GeneresList)
Genere2.place(x=1125, y=10)

variable3 = tk.StringVar(UpperFrame)

Genere3 = ttk.OptionMenu(UpperFrame, variable3, GeneresList[0], *GeneresList)
Genere3.place(x=1200, y=10)

Check_Button = ttk.Button(UpperFrame, text="Check", command=check_button, width=9)
Check_Button.place(x=1275, y=10)




# Frame of each movie

ErrorImage = ImageTk.PhotoImage(Image.open("Images/Error.png"))
for x in range(3):
    for y in range(6):
        # Frame
        Frame = ttk.Frame(window, width=Frame_Width, height=Frame_Height)

        Frame.bind('<Button-1>', EnterFrameFunc)

        Frame.place(x=(y * Frame_Width) + 2, y=(x * Frame_Height) + 54)

        # Image
        Cover = ttk.Label(Frame, image=ErrorImage)
        Cover.place(x=(Frame_Width - Image_Width) / 2, y=0)
        Cover.bind('<Button-1>', EnterFrameFunc)

        # Label
        var = tk.StringVar()
        label = ttk.Label(Frame, textvariable=var, foreground="white", wraplength=150)
        label.place(x=(Frame_Width - Image_Width) / 2, y=Frame_Height - 37)
        var.set("N/A")
        label.bind('<Button-1>', EnterFrameFunc)

        # FrameElement , CoverElement , ReleaseDate, LabelVar , X , Y , Rate , Genres
        FramesList.append([Frame, Cover, None, var, (y * Frame_Width) + 2, (x * Frame_Height) + 54, None, None])

# Movie Data Frame
DownFrame = ttk.Frame(window, width=1356, height=20)
DownFrame.place(x=2, y=768)

Rate_Label_Var = tk.StringVar()
Rate_Label = ttk.Label(DownFrame, textvariable=Rate_Label_Var, foreground="white")
Rate_Label.place(x=10, y=0)
Rate_Label_Var.set("")

RelaseData_Var = tk.StringVar()
RelaseData_Label = ttk.Label(DownFrame, textvariable=RelaseData_Var, foreground="white")
RelaseData_Label.place(x=80, y=0)
RelaseData_Var.set("")

Genere_Var = tk.StringVar()
Genere_Label = ttk.Label(DownFrame, textvariable=Genere_Var, foreground="white")
Genere_Label.place(x=210, y=0)
Genere_Var.set("")

# Creating Random genre to show up on start
List = suggestMovies(getSuggestedGeneresFromAgeAndGender(UserAge,
                                                         UserGender))  # Used machine learning to predict user fav genre from age,gender
displayMovies(List)

# Geting all photos from IMDB
'''for v, i in enumerate(movies["imdbId"]):
    if isImageWithIDExist(i):
        image2 = ImageTk.PhotoImage(Image.open("Images/" + str(i) + ".png"))
        print(movies["title"][v], "Already found at images dataset")
    else:
        try:
            img_url = ia.get_movie(i).data['cover url']
            raw_data = urllib.request.urlopen(img_url).read()
            im = Image.open(io.BytesIO(raw_data))
            im = im.resize((Image_Width, Image_Height), Image.ANTIALIAS)
            im.save("Images/" + str(i) + ".png")
            image2 = ImageTk.PhotoImage(im)
            print(movies["title"][v], img_url)
        except:
            image2 = ErrorImage
            print(movies["title"][v], "ERROR COULD NOT FINE THE IMAGE LINK")'''

window.mainloop()
