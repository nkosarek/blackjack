import random
import time

from participants import *


class Game:
    def __init__(self):
        self.deck = Deck()
        self.dealer = Dealer()
        self.players = []
        self.curr_player = 0

    @staticmethod
    def _prompt_num_players():
        num_players = kMinNumPlayers - 1
        while num_players < kMinNumPlayers or num_players > kMaxNumPlayers:
            input_str = raw_input("How many players?: ")
            if not input_str.isdigit():
                print "Invalid number of players"
                continue

            num_players = int(input_str)
            if num_players < kMinNumPlayers or num_players > kMaxNumPlayers:
                print "Invalid number of players. Must be between",\
                    kMinNumPlayers, "and", kMaxNumPlayers, "inclusive"

        return num_players

    def start(self):
        print "*** BLACKJACK ***"
        num_players = Game._prompt_num_players()
        for i in xrange(num_players):
            self.players.append(Player(i + 1))

        while True:
            self.deal()

            self.curr_player = 0
            self.draw()
            for player in self.players:
                while player.prompt_move():
                    if not player.add_card(self.deck.get_card()):
                        break
                    self.draw()
                self.curr_player += 1
                self.draw()

            while 0 <= self.dealer.hand_value < kDealerStandMin:
                self.dealer.add_card(self.deck.get_card())
                self.draw()
                time.sleep(1)

            self.payout()
            # self.draw()
            time.sleep(2)
            self.clear_table()

            if self.deck.should_be_reshuffled:
                self.deck.shuffle()

    def payout(self):
        print "PAYING OUT"
        time.sleep(2)

    def clear_table(self):
        self.dealer.clear_hand()
        for player in self.players:
            player.clear_hand()

    def deal(self):
        for _ in xrange(kNumCardsToDeal):
            for player in self.players:
                player.add_card(self.deck.get_card())

            self.dealer.add_card(self.deck.get_card())

    def draw(self):
        print "*********************************"
        print "Dealer: ", self.dealer.hand_value
        players_str = "Players: "
        arrow_loc = len(players_str) + (4 * self.curr_player)
        for player in self.players:
            player_val = "*" if player.hand_value < 0 else player.hand_value
            players_str += "{:<4}".format(player_val)
        print players_str
        if self.curr_player < len(self.players):
            print arrow_loc * " " + "^"


class Deck:
    def __init__(self):
        self.cards = range(kNumCardsInDeck * kNumDecks)
        self.should_be_reshuffled = False

    def shuffle(self):
        self.cards = range(kNumCardsInDeck * kNumDecks)

    def get_card(self):
        card_idx = random.randint(0, len(self.cards) - 1)
        card = self.cards.pop(card_idx)
        if len(self.cards) < kReshuffleCount:
            self.should_be_reshuffled = True
        return card


if __name__ == "__main__":
    game = Game()
    game.start()
