###############################################################
#
# blackjack.py
# Author: Nicholas Kosarek
#
# Rules based on summary here:
#   https://bicyclecards.com/how-to-play/blackjack/
#
###############################################################

import random
import time

from participants import *

###############################################################
# TODO:
#   better draw
#   unit tests
###############################################################


class Game:
    def __init__(self):
        self.deck = Deck()
        self.dealer = Dealer()
        self.players = []
        self.curr_player = -1
        self.broke_count = 0

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
            if self.broke_count == len(self.players):
                break
        print kEndGame

    def _play_round(self):
        self._prompt_bets()
        self._deal()

        left_to_settle_up = len(self.players) - self.broke_count
        for self.curr_player in xrange(len(self.players)):
            player = self.players[self.curr_player]
            # Player has no money, skip them
            if player.money == 0:
                continue

            self._draw()

            # If dealer has natural, immediately settle everyone up
            if self.dealer.hand_value == kMaxHandValue:
                break

            if self._get_player_moves(player):
                left_to_settle_up -= 1

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
            player = self.players[self.curr_player]
            # Player has no money, skip them
            if player.money == 0:
                continue
            self._draw()
            player.prompt_bet()

    def _deal(self):
        for _ in xrange(kNumCardsToDeal):
            for player in self.players:
                # Player has no money, skip them
                if player.money == 0:
                    continue
                player.add_card(self.deck.get_card())

            self.dealer.add_card(self.deck.get_card())

    def _get_player_moves(self, player):
        # If player has natural, pay 3/2 * bet
        player_has_natural = (player.hand_value == kMaxHandValue)
        if player_has_natural:
            player.settle_up(player.current_bet + player.current_bet / 2)
            return True

        settled_up = False
        player_should_move = True
        while player_should_move:
            move = player.prompt_move()
            if move == kHit:
                player.add_card(self.deck.get_card())
                # If player busts, settle them up
                if player.hand_value < 0:
                    player.settle_up_first(-player.current_bet)
                    if player.money == 0:
                        self.broke_count += 1
                    settled_up = True
                    break
                # If player reaches max (21), don't prompt more moves
                elif player.hand_value == kMaxHandValue:
                    break
                self._draw()
            elif move == kDoubleDown:
                player.add_card(self.deck.get_card())
                player.double_down()
                player_should_move = False
            elif move == kSplitPair:
                player.split_pair()
                self._draw()
            else:
                player_should_move = False

        # Allow player to make moves on second hand if they split a pair
        if player.has_split and not self._get_player_split_moves(player):
            return False

        return settled_up

    def _get_player_split_moves(self, player):
        player.move_on_to_second_hand()
        self._draw()
        settled_up = False
        player_should_move = True
        while player_should_move:
            move = player.prompt_move()
            if move == kHit:
                player.add_card_to_second(self.deck.get_card())
                # If player busts, settle them up
                if player.second_hand_value < 0:
                    player.settle_up_second(-player.current_second_bet)
                    if player.money == 0:
                        self.broke_count += 1
                    settled_up = True
                    break
                # If player reaches max (21), don't prompt more moves
                elif player.second_hand_value == kMaxHandValue:
                    break
                self._draw()
            else:
                player_should_move = False
        return settled_up

    def _settle_up(self):
        for player in self.players:
            # Player has no money, skip them
            if player.money == 0:
                continue
            # Bust/natural should have already been settled
            if player.has_been_settled():
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

            if player.money == 0:
                self.broke_count += 1

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
        arrow_loc = len(value_str) + (12 * self.curr_player)
        if self.players[self.curr_player].on_second_hand:
            arrow_loc += 6
        for player in self.players:
            hand_value_str = get_hand_value_str(player.hand_value)
            if player.has_split:
                second_hand_value_str = get_hand_value_str(player.second_hand_value)
                value_str += "{:<6}".format(hand_value_str)
                value_str += "{:<6}".format(second_hand_value_str)
                bet_str += "${:<5}".format(player.current_bet)
                bet_str += "${:<5}".format(player.current_second_bet)
            else:
                value_str += "{:<12}".format(hand_value_str)
                bet_str += "${:<11}".format(player.current_bet)
            money_str += "${:<11}".format(player.money)
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
