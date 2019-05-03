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
#   hide dealer's second card
#   unit tests
###############################################################


class Game:
    def __init__(self):
        self.deck = Deck()
        self.dealer = Dealer()
        self.players = []
        self.curr_player = -1
        self.broke_count = 0
        self.round_delim = ""

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
        print "****** BLACKJACK ******"
        num_players = Game._prompt_num_players()
        for i in xrange(num_players):
            self.players.append(Player(i + 1))

        self.round_delim = "*" * (kPrefixLen + kPlayerWidth * len(self.players))

        while True:
            self._play_round()
            if self.broke_count == len(self.players):
                break
        print kEndGame

    def _play_round(self):
        self._prompt_bets()
        self._deal()

        # Reveal dealer's second card if capable of a natural
        first_dealer_card_value = get_card_value(self.dealer.hand[0])
        if first_dealer_card_value == 1 or \
                first_dealer_card_value == 10:
            self._draw(True)
            self.dealer.reveal_second_card()

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

        first = True
        while left_to_settle_up > 0 and \
                0 <= self.dealer.hand_value < kDealerStandMin:
            if first:
                self.dealer.reveal_second_card()
                self._draw(True)
                first = False
                continue
            self.dealer.add_card(self.deck.get_card())
            self._draw(True)

        self._settle_up()
        self._clear_table()

        if self.deck.should_be_reshuffled:
            self.deck.shuffle()
            print self.round_delim
            print "Reshuffling cards..."
            time.sleep(2)

    def _prompt_bets(self):
        for self.curr_player in xrange(len(self.players)):
            player = self.players[self.curr_player]
            # Player has no money, skip them
            if player.money == 0:
                continue
            self._draw()
            player.prompt_bet()
        self.curr_player = -1

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
        print self.round_delim
        self._draw_dealers_cards()
        print kDealerDelim
        self._draw_players()
        self._draw_arrow()
        if sleep:
            time.sleep(2)

    def _draw_dealers_cards(self):
        value_str = kValuesStr + get_hand_value_str(self.dealer.hand_value)
        if self.dealer.hand_value == 0:
            print value_str
            print kDealerStr
            return

        # Dealer has cards to display
        rows = [kPrefix, kPrefix, kPrefix, kPrefix, value_str, kDealerStr]
        hand_len = len(self.dealer.hand)
        hide_second = not self.dealer.second_card_visible
        for i in xrange(hand_len):
            card = self.dealer.hand[i]
            card_str = get_card_str(card)
            rows[0] += " --"
            if hide_second and i == 1:
                rows[1] += "|  "
            else:
                rows[1] += "|{:<2}".format(card_str)
            rows[2] += "|  "
            rows[3] += " --"
            if i == hand_len - 1:
                rows[0] += "-- "
                rows[1] += "  |"
                if hide_second and i == 1:
                    rows[2] += "  |"
                else:
                    rows[2] += "{:>2}|".format(card_str)
                rows[3] += "-- "

        for row in rows:
            print row

    def _draw_players(self):
        rows = [kPlayersStr, kMoneyStr, kBetStr, kValuesStr]
        num_info_rows = len(rows)
        empty_card_str = " " * (kPlayerWidth / 2)
        for i in xrange(len(self.players)):
            player = self.players[i]

            # Money row
            rows[kMoneyRow] += "${:<13}".format(player.money)
            # Bets row
            rows[kBetRow] += "${:<6}".format(player.current_bet)
            # Card value row
            rows[kValuesRow] += "{:<7}"\
                .format(get_hand_value_str(player.hand_value))
            if player.has_split:
                rows[kBetRow] += "${:<6}".format(player.current_second_bet)
                rows[kValuesRow] += "{:<7}"\
                    .format(get_hand_value_str(player.second_hand_value))
            else:
                rows[kBetRow] += " " * (kPlayerWidth / 2)
                rows[kValuesRow] += " " * (kPlayerWidth / 2)

            num_cards = len(player.hand)
            num_second_cards = len(player.second_hand)
            if num_cards == 0:
                continue

            first_height_required = num_info_rows + kCardHeight + \
                (num_cards - 1) * (kCardHeight / 2)
            second_height_required = num_info_rows + kCardHeight + \
                (num_second_cards - 1) * (kCardHeight / 2)

            if num_cards > num_second_cards:
                height_required = first_height_required
            else:
                height_required = second_height_required
            # Extend the rows if this player has more cards than anyone so far

            for _ in xrange(height_required - len(rows)):
                rows.append(kPrefix + " " * (kPlayerWidth * i))

            # Print cards
            Game._print_hand(rows, player.hand, num_info_rows)

            # Fill out empty rows below this player's cards
            for j in xrange(first_height_required, len(rows)):
                rows[j] += empty_card_str

            # Print out second hand if player split a pair
            if player.has_split:
                Game._print_hand(rows, player.second_hand, num_info_rows)
                # Fill out empty rows below player's second cards
                for j in xrange(second_height_required, len(rows)):
                    rows[j] += empty_card_str
            else:
                # No second hand; fill with empty rows
                for j in xrange(num_info_rows, len(rows)):
                    rows[j] += empty_card_str

        for row in rows:
            print row

    def _draw_arrow(self):
        if 0 <= self.curr_player < len(self.players):
            arrow_loc = kPrefixLen + kPlayerWidth * self.curr_player
            player = self.players[self.curr_player]
            if player.on_second_hand:
                arrow_loc += kPlayerWidth / 2
            if player.hand_value != 0:
                arrow_loc += kArrowPadding
            print " " * arrow_loc + "^"

    @staticmethod
    def _print_hand(rows, hand, num_info_rows):
        num_cards = len(hand)
        for i in xrange(num_cards):
            card_str = get_card_str(hand[i])
            row = (num_cards - i) * kCardHeight / 2 + num_info_rows
            if i == num_cards - 1:
                rows[row - 2] += " ----  "
                rows[row - 1] += "|{:<4}| ".format(card_str)
            rows[row] += "|{:>4}| ".format(card_str)
            rows[row + 1] += " ----  "


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
