import random
import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQL("sqlite:///finals.db")

# Home page
@app.route("/", methods=["GET", "POST"])
def home():
    # Initialize all error messages
    error_message = None
    if request.method=="POST":
        
        # Retrieve number and categories from form
        number = request.form.get("number")
        categories = request.form.get("categories")
        
        # If number and categories are not provided, change error message
        if number in ["#"] and categories in ["Choose..."]:
            error_message = "Invalid number and category."

        # If number is not provided, change error message
        elif number in ["#"]:
            error_message = "Invalid number."
        
        # If category is not provided, change error message
        elif categories in ["Choose..."]:
            error_message = "Invalid category."
        
        # If both number and category are chosen, continue
        else:
            # Generate a random number between 0 and 10000 for each use
            random_id = random.randrange(10000)
            # Save the random number in a session
            session["random_id"] = random_id
            # Insert the requested number and categories into a table called request
            db.execute("INSERT INTO request (random_id, number, categories) VALUES(:random_id, :number, :categories)",
            random_id=session["random_id"], number=number, categories=categories)
            
            # Go to new page called /generate where the affirmations are generated
            return redirect("/generate")

    # User reached route via GET 
    
    # Get the lists of categories to be displayed as dropdown options
    
    # Count the number of categories in the affirmation table
    id_names_raw = db.execute("SELECT COUNT (DISTINCT id) FROM affirm")
    id_names = id_names_raw[0]["COUNT (DISTINCT id)"]
    
    # Retrieve the names of all the categories
    names = db.execute("SELECT DISTINCT id, name FROM affirm")
    
    return render_template("home.html", error_message=error_message, id_names=id_names, names=names)

# Register a new user
@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()
    
    # Initialize error_message
    error_message = None
    
    # User reached route via POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            error_message = "Must provide username."

        # Ensure password was submitted
        elif not request.form.get("password"):
            error_message = "Must provide password."

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            error_message = "Passwords must match."
            
        # Ensure password has appropriate length
        elif len(request.form.get("password")) < 6:
            error_message = "Password should be six or more characters long"
        
        else:
            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              username=request.form.get("username"))
    
            # Ensure username does not already exist
            if len(rows) == 1:
                error_message = "Username already exists."
            
            # If username and password are fine, continue
            else:
                db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash_password)",
                username=request.form.get("username"), hash_password=generate_password_hash(request.form.get("password")));
    
                # Redirect user to home page
                return redirect("/login")

    # User reached route via GET 
    return render_template("register.html", error_message=error_message)

# Log in a registered user
@app.route("/login", methods=["GET", "POST"])
def login(): 
    # Forget any user_id
    session.clear()
    
    # Initialize the error mesage
    error_message = None

    # User reached route via POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            error_message = "Must provide username."

        # Ensure password was submitted
        elif not request.form.get("password"):
            error_message = "Must provide password."

        else:
            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              username=request.form.get("username"))
    
            # Ensure username exists and password is correct
            if not check_password_hash(rows[0]["hash"], request.form.get("password")):
                error_message = "Invalid username and/or password."
    
            # Remember which user has logged in
            else:
                session["user_id"] = rows[0]["id"]
    
                # Redirect user to journal page
                return redirect("/journal")

    # User reached route via GET
    return render_template("login.html", error_message=error_message)

# Log out a logged in user
@app.route("/logout")
def logout(): 
    # Forget any user_id
    session.clear()
    # Return to homepage
    return redirect("/")
    
@app.route("/generate")
def generate():
    
    # Retrieve the number of affirmation requested for by the user
    numbers_raw = db.execute("SELECT number FROM request WHERE random_id=:random_id", random_id = session["random_id"])
    numbers = numbers_raw[0]["number"]
    
    # Retrieve the categories that the user requested
    categories_raw =db.execute("SELECT categories FROM request WHERE random_id=:random_id", random_id = session["random_id"])
    categories = categories_raw[0]["categories"]
    
    # Count the number of affirmations available for the category requested for by the user
    position_options_raw = db.execute("SELECT COUNT (*) FROM affirm WHERE name=:categories", categories=categories)
    position_options = position_options_raw[0]["COUNT (*)"]
    
    # Generate random numbers from 0 up to the number of affirmations in the requested category
    position = random.randrange(1, position_options)
    
    # List of categories in a particular order
    affirmations_raw = db.execute("SELECT affirmation FROM affirm WHERE name=:categories", categories=categories)
    
    # Create an empty list of affirmations to be displayed
    affirmations = []
    
    # For the number of affrmations requested
    # Append the list randomly
    for number in range(0, numbers):
        affirmations.append(affirmations_raw[random.randrange(1, position_options)]["affirmation"])
    
    return render_template("affirmation.html", numbers=numbers, affirmations=affirmations)

