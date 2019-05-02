from constants import *


def get_card_value(card):
    card_rank = card % kNumUniqueRanks
    if card_rank >= 9:
        return kFaceCardValue
    else:
        return card_rank + 1


def get_highest_valid_hand_value(hand):
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
        if kMaxHandValue - hand_value - kAltAceValue >= num_aces - 1:
            hand_value += kAltAceValue
            num_aces -= 1

    return hand_value + num_aces * kAceValue


def get_all_valid_hand_values(hand):
    num_aces = 0
    base_hand_value = 0
    for card in hand:
        card_val = get_card_value(card)
        if card_val == kAceValue:
            num_aces += 1
        else:
            base_hand_value += card_val

    hand_values = set()
    hand_values.add(base_hand_value)

    for _ in xrange(num_aces):
        new_hand_values = set()
        for value in hand_values:
            if (value + kAceValue) <= kMaxHandValue:
                new_hand_values.add(value + kAceValue)
            if (value + kAltAceValue) <= kMaxHandValue:
                new_hand_values.add(value + kAltAceValue)
        hand_values = new_hand_values

    return hand_values


class Participant(object):
    def __init__(self):
        self.hand = []
        self.hand_value = 0

    def add_card(self, card):
        self.hand.append(card)
        self.hand_value = get_highest_valid_hand_value(self.hand)

    def clear_hand(self):
        self.hand = []
        self.hand_value = 0

    def get_hand_value_str(self):
        if self.hand_value < 0:
            return "*"
        return str(self.hand_value)


class Player(Participant):
    def __init__(self, number):
        super(Player, self).__init__()
        self.number = number
        self.current_bet = 0
        self.money = kInitPlayerMoney
        self.has_been_settled = False
        self.has_made_move = False

    def prompt_bet(self):
        while True:
            input_str = raw_input(kBetPrompt.format(self.number))
            if not input_str.isdigit():
                print kBetNonDigitError
                continue
            bet = int(input_str)
            if bet > self.money:
                print kBetNotEnoughMoney
            else:
                self.current_bet = bet
                return

    def prompt_move(self):
        can_double_down = self._can_double_down()
        if can_double_down:
            input_prompt = kMovePromptWithDoubleDown.format(self.number)
            error_msg = kMoveErrorWithDoubleDown
        else:
            input_prompt = kMovePrompt.format(self.number)
            error_msg = kMoveError

        move = kNoMove
        while move == kNoMove:
            input_str = raw_input(input_prompt)
            if input_str == kHitInput:
                move = kHit
                break
            elif input_str == kStandInput:
                move = kStand
                break
            elif can_double_down and input_str == kDoubleDownInput:
                move = kDoubleDown
                break
            print error_msg

        self.has_made_move = True
        return move

    def double_down(self):
        self.current_bet *= 2

    def settle_up(self, payout):
        self.money += payout
        self.current_bet = 0
        self.has_been_settled = True

    def clear_hand(self):
        super(Player, self).clear_hand()
        self.has_been_settled = False
        self.has_made_move = False

    def _can_double_down(self):
        if not self.has_made_move and \
                self.current_bet * 2 <= self.money and \
                self._one_hand_value_can_double_down():
            return True
        return False

    def _one_hand_value_can_double_down(self):
        hand_values = get_all_valid_hand_values(self.hand)
        for value in hand_values:
            if 9 <= value <= 11:
                return True
        return False


class Dealer(Participant):
    def __init__(self):
        super(Dealer, self).__init__()
        self.second_card_visible = False

    def reveal_second_card(self):
        self.second_card_visible = True

    def clear_hand(self):
        super(Dealer, self).clear_hand()
        self.second_card_visible = False
