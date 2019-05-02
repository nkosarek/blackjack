import random
import time

from participants import *

###############################################################
# TODO:
#   how to remove player with no money
#   double down
#   better draw
#   unit tests
###############################################################


class Game:
    def __init__(self):
        self.deck = Deck()
        self.dealer = Dealer()
        self.players = []
        self.curr_player = -1

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
            self._play_round()

    def _play_round(self):
        self._prompt_bets()
        self._deal()

        left_to_settle_up = len(self.players)
        for self.curr_player in xrange(len(self.players)):
            self._draw()

            # If dealer has natural, immediately settle everyone up
            if self.dealer.hand_value == kMaxHandValue:
                break

            player = self.players[self.curr_player]

            # If player has natural, pay 3/2 * bet
            player_has_natural = (player.hand_value == kMaxHandValue)
            if player_has_natural:
                player.settle_up(player.current_bet + player.current_bet/2)
                left_to_settle_up -= 1
                continue

            while player.prompt_move():
                player.add_card(self.deck.get_card())
                # If player busts, settle them up
                if player.hand_value < 0:
                    player.settle_up(-player.current_bet)
                    left_to_settle_up -= 1
                    break
                # If player reaches max value (21), don't prompt more moves
                elif player.hand_value == kMaxHandValue:
                    break
                self._draw()

        self.curr_player = -1
        self._draw(True)

        while left_to_settle_up > 0 and \
                0 <= self.dealer.hand_value < kDealerStandMin:
            self.dealer.add_card(self.deck.get_card())
            self._draw(True)

        self._settle_up()
        self._clear_table()

        if self.deck.should_be_reshuffled:
            self.deck.shuffle()

    def _prompt_bets(self):
        for self.curr_player in xrange(len(self.players)):
            self._draw()
            player = self.players[self.curr_player]
            player.prompt_bet()

    def _deal(self):
        for _ in xrange(kNumCardsToDeal):
            for player in self.players:
                player.add_card(self.deck.get_card())

            self.dealer.add_card(self.deck.get_card())

    def _settle_up(self):
        for player in self.players:
            # Bust/natural should have already been settled
            if player.has_been_settled:
                continue
            # Player beats dealer
            elif self.dealer.hand_value < 0 or \
                    self.dealer.hand_value < player.hand_value:
                player.settle_up(player.current_bet)
            # Dealer beats player
            elif self.dealer.hand_value > player.hand_value:
                player.settle_up(-player.current_bet)
            # Tie
            else:
                player.settle_up(0)

    def _clear_table(self):
        self.dealer.clear_hand()
        for player in self.players:
            player.clear_hand()

    def _draw(self, sleep=False):
        print "*********************************"
        print "Dealer: ", self.dealer.get_hand_value_str()
        value_str = "Players: "
        money_str = " " * len(value_str)
        bet_str = money_str
        arrow_loc = len(value_str) + (6 * self.curr_player)
        for player in self.players:
            value_str += "{:<6}".format(player.get_hand_value_str())
            money_str += "${:<5}".format(player.money)
            bet_str += "${:<5}".format(player.current_bet)
        print value_str
        print money_str
        print bet_str
        if 0 <= self.curr_player < len(self.players):
            print arrow_loc * " " + "^"
        if sleep:
            time.sleep(2)


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
