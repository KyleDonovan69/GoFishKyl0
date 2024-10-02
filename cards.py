import random

faces=("Jack", "Queen","King","Ace")
suits=("Clubs","Spades","Hearts","Diamonds")
nums=(2,3,4,5,6,7,8,9,10)

def buildDeck():
    """ Build and return a shuffled deck of 52 cards."""
    deck=[]
    for suit in suits:
        for value in faces+nums:
            deck.append(f"{value} of {suit}")
    random.shuffle(deck)
    return deck

def cardsDict():
    """
    Return a shuffled dictionary of cards with the keys being the card name and the values being the card's value.
    The values are numeric exept for the aces with returns a list of possible values
    """
    cards={}
    for suit in suits:
        for card in faces+nums:
            if card=="Ace":
                value =[1,11]
            elif card in ["Jack", "Queen","King"]:
                value = 10
            else:
                value=card
            cards[f"{card} of {suit}"]=value
    # The next 3 lines are inspired by StackOverFlow:
    #https://stackoverflow.com/questions/61074422/how-to-shuffle-a-python-dictionary
    cards_list= list(cards.items())
    random.shuffle(cards_list)
    return dict(cards_list)