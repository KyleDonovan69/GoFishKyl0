from textual.app import App, ComposeResult
from textual.widgets import Button, Label
from textual.containers import Container, Horizontal, Center
import cards
import random

class GoFishGame(App):
    """A Go Fish game built with Textual for the terminal."""

    def __init__(self):
        super().__init__()
        self.deck, self.player, self.computer, self.player_pairs, self.computer_pairs = self.initialize_game()
        self.card_buttons = []  #Store card buttons for visibility

    def initialize_game(self):
        """Initialize the game with a deck, player hands, and remove initial pairs."""
        deck = cards.build_deck()

        computer = []
        player = []
        player_pairs = []
        computer_pairs = []

        for _ in range(7):
            computer.append(deck.pop())
            player.append(deck.pop())

        player, pairs = cards.identify_remove_pairs(player)
        player_pairs.extend(pairs)
        computer, pairs = cards.identify_remove_pairs(computer)
        computer_pairs.extend(pairs)

        return deck, player, computer, player_pairs, computer_pairs

    def compose(self) -> ComposeResult:
        """Create the interface using Textual components."""
        yield Center(Label("Go Fish - Select a card from your hand"))
        
        #Create all card
        self.card_buttons = [Button(f"{card}", id=f"card-{i}-{card.replace(' ', '-')}", disabled=False) for i, card in enumerate(cards.build_deck())]
        yield Horizontal(*self.card_buttons, id="player-hand")

        #Status label
        yield Center(Label("Status: Waiting for your move", id="status"))

        #Buttons for Yes/No
        yield Horizontal(Button("Yes", id="yes-btn", disabled=True), Button("No", id="no-btn", disabled=True), id="yes-no-container")

        #Button to restart
        yield Button("Play Again", id="play-again-btn", disabled=True)

    def on_mount(self) -> None:
        """Called when the app is mounted; update the player hand here."""
        self.update_player_hand()

    def player_turn(self, card_index: int):
        """Handle player's selection of a card."""
        selection = self.player[card_index]
        value = selection.split(" ")[0]

        found_it = False
        for n, card in enumerate(self.computer):
            if card.startswith(value):
                found_it = n
                break

        if isinstance(found_it, bool):
            self.set_status("Go Fish!")
            if len(self.deck) > 0:
                self.player.append(self.deck.pop())
                self.set_status(f"You drew a {self.player[-1]}.")
            else:
                self.end_game()
                return
        else:
            self.set_status(f"The computer gives you {self.computer[n]}.")
            self.player.append(self.computer.pop(n))

        self.player, pairs = cards.identify_remove_pairs(self.player)
        self.player_pairs.extend(pairs)

        self.update_player_hand()

        #Check if the game is over
        if self.check_game_over():
            return

        self.computer_turn()

    def computer_turn(self):
        """Handle the computer's turn."""
        card = random.choice(self.computer)
        self.value = card.split(" ")[0]

        self.set_status(f"Computer asks: Do you have a {self.value}?")
        #Enable Yes/No buttons
        self.query_one("#yes-btn").disabled = False
        self.query_one("#no-btn").disabled = False

    def yes_response(self):
        """Handle the player's 'Yes' response."""        
        for n, card in enumerate(self.player):
            if card.startswith(self.value):
                break
        self.computer.append(self.player.pop(n))

        self.set_status("The computer took your card.")

        #Disable Yes/No buttons
        self.query_one("#yes-btn").disabled = True
        self.query_one("#no-btn").disabled = True

        self.update_player_hand()

        #Check if the game is over
        if not self.check_game_over():
            self.computer_turn()

    def no_response(self):
        """Handle the player's 'No' response."""
        self.set_status("Go Fish!")
        if len(self.deck) > 0:
            self.computer.append(self.deck.pop())

        #Disable Yes/No buttons
        self.query_one("#yes-btn").disabled = True
        self.query_one("#no-btn").disabled = True

        #Check if the game is over
        if not self.check_game_over():
            self.computer_turn()

    def check_game_over(self):
        """Check if the game is over."""
        if len(self.player) == 0:
            self.set_status("The game is over. You won!")
            self.end_game(winner="Player")
            return True
        elif len(self.computer) == 0:
            self.set_status("The game is over. The computer won!")
            self.end_game(winner="Computer")
            return True
        elif len(self.deck) == 0:
            self.set_status("The game is over. No more cards in the deck.")
            if len(self.player_pairs) > len(self.computer_pairs):
                self.set_status("You have more pairs. You won!")
            elif len(self.player_pairs) < len(self.computer_pairs):
                self.set_status("The computer has more pairs. The computer won!")
            else:
                self.set_status("It's a draw!")
            self.end_game()
            return True
        return False

    def update_scoreboard(self):
    player_score = len(self.player_pairs) * 10
    computer_score = len(self.computer_pairs) * 10
    self.query_one("#scoreboard").update(f"Scoreboard: Player: {player_score}, Computer: {computer_score}")

    def set_status(self, message: str):
        """Update the status label with a new message."""
        self.query_one("#status").update(f"Status: {message}")

    def update_player_hand(self):
        """Update the player's hand of card buttons."""
        hand_container = self.query_one("#player-hand")
        
        #Hide all buttons on start
        for button in self.card_buttons:
            button.visible = False  #Hide buttons
            button.disabled = False  #Disables buttons

        #Show only the buttons for the cards in the player's hand
        for i, card in enumerate(self.player):
            if i < len(self.card_buttons):
                self.card_buttons[i].visible = True
                self.card_buttons[i].label = card
                self.card_buttons[i].disabled = False  #Enable button for clicking

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id

        if button_id.startswith("card-"):
            card_index = int(button_id.split("-")[1])
            self.player_turn(card_index)
        elif button_id == "yes-btn":
            self.yes_response()
        elif button_id == "no-btn":
            self.no_response()
        elif button_id == "play-again-btn":
            self.restart_game()

    def end_game(self, winner=None):
        """End the game and display the result."""
        if winner:
            self.set_status(f"{winner} won!")
        else:
            if len(self.player_pairs) > len(self.computer_pairs):
                self.set_status("The player won!")
            elif len(self.player_pairs) < len(self.computer_pairs):
                self.set_status("The computer won!")
            else:
                self.set_status("It's a draw!")

        #Enable the Play Again
        self.query_one("#play-again-btn").disabled = False

    def restart_game(self):
        """Restart the game by resetting all state and starting a new game."""
        self.deck, self.player, self.computer, self.player_pairs, self.computer_pairs = self.initialize_game()
        self.update_player_hand()
        self.set_status("Game restarted! Select a card to begin.")
        self.query_one("#play-again-btn").disabled = True

#Start the game
if __name__ == "__main__":
    GoFishGame().run()
