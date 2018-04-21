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

    if (hands.size() != 4)
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
                    Hand all_hands;
                    for (const Hand & hand : trick_states[0].holdings)
                        all_hands.cards[suit] += hand.cards[suit];
                    for (int rank = 2; rank < std::size(RANK_NAMES); ++rank)
                    {
                        if (all_hands.contains(suit, rank))
                            continue;
                        trick_states[0].holdings[player].add_card(suit, rank);
                        break;
                    }
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
    return alpha_beta(0, total_tricks, 0);
}

int DDAnalyzer::alpha_beta(int alpha, int beta, int depth)
{
    const int tsx = depth / 4;
    TrickState & ts = trick_states.at(tsx);
    compute_legal_moves(depth);
//    std::cout << std::string(depth, ' ') <<
//        "A:" << alpha << " B:" << beta << " " << ts << std::endl;

    // Terminal state!
    if (depth == max_depth)
        return ts.tricks_won;

    // If the leading team is playing, we're trying to maximize the
    // number of tricks
    if (ts.next_to_play % 2 == 0)
    {
        int v = alpha;
        for (int suit = 0; suit < NUM_SUITS; ++suit)
        {
            while (true)
            {
                int rank = ts.legal_moves[ts.next_to_play].smallest(suit);
                if (rank < 0)
                    break;
                play_card(depth, suit, rank);
                v = alpha_beta(alpha, beta, depth+1);
                undo_play(depth);
                alpha = std::max(alpha, v);
                if (alpha == beta)
                {
                    return alpha;
                }
                if (alpha > beta)
                    return beta;
            }
        }
        return alpha;
    } else
    {
        int v = beta;
        for (int suit = 0; suit < NUM_SUITS; ++suit)
        {
            while (true)
            {
                int rank = ts.legal_moves[ts.next_to_play].smallest(suit);
                if (rank < 0)
                    break;
                play_card(depth, suit, rank);
                v = alpha_beta(alpha, beta, depth+1);
                undo_play(depth);
                beta = std::min(beta, v);
                if (alpha == beta)
                {
                    return alpha;
                }
                if (alpha > beta)
                    return beta;
            }
        }
        return beta;
    }
}

void DDAnalyzer::compute_legal_moves(int depth)
{
    const int tsx = depth / 4;
    TrickState & ts = trick_states.at(tsx);
    Hand & lm = ts.legal_moves[ts.next_to_play];
    lm = ts.holdings[ts.next_to_play];
    if (ts.current_suit < 0)
    {
        // Cannot lead the Sumit suit!
        lm.remove_suit(4);
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

void DDAnalyzer::play_card(int depth, int suit, int rank)
{
    const int tsx = depth / 4;
    TrickState & ts = trick_states.at(tsx);

    ts.holdings[ts.next_to_play].remove_card(suit, rank);
    ts.legal_moves[ts.next_to_play].remove_card(suit, rank);
    ts.played[ts.next_to_play][0] = rank;
    ts.played[ts.next_to_play][1] = suit;
    if (ts.current_suit < 0)
        ts.current_suit = suit;
    ts.next_to_play = (ts.next_to_play + 1) % 4;

    if (depth % 4 == 3)
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
        std::array<int, 4> idx = {{0, 1, 2, 3}};
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
}

void DDAnalyzer::undo_play(int depth)
{
    const int tsx = depth / 4;
    TrickState & ts = trick_states.at(tsx);

    ts.next_to_play = (ts.next_to_play + 3) % 4;
    ts.holdings[ts.next_to_play].add_card(
            ts.played[ts.next_to_play][1],
            ts.played[ts.next_to_play][0]);
    ts.played[ts.next_to_play][0] = ts.played[ts.next_to_play][1] = 0;
    if (depth % 4 == 0)
        ts.current_suit = -1;
}