# Write a journal input
@app.route("/write", methods=["GET", "POST"])
@login_required
def write():  
    # Initialize the error message
    error_message = None

    # User reached route via POST
    if request.method=="POST":

        # If there is no journal input, reload /write
        if not request.form.get("journal_input"):
            return redirect("/write")
        
        else:
            journal_input = request.form.get("journal_input")
            
            # Check to see if the journal input already exists
            journal_list = db.execute("SELECT journal_input FROM journal WHERE user_id=:user_id AND journal_input=:journal_input",
            user_id=session["user_id"], journal_input=journal_input)

            # If it does not exist, add to journal
            if len(journal_list) == 0:
                db.execute("INSERT INTO journal (user_id, journal_input) VALUES (:user_id, :journal_input)", 
                user_id = session["user_id"], journal_input=journal_input)
                return redirect("/journal")
            
            # If it does, change error message
            elif len(journal_list) != 0:
                error_message = "You already have this journal input"
           
    # User reached route via GET
    return render_template("write.html", error_message=error_message)
    
# List of journal
@app.route("/journal", methods=["POST", "GET"])
@login_required
def journal(): 
    
    # User reached route via POST
    if request.method == "POST":
        
        # Initialize the flag_journal
        flag_journal = None
        
        # Set a name for the results from the forms
        
        # Favorites is the div to be favorited
        favorites = request.form.get("favorited")

        # Deleted is the div to be deleted
        deleted = request.form.get("deleted")
        
        # Delete_all exists when the delete_all button is clicked
        delete_all = request.form.get("delete_all")
        
        # If delete_all is clicked, delete all journal inputs from the user        
        if delete_all:
            db.execute("DELETE FROM journal WHERE user_id=:user_id", user_id=session["user_id"])

        # If a div is to be deleted, delete the div
        elif deleted:
            journal_list = db.execute("SELECT journal_input FROM journal WHERE user_id=:user_id AND journal_input=:journal_input",
            user_id=session["user_id"], journal_input=deleted)
            
            if len(journal_list) != 0:
                db.execute("DELETE FROM journal WHERE user_id=:user_id AND journal_input=:journal_input", user_id=session["user_id"], journal_input=f'{deleted}')
        
        # If a div is to be favorited, put it in a new table
        elif favorites:
            # Get the date-match of the favorited input
            date_favorite_raw = db.execute("SELECT date FROM journal WHERE user_id=? AND journal_input=? ORDER BY date DESC, time DESC", 
            session["user_id"], f'{favorites}')
            
            date_favorite = date_favorite_raw[0]["date"]
            
            # Get the time-match of the favorited input
            time_favorite_raw = db.execute("SELECT time FROM journal WHERE user_id=? AND journal_input=? ORDER BY date DESC, time DESC", 
            session["user_id"], f'{favorites}')
            
            time_favorite = time_favorite_raw[0]["time"]
    
            # Check if the div to be favorited already exists in the list of favorites 
            favorites_list = db.execute("SELECT * FROM favorites WHERE user_id=:user_id AND favorites=:favorites", 
            user_id=session["user_id"], favorites=favorites)
    
            # If it does not, insert into favorites table
            if len(favorites_list) == 0:
                db.execute("INSERT INTO favorites (user_id, favorites, date, time) VALUES (:user_id, :favorites, :date_favorite, :time_favorite)", 
                user_id=session["user_id"], favorites=favorites, date_favorite=date_favorite, time_favorite=time_favorite)
     
    # User reached route via GET
    # Create a new list
    journal_input=[]
    
    # Check to see of the list of journals exists
    lists = db.execute("SELECT * FROM journal WHERE user_id=:user_id", user_id=session["user_id"])
    
    # If it does, mark the flag as true
    if len(lists) != 0:
        flag_journal = True
    
    # If it doesn't, mark the flag as false
    else:
        flag_journal = False
    
    # User reached route via GET

    # Check the number of journal inputs for the user
    rows_raw = db.execute("SELECT COUNT (*) FROM journal WHERE user_id=:user_id", user_id=session["user_id"])
    rows = rows_raw[0]["COUNT (*)"]
    
    # Get the journal inouts and the date and time of upload
    journal_input_raw = db.execute("SELECT journal_input FROM journal WHERE user_id=:user_id ORDER BY date DESC, time DESC", user_id=session["user_id"])
    date = db.execute("SELECT date FROM journal WHERE user_id=:user_id ORDER BY date DESC, time DESC", user_id=session["user_id"])
    time = db.execute("SELECT time FROM journal WHERE user_id=:user_id ORDER BY date DESC, time DESC", user_id=session["user_id"])
    
    for row in range(rows):
        journal_input.append(journal_input_raw[row]["journal_input"])
    
    return render_template("journal.html", journal_input=journal_input, date=date, time=time, rows=rows, flag_journal=flag_journal)

