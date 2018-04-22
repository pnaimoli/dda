#include "dda.h"

#include <iterator>
#include <iostream>
#include <boost/algorithm/string.hpp>
#include <boost/format.hpp>

constexpr char RANK_NAMES[] = "??23456789TJQKA";

int Hand::smallest(int suit) const
{
    if (cards[suit] == 0) return -1;
    else if (cards[suit] & 1    ) return 0;
    else if (cards[suit] & 2    ) return 1;
    else if (cards[suit] & 4    ) return 2;
    else if (cards[suit] & 8    ) return 3;
    else if (cards[suit] & 16   ) return 4;
    else if (cards[suit] & 32   ) return 5;
    else if (cards[suit] & 64   ) return 6;
    else if (cards[suit] & 128  ) return 7;
    else if (cards[suit] & 256  ) return 8;
    else if (cards[suit] & 512  ) return 9;
    else if (cards[suit] & 1024 ) return 10;
    else if (cards[suit] & 2048 ) return 11;
    else if (cards[suit] & 4096 ) return 12;
    else if (cards[suit] & 8192 ) return 13;
    else if (cards[suit] & 16384) return 14;
    else return -1;
}

int Hand::highest(int suit) const
{
    if (cards[suit] == 0) return -1;
    else if (cards[suit] & 16384) return 14;
    else if (cards[suit] & 8192 ) return 13;
    else if (cards[suit] & 4096 ) return 12;
    else if (cards[suit] & 2048 ) return 11;
    else if (cards[suit] & 1024 ) return 10;
    else if (cards[suit] & 512  ) return 9;
    else if (cards[suit] & 256  ) return 8;
    else if (cards[suit] & 128  ) return 7;
    else if (cards[suit] & 64   ) return 6;
    else if (cards[suit] & 32   ) return 5;
    else if (cards[suit] & 16   ) return 4;
    else if (cards[suit] & 8    ) return 3;
    else if (cards[suit] & 4    ) return 2;
    else if (cards[suit] & 2    ) return 1;
    else if (cards[suit] & 1    ) return 0;
    else return -1;
}

bool Hand::empty() const
{
    for (uint16_t suit_set : cards)
        if (suit_set)
            return false;
    return true;
}

bool Hand::empty(int suit) const
{
    return cards[suit] == 0;
}

int Hand::length() const
{
    int num = 0;
    for (int suit = 0; suit < NUM_SUITS; ++suit)
        num += length(suit);
    return num;
}

int Hand::length(int suit) const
{
    int num = 0;
    for (uint16_t tmp = cards[suit]; tmp; tmp >>= 1)
        if (tmp & 1)
            ++num;
    return num;
}

bool Hand::contains(int suit, int rank) const
{
    return cards[suit] & (1 << rank);
}

void Hand::add_card(int suit, int rank)
{
    cards[suit] |= 1 << rank;
}

void Hand::remove_card(int suit, int rank)
{
    cards[suit] &= uint16_t(-1) - (1 << rank);
}

void Hand::shift_cards_down(int suit, int rank)
{
    uint16_t & c = cards[suit];
    if (c < (1 << rank))
        return;
    uint16_t smaller_cards = c & ((1 << rank) - 1);
    uint16_t larger_cards = (c - smaller_cards) >> 1;
    c = larger_cards | smaller_cards;
}

void Hand::remove_suit(int suit)
{
    cards[suit] = 0;
}

void Hand::keep_only_suit(int suit_to_keep)
{
    for (int suit = 0; suit < NUM_SUITS; ++suit)
        if (suit != suit_to_keep)
            cards[suit] = 0;
}

void Hand::remove_adjacents(int suit)
{
    if (cards[suit] == 0)
        return;
    bool in_block = contains(suit, 0);
    for (int rank = 1; rank < 16; ++rank)
    {
        if (!in_block)
        {
            in_block = contains(suit, rank);
            continue;
        }

        in_block = contains(suit, rank);
        if (in_block)
            remove_card(suit, rank);
    }
}

std::ostream & operator<<(std::ostream & os, const Hand & hand)
{
    for (int suit = 0; suit < NUM_SUITS; ++suit)
    {
        if (suit > 0)
            os << ".";
        for (int rank = 0; rank < std::size(RANK_NAMES); ++rank)
        {
            if (!hand.contains(suit, rank))
                continue;
            os << RANK_NAMES[rank];
        }
    }
    return os;
}

