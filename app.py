from flask import Flask, render_template, session, flash, redirect, url_for, request
import cards
import random
from DBcm import UseDatabase

db_config = {
    'host': 'localhost',
    'user': 'GoFishUser',
    'password': 'password',
    'database': 'GoFishDB',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}


app = Flask(__name__)
app.secret_key = "fdhghdfjghndfhgdlfgnh'odfahngldafhgjdafngjdfaghldkafngladkfngdfljka"


def reset_state():
    session["deck"] = cards.build_deck()
    session["computer"] = []
    session["player"] = []
    session["player_pairs"] = []
    session["computer_pairs"] = []
    
    for _ in range(7):
        session["computer"].append(session["deck"].pop())
        session["player"].append(session["deck"].pop())

    session["player"], pairs = cards.identify_remove_pairs(session["player"])
    session["player_pairs"].extend(pairs)
    session["computer"], pairs = cards.identify_remove_pairs(session["computer"])
    session["computer_pairs"].extend(pairs)


@app.route("/home")
def home():
    return render_template("menu.html")


@app.route("/startgame")
def start():
    reset_state()  # Reset the game state
    player_pairs = len(session.get("player_pairs", []))
    computer_pairs = len(session.get("computer_pairs", []))

    # Pass pair counts to the template
    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]
    return render_template(
        "startgame.html",
        cards=card_images,
        n_computer=len(session["computer"]),
        player_pairs=player_pairs,
        computer_pairs=computer_pairs
    )


def check_game_over():
    """Check if the game is over and redirect to a game over page if it is."""
    if not session["player"]:
        flash("Game Over! You won!")
        return True
    elif not session["computer"]:
        flash("Game Over! The computer won!")
        return True
    elif not session["deck"]:
        if len(session["player_pairs"]) > len(session["computer_pairs"]):
            flash("Game Over! You have more pairs and won!")
        elif len(session["player_pairs"]) < len(session["computer_pairs"]):
            flash("Game Over! The computer has more pairs and won!")
        else:
            flash("Game Over! It’s a draw!")
        return True
    return False


@app.route("/select/<value>")
def process_card_selection(value):
    """Process player's card selection and handle game logic."""
    found_it = False
    card_to_transfer = None

    # Check if the computer has a card matching the requested value
    for n, card in enumerate(session["computer"]):
        if card.startswith(value):  # Match card by its value
            found_it = True
            card_to_transfer = session["computer"].pop(n)  # Remove card from computer
            break

    if found_it:
        # Computer gives the card to the player
        flash(f"The computer gave you the {card_to_transfer}.")
        session["player"].append(card_to_transfer)
    else:
        # Go Fish logic
        flash("Go Fish!")
        if session["deck"]:  # Check if the deck has cards left
            new_card = session["deck"].pop()
            session["player"].append(new_card)
            flash(f"You drew a {new_card}.")
        else:
            flash("The deck is empty! No more cards to draw.")

    # Identify and remove pairs from the player's hand
    session["player"], pairs = cards.identify_remove_pairs(session["player"])
    session["player_pairs"].extend(pairs)

    # Check if the game is over
    if check_game_over():
        return redirect(url_for("game_over"))

    card = random.choice(session["computer"])
    the_value = card.split(" ")[0]
    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]
    return render_template(
        "pickcard.html",
        title="The computer wants to know",
        value=the_value,
        cards=card_images,
    )


@app.route("/pick/<value>")
def process_the_picked_card(value):
    if value == "0":
        session["computer"].append(session["deck"].pop())
    else:
        for n, card in enumerate(session["player"]):
            if card.startswith(value.title()):
                break
        session["computer"].append(session["player"].pop(n))

    session["computer"], pairs = cards.identify_remove_pairs(session["computer"])
    session["computer_pairs"].extend(pairs)

    player_pairs = len(session.get("player_pairs", []))
    computer_pairs = len(session.get("computer_pairs", []))

    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]
    return render_template(
        "startgame.html",
        cards=card_images,
        n_computer=len(session["computer"]),
        player_pairs=player_pairs,
        computer_pairs=computer_pairs
    )

