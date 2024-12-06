import cards
import random

def initialize_game():
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


def show_player_hand(player):
    print("\nPlayer's hand:")
    for n, card in enumerate(player):
        print(f"\tSelect {n} for {card}")


def player_turn(player, computer, deck, player_pairs):
    show_player_hand(player)
    choice = input("\nPlease select the number for the card you want from the above list: ")
    choice = int(choice)
    selection = player[choice]
    value = selection.split(" ")[0]

    found_it = False
    for n, card in enumerate(computer):
        if card.startswith(value):
            found_it = n
            break

    if isinstance(found_it, bool):  # Go Fish
        print("\nGo Fish!\n")
        player.append(deck.pop())
        print(f"You drew a {player[-1]}.")
    else:
        print(f"Here is your card from the computer: {computer[n]}.")
        player.append(computer.pop(n))

    # Identify and remove pairs
    player, pairs = cards.identify_remove_pairs(player)
    player_pairs.extend(pairs)

    # Update the score dynamically
    player_score = len(player_pairs) * 10
    computer_score = len(computer_pairs) * 10
    print(f"Your current score: {player_score}")
    print(f"Your pairs: {len(player_pairs)}")

    return player, computer, deck, player_pairs, player_score, computer_score


def computer_turn(player, computer, deck, computer_pairs):
    card = random.choice(computer)
    value = card.split(" ")[0]

    print(f"\nThe computer asks: Do you have a {value}?")
    response = input("Do you have this card? (y/n): ").strip().lower()

    if response == "y":
        for n, card in enumerate(player):
            if card.startswith(value):
                break
        computer.append(player.pop(n))
    else:
        if len(deck) > 0:
            computer.append(deck.pop())
            print("The computer draws a card.")
        else:
            print("The deck is empty!")

    # Identify and remove pairs
    computer, pairs = cards.identify_remove_pairs(computer)
    computer_pairs.extend(pairs)

    # Update the score dynamically
    player_score = len(player_pairs) * 10
    computer_score = len(computer_pairs) * 10
    print(f"The computer's current score: {computer_score}")
    print(f"The computer's pairs: {len(computer_pairs)}")

    return player, computer, deck, computer_pairs, player_score, computer_score


def check_game_over(player, computer, deck, player_pairs, computer_pairs):
    if len(player) == 0:
        print("The Game is over. The player won.")
        return True
    if len(computer) == 0:
        print("The Game is over. The computer won.")
        return True
    if len(deck) == 0:
        print("The deck is empty. Game over.")
        if len(player_pairs) > len(computer_pairs):
            print("The player won.")
        elif len(player_pairs) < len(computer_pairs):
            print("The computer won.")
        else:
            print("It's a draw.")
        return True
    return False

    def update_scores(self):
    """Update scores for both player and computer dynamically."""
    player_score = len(self.player_pairs) * 10
    computer_score = len(self.computer_pairs) * 10

    # Update status with scores
    self.set_status(f"Your score: {player_score} | Computer's score: {computer_score}")


def main():
    deck, player, computer, player_pairs, computer_pairs = initialize_game()

    while True:
        # Player's turn
        player.sort()
        player, computer, deck, player_pairs = player_turn(player, computer, deck, player_pairs)

        # Check if game is over
        if check_game_over(player, computer, deck, player_pairs, computer_pairs):
            break

        # Computer's turn
        player, computer, deck, computer_pairs = computer_turn(player, computer, deck, computer_pairs)

        # Check if game is over
        if check_game_over(player, computer, deck, player_pairs, computer_pairs):
            break


if __name__ == "__main__":
    main()