std::ostream & operator<<(std::ostream & os, const TrickState & ts)
{
    os << "Hands:";
    for (const Hand & hand : ts.holdings)
        os << " " << hand;
    os << " Legal:";
    for (const Hand & hand : ts.legal_moves)
        os << " " << hand;
    os << " Played:";
    for (auto card : ts.played)
        os << " (" << card[0] << "," << card[1] << ")";
    os << " Suit: " << ts.current_suit;
    os << " To Play: " << ts.next_to_play;
    os << " Tricks Won: (" << ts.tricks_won << "," << ts.opp_tricks_won << ")";
    return os;
}

void TrickState::add_spot(int player, int suit)
{
    Hand all_hands;
    for (const Hand & hand : holdings)
        all_hands.cards[suit] += hand.cards[suit];
    for (int rank = 2; rank < std::size(RANK_NAMES); ++rank)
    {
        if (all_hands.contains(suit, rank))
            continue;
        holdings[player].add_card(suit, rank);
        return;
    }

    throw std::runtime_error("No more space to add a spot card");
}

void TrickState::compress()
{
    for (int suit = 0; suit < NUM_SUITS; ++suit)
    {
        int rank = 2;
        for (int i = 0; i < std::size(RANK_NAMES); ++i)
        {
            bool present = false;
            for (int player = 0; player < NUM_PLAYERS; ++player)
                present |= holdings[player].contains(suit, rank);
            if (present) {
                ++rank;
                continue;
            }
            for (int player = 0; player < NUM_PLAYERS; ++player)
                holdings[player].shift_cards_down(suit, rank);
        }
    }
}

DDAnalyzer::DDAnalyzer(const std::string & hand_string) :
    DDAnalyzer(hand_string, -1)
{
}

DDAnalyzer::DDAnalyzer(const std::string & hand_string, int trump) :
    trump(trump),
    trick_states(1)
{
    // Replace "10" w/ "T"
    std::string new_str = hand_string;
    boost::replace_all(new_str, "10", "T");

    // Split by whitespace
    std::vector<std::string> hands;
    boost::split(hands, new_str, boost::is_space(), boost::token_compress_on);

    if (hands.size() != NUM_PLAYERS)
        throw std::runtime_error("Hand string must contain 4 hands separated "
                                 "by whitespace");

    for (int player = 0; player < hands.size(); ++player)
    {
        // Now split by "."
        std::vector<std::string> suit_holdings;
        boost::split(suit_holdings, hands[player], boost::is_any_of("."));
        for (int suit = 0; suit < suit_holdings.size(); ++suit)
        {
            for (char card : suit_holdings[suit])
            {
                if (card == 'x' || card == 'X')
                {
                    trick_states[0].add_spot(player, suit);
                    continue;
                }
                int rank = (char*)strchr(RANK_NAMES, card) - RANK_NAMES;
                if (rank < 0)
                    throw std::runtime_error((boost::format(
                        "Invalid card (%c) in hand string") % card).str());

                trick_states[0].holdings[player].add_card(suit, rank);
            }
        }
    }

    trick_states[0].compress();
}

DDAnalyzer::~DDAnalyzer()
{
    std::cout << "Stats - ab_calls=" << stats.ab_calls << std::endl;
}

int DDAnalyzer::analyze(int _total_tricks/* = 0*/)
{
    total_tricks = _total_tricks;
    if (total_tricks <= 0) {
        total_tricks = 13;
        for (const Hand & hand : trick_states[0].holdings)
        {
            total_tricks = std::min(total_tricks, hand.length());
        }
    }
    trick_states.resize(total_tricks + 1);
    max_depth = total_tricks * NUM_PLAYERS;
    return alpha_beta(0, total_tricks);
}

int DDAnalyzer::alpha_beta(int alpha, int beta)
{
    stats.ab_calls++;

    const int tsx = depth / NUM_PLAYERS;
    TrickState & ts = trick_states.at(tsx);
    compute_legal_moves();
//    std::cout << std::string(depth, ' ') <<
//        "A:" << alpha << " B:" << beta << " " << ts << std::endl;

    // Terminal state!
    if (depth == max_depth)
        return ts.tricks_won;

    const int side = ts.next_to_play % 2;

    const int tricks_remaining = total_tricks -
                                 (ts.tricks_won + ts.opp_tricks_won);

    int quick_tricks[2] = {0, 0};
    if (ts.current_suit < 0)
    {
        quick_tricks[side] = quick_tricks_on_lead();
        quick_tricks[side] = std::min(tricks_remaining, quick_tricks[side]);
    }

    // I'm not 100% sure about these lines
    beta = std::min(beta, ts.tricks_won + tricks_remaining - quick_tricks[1]);
    alpha = std::max(alpha, ts.tricks_won + quick_tricks[0]);
    if (alpha >= beta)
        return beta;

    // If the leading team is playing, we're trying to maximize the
    // number of tricks
    if (side == 0)
    {
        for (int suit = 0; suit < NUM_SUITS; ++suit)
        {
            while (alpha < beta)
            {
                int rank = ts.legal_moves[ts.next_to_play].highest(suit);
                if (rank < 0)
                    break;
                play_card(suit, rank);
                alpha = std::max(alpha, alpha_beta(alpha, beta));
                undo_play();
            }
        }
        return alpha;
    } else
    {
        for (int suit = 0; suit < NUM_SUITS; ++suit)
        {
            while (alpha < beta)
            {
                int rank = ts.legal_moves[ts.next_to_play].highest(suit);
                if (rank < 0)
                    break;
                play_card(suit, rank);
                beta = std::min(beta, alpha_beta(alpha, beta));
                undo_play();
            }
        }
        return beta;
    }
}