# Favorites inputs of the user
@app.route("/favorites", methods=["POST", "GET"])
@login_required
def favorites(): 
    
    # Get the lists of favorites of the user
    favorites = db.execute("SELECT favorites FROM favorites WHERE user_id=:user_id", user_id=session["user_id"])
    
    # Check to see that the items in the favorites exist (and have not been deleted) in the journal list
    # Iterate through the index of the favorites
    for lengths in range(len(favorites)):
        favorite = favorites[lengths]["favorites"]

        # Compare each 'favorite' input with the journal input to see if any does not exist
        favorites_list = db.execute("SELECT journal_input FROM journal WHERE user_id=:user_id AND journal_input=:journal_input", 
        user_id=session["user_id"], journal_input=favorite)
            
        # If one does not exist, delete from favorites
        if len(favorites_list) == 0:
            db.execute("DELETE FROM favorites WHERE user_id=:user_id AND favorites=:favorite", user_id=session["user_id"], favorite=favorite)
    
    # Get the new number of favorites, the date and time of upload of the favorites and the favorites
    
    lengths_raw = db.execute("SELECT COUNT (*) FROM favorites WHERE user_id=:user_id", user_id=session["user_id"])
    lengths = lengths_raw[0]["COUNT (*)"]
    
    favorites = db.execute("SELECT favorites FROM favorites WHERE user_id=:user_id ORDER BY date DESC, time DESC", user_id=session["user_id"])

    date = db.execute("SELECT date FROM favorites WHERE user_id=:user_id ORDER BY date DESC, time DESC", user_id=session["user_id"])

    time = db.execute("SELECT time FROM favorites WHERE user_id=:user_id ORDER BY date DESC, time DESC", user_id=session["user_id"])
    
    # If no favorites exist, mark flag as false
    if lengths == 0:
        flag_favorites = False
        
    # If at least one favorite exists, mark flag as true
    else:
        flag_favorites = True
        
    return render_template("favorites.html", favorites=favorites, lengths=lengths, date=date, time=time, flag_favorites=flag_favorites)

# Search through the journal
@app.route("/search", methods=["GET", "POST"])
def search():  
    # Get the item to be searched
    search = request.form.get("search")
    
    # If no search item is inputted, go back to the journal page
    if not request.form.get("search"):
        return redirect("/journal")
    else:
        
        # Get the number of matching rows
        rows_search_raw = db.execute("SELECT COUNT (*) FROM journal WHERE user_id=? AND (journal_input LIKE ? \
        OR date LIKE ?)", session["user_id"], f'%{search}%', f'%{search}%')
        
        rows_search = rows_search_raw[0]["COUNT (*)"]
        
        # Get the matching inputs (and dates), and their date and time of upload
        journal_input_search = db.execute("SELECT journal_input FROM journal WHERE user_id=? AND (journal_input LIKE ? \
        OR date LIKE ?) ORDER BY date DESC, time DESC", session["user_id"], f'%{search}%', f'%{search}%')
        
        date_search = db.execute("SELECT date FROM journal WHERE user_id=? AND (journal_input LIKE ? \
        OR date LIKE ?) ORDER BY date DESC, time DESC", session["user_id"], f'%{search}%', f'%{search}%')
        
        time_search = db.execute("SELECT time FROM journal WHERE user_id=? AND (journal_input LIKE ? \
        OR date LIKE ?) ORDER BY date DESC, time DESC", session["user_id"], f'%{search}%', f'%{search}%')
        
        # If there is no search result, mark flag as false 
        if rows_search == 0:
            flag_search = False
            
        # If there is a search result, mark flag as true 
        else:
            flag_search = True
        
        return render_template("search.html", search=search, journal_input_search=journal_input_search, date_search=date_search, time_search=time_search,
        rows_search=rows_search, flag_search=flag_search)