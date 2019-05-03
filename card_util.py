from constants import *


def get_card_rank(card):
    return card % kNumUniqueRanks


def get_card_value(card):
    card_rank = get_card_rank(card)
    if card_rank >= 9:
        return kFaceCardValue
    else:
        return card_rank + 1


def get_card_str(card):
    card_rank = get_card_rank(card)
    if card_rank == 0:
        return "A"
    elif card_rank == 10:
        return "J"
    elif card_rank == 11:
        return "Q"
    elif card_rank == 12:
        return "K"
    else:
        return card_rank + 1


def get_hand_value_str(hand_value):
    if hand_value < 0:
        return "*"
    return str(hand_value)


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