void DDAnalyzer::compute_legal_moves()
{
    const int tsx = depth / NUM_PLAYERS;
    TrickState & ts = trick_states.at(tsx);
    Hand & lm = ts.legal_moves[ts.next_to_play];
    lm = ts.holdings[ts.next_to_play];
    if (ts.current_suit < 0)
    {
        // Cannot lead the Sumit suit!
        lm.remove_suit(SUMIT_SUIT);
        for (int suit = 0; suit < NUM_SUITS; ++suit)
            lm.remove_adjacents(suit);
    } else if (!lm.empty(ts.current_suit))
    {
        // We can follow suit
        lm.keep_only_suit(ts.current_suit);
        lm.remove_adjacents(ts.current_suit);
    } else {
        // We pitch
        for (int suit = 0; suit < NUM_SUITS; ++suit)
            lm.remove_adjacents(suit);
    }
}

void DDAnalyzer::play_card(int suit, int rank)
{
    const int tsx = depth / NUM_PLAYERS;
    TrickState & ts = trick_states.at(tsx);

    if (!ts.holdings[ts.next_to_play].contains(suit, rank))
        throw std::runtime_error((boost::format(
                    "Hand does not contain suit=%d rank=%d") % suit % rank).str());

    ts.holdings[ts.next_to_play].remove_card(suit, rank);
    ts.legal_moves[ts.next_to_play].remove_card(suit, rank);
    ts.played[ts.next_to_play][0] = rank;
    ts.played[ts.next_to_play][1] = suit;
    if (ts.current_suit < 0)
        ts.current_suit = suit;
    ts.next_to_play = (ts.next_to_play + 1) % NUM_PLAYERS;

    if (depth % NUM_PLAYERS == 3)
    {
        int winning_value = -1;
        int winner = -1;

        // Last trick of the round, see who won!
        for (int player = 0; player < NUM_PLAYERS; ++player)
        {
            int value = -1;
            if (trump >= 0 && ts.played[player][1] == trump)
            {
                value = 100+ts.played[player][0];
            } else if (ts.played[player][1] == ts.current_suit) {
                value = ts.played[player][0];
            }
            if (value > winning_value)
            {
                winning_value = value;
                winner = player;
            }
        }

        TrickState & next_ts = trick_states.at(tsx+1);
        for (int player = 0; player < NUM_PLAYERS; ++player)
            next_ts.holdings[player] = ts.holdings[player];
        next_ts.current_suit = -1;
        next_ts.next_to_play = winner;
        if (winner % 2 == 0)
        {
            next_ts.tricks_won = ts.tricks_won + 1;
            next_ts.opp_tricks_won = ts.opp_tricks_won;
        } else
        {
            next_ts.tricks_won = ts.tricks_won;
            next_ts.opp_tricks_won = ts.opp_tricks_won + 1;
        }

        // Compress the board downward.  We start on the highest cards first
        // so we don't double (triple! etc) compress.
        std::array<int, NUM_PLAYERS> idx = {{0, 1, 2, 3}};
        std::sort(idx.rbegin(), idx.rend(),
             [&ts](int i1, int i2)
                 { return ts.played[i1][0] < ts.played[i2][0];});

        for (int played_idx : idx)
        {
            const int rank_to_remove = ts.played[played_idx][0];
            const int suit_to_remove = ts.played[played_idx][1];
            for (int player = 0; player < NUM_PLAYERS; ++player)
            {
                Hand & hand = next_ts.holdings[player];
                hand.shift_cards_down(suit_to_remove, rank_to_remove);
            }
        }
    }

    depth++;
}