@app.route("/respond/<response>/<value>")
def respond_to_computer(response, value):
    """Handle the player's response to the computer's card request."""
    if response == "yes":
        # Check if the player has the card
        card_given = None
        for n, card in enumerate(session["player"]):
            if card.startswith(value):
                card_given = session["player"].pop(n)  # Remove from player's hand
                session["computer"].append(card_given)  # Add to computer's hand
                flash(f"You gave the computer your {card_given}.")
                break
        
        if not card_given:
            flash("You don't actually have that card!")
    elif response == "no":
        flash("Go Fish!")
        if session["deck"]:
            drawn_card = session["deck"].pop()
            session["computer"].append(drawn_card)
            flash(f"The computer drew a card.")
        else:
            flash("The deck is empty. No more cards to draw!")

    # Update computer's pairs
    session["computer"], pairs = cards.identify_remove_pairs(session["computer"])
    session["computer_pairs"].extend(pairs)

    # Check if the game is over
    if check_game_over():
        return redirect(url_for("game_over"))

    # Prepare updated cards for the player's view
    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]

    # Render the gameplay template (continue the game)
    return render_template(
        "startgame.html",
        cards=card_images,
        n_computer=len(session["computer"]),
        player_pairs=len(session.get("player_pairs", [])),
        computer_pairs=len(session.get("computer_pairs", []))
    )

@app.route("/gameover")
def game_over():
    player_pairs = len(session.get("player_pairs", []))
    computer_pairs = len(session.get("computer_pairs", []))

    # Scoring
    player_score = player_pairs * 10
    computer_score = computer_pairs * 10

    with UseDatabase(db_config) as db:
        if player_pairs > computer_pairs:
            # Player wins
            winner_id = session.get("player_id")
            winner = session.get("username", "Player")
            flash(f"Congratulations, {winner}! You won!")
        elif player_pairs < computer_pairs:
            # Computer wins: Check if it's already in the database
            db.execute("SELECT id FROM Players WHERE username = 'Computer'")
            result = db.fetchone()
            if not result:
                # Insert computer into Players table
                db.execute("INSERT INTO Players (username) VALUES ('Computer')")
                db.execute("SELECT id FROM Players WHERE username = 'Computer'")
                computer_id = db.fetchone()[0]
            else:
                computer_id = result[0]

            winner_id = computer_id
            winner = "Computer"
            flash("The computer won! Better luck next time!")
        else:
            # It's a draw
            winner_id = None
            winner = "Draw"
            flash("It's a draw! Well played!")

        # Record the game
        db.execute(
            """
            INSERT INTO Games (game_date, winner_id, player_score, computer_score)
            VALUES (CURRENT_TIMESTAMP, %s, %s, %s)
            """,
            (winner_id, player_score, computer_score),
        )

    # Fetch leaderboard data
    with UseDatabase(db_config) as db:
        db.execute(
            """
            SELECT player_name, games_played, total_score, games_won
            FROM Leaderboard
            """
        )
        leaderboard_data = db.fetchall()

    return render_template(
        "gameover.html",
        winner=winner,
        player_pairs=player_pairs,
        computer_pairs=computer_pairs,
        player_score=player_score,
        computer_score=computer_score,
        leaderboard=leaderboard_data,
        enumerate=enumerate,
    )

@app.route("/leaderboard")
def leaderboard():
    # Fetch leaderboard data from the database
    with UseDatabase(db_config) as db:
        db.execute(
            """
            SELECT player_name, games_played, total_score, games_won
            FROM Leaderboard
            """
        )
        leaderboard_data = db.fetchall()

    # Pass `enumerate` to the template context
    return render_template("leaderboard.html", leaderboard=leaderboard_data, enumerate=enumerate)

@app.route("/", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        if not username:
            flash("Username cannot be empty. Please try again.")

        with UseDatabase(db_config) as db:
            db.execute("SELECT id FROM Players WHERE username = %s", (username,))
            result = db.fetchone()
            if result:
                session["player_id"] = result[0]
                session["username"] = username
                flash(f"Welcome back, {username}!")
            else:
                db.execute("INSERT INTO Players (username) VALUES (%s)", (username,))
                db.execute("SELECT id FROM Players WHERE username = %s", (username,))
                new_user = db.fetchone()
                session["player_id"] = new_user[0]
                session["username"] = username
                flash(f"Welcome, {username}! Your account has been created.")
        return redirect(url_for("home"))
    return render_template("auth.html")

if __name__ == "__main__":
    app.run(debug=True)

