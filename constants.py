kNumCardsInDeck = 52
kNumUniqueRanks = 13
kNumDecks = 6
kNumCardsToDeal = 2
kReshuffleCount = 60

kFaceCardValue = 10
kAceValue = 1
kAltAceValue = 11
kMaxHandValue = 21
kDealerStandMin = 17

kMinNumPlayers = 1
kMaxNumPlayers = 7

kInitPlayerMoney = 1000

kNoMove = -1
kHit = 5
kStand = 6
kDoubleDown = 7
kSplitPair = 8

kHitInput = "h"
kStandInput = "s"
kDoubleDownInput = "d"
kSplitPairInput = "p"

kBetPrompt = "Player {}, place your bet: "
kBetNonDigitError = "Invalid input. Please input an integer"
kBetNotEnoughMoneyError = "Invalid input. You don't have that much money to bet"
kBetZeroError = "You can't bet nothing. Come on"

kMovePrompt = "Player {}, hit or stand? (%s/%s): " % (kHitInput, kStandInput)
kMovePromptWithDoubleDown = "Player {}, hit, stand, or double down? (%s/%s/%s): "\
    % (kHitInput, kStandInput, kDoubleDownInput)
kMovePromptWithSplitPair = "Player {}, hit, stand, or split pair? (%s/%s/%s): "\
    % (kHitInput, kStandInput, kSplitPairInput)
kMovePromptWithBoth = "Player {}, hit, stand, double down, or " \
                      "split pair? (%s/%s/%s/%s): "\
    % (kHitInput, kStandInput, kDoubleDownInput, kSplitPairInput)

kMoveError = "Invalid input. Please type either '{}' or '{}'"\
    .format(kHitInput, kStandInput)
kMoveErrorWithDoubleDown = "Invalid input. Please type '{}', '{}', or '{}'"\
    .format(kHitInput, kStandInput, kDoubleDownInput)
kMoveErrorWithSplitPair = "Invalid input. Please type '{}', '{}', or '{}'"\
    .format(kHitInput, kStandInput, kSplitPairInput)
kMoveErrorWithBoth = "Invalid input. Please type '{}', '{}', '{}', or '{}'"\
    .format(kHitInput, kStandInput, kDoubleDownInput, kSplitPairInput)

kCardHeight = 4
kPrefixLen = 14
kPlayerWidth = 14

kDealerDelim = "-" * (kPlayerWidth * 2)

kPrefix = " " * kPrefixLen

kDealerStr = "Dealer"
kDealerStr += " " * (kPrefixLen - len(kDealerStr))

kPlayersStr = "Players"
kPlayersStr += " " * (kPrefixLen - len(kPlayersStr))
kPlayersRow = 0

kMoneyStr = "Money: "
kMoneyStr = " " * (kPrefixLen - len(kMoneyStr)) + kMoneyStr
kMoneyRow = 1

kBetStr = "Bets: "
kBetStr = " " * (kPrefixLen - len(kBetStr)) + kBetStr
kBetRow = 2

kValuesStr = "Card Value: "
kValuesStr = " " * (kPrefixLen - len(kValuesStr)) + kValuesStr
kValuesRow = 3

kArrowPadding = 2

kEndGame = "Ha ha ha dealer wins! What did you think was going to happen?"