void DDAnalyzer::give_pitch(int player)
{
    trick_states[0].add_spot(player, SUMIT_SUIT);
}

void DDAnalyzer::undo_play()
{
    depth--;

    const int tsx = depth / NUM_PLAYERS;
    TrickState & ts = trick_states.at(tsx);

    ts.next_to_play = (ts.next_to_play + 3) % NUM_PLAYERS;
    ts.holdings[ts.next_to_play].add_card(
            ts.played[ts.next_to_play][1],
            ts.played[ts.next_to_play][0]);
    ts.played[ts.next_to_play][0] = ts.played[ts.next_to_play][1] = 0;
    if (depth % NUM_PLAYERS == 0)
        ts.current_suit = -1;
}

int DDAnalyzer::quick_tricks_on_lead() const
{
    const int tsx = depth / NUM_PLAYERS;
    TrickState ts = trick_states.at(tsx);

    int quick_tricks = 0;
    if (trump > 0)
        quick_tricks += quick_tricks_single_suit(ts, trump);

    for (int suit = 0; suit < NUM_SUITS; ++suit)
    {
        // Ignore the Sumit suit and trump, because we've already been there
        if (suit == SUMIT_SUIT || suit == trump)
            continue;

        quick_tricks += quick_tricks_single_suit(ts, suit);
    }

    return quick_tricks;
}

int DDAnalyzer::quick_tricks_single_suit(TrickState & ts, int suit) const
{
    const int us = ts.next_to_play;
    const int lho = (ts.next_to_play + 1) % NUM_PLAYERS;
    const int cho = (ts.next_to_play + 2) % NUM_PLAYERS;
    const int rho = (ts.next_to_play + 3) % NUM_PLAYERS;

    // Suit, Our card, Partner's card
    int quick_trick_moves[26][3] = {{-1,-1,-1}};
    int cur_qt = 0;

    while (true)
    {
        const int opponents_top_card = std::max(
                ts.holdings[lho].highest(suit),
                ts.holdings[rho].highest(suit));

        const bool we_are_shorter = ts.holdings[us].length(suit) <
                                    ts.holdings[cho].length(suit);
        const int shorter_hand = we_are_shorter ? us : cho;
        const int longer_hand = (shorter_hand + 2) % NUM_PLAYERS;

        const int top_card_per_player[] = {ts.holdings[0].highest(suit),
                                           ts.holdings[1].highest(suit),
                                           ts.holdings[2].highest(suit),
                                           ts.holdings[3].highest(suit)
                                           };

        const int smallest_card_per_player[] = {ts.holdings[0].smallest(suit),
                                                ts.holdings[1].smallest(suit),
                                                ts.holdings[2].smallest(suit),
                                                ts.holdings[3].smallest(suit)
                                                };

        int who_plays_high = -1;
        if (top_card_per_player[shorter_hand] > opponents_top_card)
            who_plays_high = shorter_hand;
        else if (top_card_per_player[longer_hand] > opponents_top_card)
            who_plays_high = longer_hand;

        if (who_plays_high == -1)
            break;

        // Can opponents trump?
        if (trump > 0)
        {
            bool can_trump = false;
            for (int opponent : {lho, rho})
            {
                if (top_card_per_player[opponent] >= 0)
                    continue;
                if (ts.holdings[opponent].smallest(trump) >= 0)
                    can_trump = true;
            }
            if (can_trump)
                break;
        }

        if (who_plays_high == us)
        {
            quick_trick_moves[cur_qt][0] = suit;
            quick_trick_moves[cur_qt][1] = top_card_per_player[us];
            quick_trick_moves[cur_qt][2] = smallest_card_per_player[cho];
            ts.holdings[us].remove_card(suit, top_card_per_player[us]);
        } else
        {
            quick_trick_moves[cur_qt][0] = suit;
            quick_trick_moves[cur_qt][1] = smallest_card_per_player[us];
            quick_trick_moves[cur_qt][2] = top_card_per_player[cho];
            ts.holdings[cho].remove_card(suit, top_card_per_player[cho]);
        }

        cur_qt++;

        for (int player = 0; player < NUM_PLAYERS; ++player)
        {
            if (player == who_plays_high)
                continue;
            ts.holdings[player].remove_card(suit, smallest_card_per_player[player]);
        }
    }

    // For now, don't do anything intelligent with entries
    int quick_tricks = 0;
    for (int i = 0; i < cur_qt; ++i)
    {
        if (quick_trick_moves[i][1] >= 0)
            quick_tricks++;
    }

    return quick_tricks;
}
