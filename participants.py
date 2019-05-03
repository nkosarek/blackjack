from card_util import *


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
        self.first_has_been_settled = False
        self.has_made_move = False
        self.has_split = False
        self.on_second_hand = False
        self.second_hand = []
        self.second_hand_value = 0
        self.current_second_bet = 0
        self.second_has_been_settled = False

    def prompt_bet(self):
        while True:
            input_str = raw_input(kBetPrompt.format(self.number))
            if not input_str.isdigit():
                print kBetNonDigitError
                continue
            bet = int(input_str)
            if bet > self.money:
                print kBetNotEnoughMoneyError
            elif bet == 0:
                print kBetZeroError
            else:
                self.current_bet = bet
                return

    def prompt_move(self):
        can_double_down = self._can_double_down()
        can_split = self._can_split()
        if can_double_down and can_split:
            input_prompt = kMovePromptWithBoth.format(self.number)
            error_msg = kMoveErrorWithBoth
        elif can_double_down:
            input_prompt = kMovePromptWithDoubleDown.format(self.number)
            error_msg = kMoveErrorWithDoubleDown
        elif can_split:
            input_prompt = kMovePromptWithSplitPair.format(self.number)
            error_msg = kMoveErrorWithSplitPair
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
            elif can_split and input_str == kSplitPairInput:
                move = kSplitPair
                break
            print error_msg

        self.has_made_move = True
        return move

    def double_down(self):
        self.current_bet *= 2

    def split_pair(self):
        self.has_split = True
        self.current_second_bet = self.current_bet
        card0, card1 = self.hand
        self.hand = []
        self.add_card(card0)
        self.add_card_to_second(card1)

    def move_on_to_second_hand(self):
        self.on_second_hand = True

    def add_card_to_second(self, card):
        self.second_hand.append(card)
        self.second_hand_value = get_highest_valid_hand_value(self.second_hand)

    def settle_up_first(self, payout):
        self.money += payout
        self.current_bet = 0
        self.first_has_been_settled = True

    def settle_up_second(self, payout):
        if not self.has_split:
            return
        self.money += payout
        self.current_second_bet = 0
        self.second_has_been_settled = True

    def has_been_settled(self):
        return self.first_has_been_settled and \
               (not self.has_split or self.second_has_been_settled)

    def clear_hand(self):
        super(Player, self).clear_hand()
        self.first_has_been_settled = False
        self.second_has_been_settled = False
        self.has_made_move = False
        self.has_split = False
        self.on_second_hand = False
        self.second_hand = []
        self.second_hand_value = 0

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

    def _can_split(self):
        if not self.has_made_move and \
                self.current_bet * 2 <= self.money and \
                get_card_rank(self.hand[0]) == get_card_rank(self.hand[1]):
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
