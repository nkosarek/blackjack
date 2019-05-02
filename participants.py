from constants import *


def get_card_value(card):
    card_rank = card % kNumUniqueRanks
    if card_rank >= 9:
        return kFaceCardValue
    else:
        return card_rank + 1


def get_hand_value(hand):
    hand_value = 0
    num_aces = 0
    for card in hand:
        card_val = get_card_value(card)
        if card_val == kAceValue:
            num_aces += 1
        else:
            hand_value += card_val

    left_to_bust = kMaxHandValue - hand_value
    if left_to_bust < num_aces:
        return -1

    for _ in xrange(num_aces):
        if kMaxHandValue - hand_value - kAltAceValue > num_aces - 1:
            hand_value += kAltAceValue
            num_aces -= 1

    return hand_value + num_aces * kAceValue


class Participant(object):
    def __init__(self):
        self.hand = []
        self.hand_value = 0

    def add_card(self, card):
        self.hand.append(card)
        self.hand_value = get_hand_value(self.hand)
        if self.hand_value < 0:
            return False
        return True

    def clear_hand(self):
        self.hand = []
        self.hand_value = 0


class Player(Participant):
    def __init__(self, number):
        super(Player, self).__init__()
        self.number = number
        self.current_bet = 0
        self.money = kInitPlayerMoney

    def prompt_bet(self):
        while True:
            input_str = raw_input("Player " + str(self.number) +
                                  ", place your bet: ")
            if not input_str.isdigit():
                print "Invalid input. Please input an integer"
                continue
            bet = int(input_str)
            if bet > self.money:
                print "Invalid input. You don't have that much money to bet"
            else:
                self.current_bet = bet
                return

    def prompt_move(self):
        while True:
            input_str = raw_input("Player " + str(self.number) +
                                  ", hit or stand? (h/s): ")
            if input_str == "h":
                return True
            elif input_str == "s":
                return False
            print "Invalid input. Please type either 'h' or 's'"

    def settle_up(self, payout):
        self.money += payout
        self.current_bet = 0


class Dealer(Participant):
    def __init__(self):
        super(Dealer, self).__init__()
        self.second_card_visible = False

    def reveal_second_card(self):
        self.second_card_visible = True
