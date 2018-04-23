#include <string>
#include <unordered_map>
#include <vector>

constexpr int NUM_PLAYERS = 4;
constexpr int NUM_SUITS = 5;
constexpr int SUMIT_SUIT = NUM_SUITS - 1;

struct Hand
{
    uint16_t cards[NUM_SUITS] = {0};

    int smallest(int suit) const;
    int highest(int suit) const;
    bool empty() const;
    bool empty(int suit) const;
    int length() const;
    int length(int suit) const;
    bool contains(int suit, int rank) const;
    void add_card(int suit, int rank);
    void remove_card(int suit, int rank);
    void shift_cards_down(int suit, int rank);
    void remove_suit(int suit);
    void keep_only_suit(int suit);
    void remove_adjacents(int suit);

    bool operator ==(const Hand & ts) const;
    bool operator !=(const Hand & ts) const;
    size_t hash_value() const;

    friend std::ostream & operator<<(std::ostream &, const Hand &);
};

struct TrickState
{
    Hand holdings[NUM_PLAYERS];
    Hand legal_moves[NUM_PLAYERS];
    int played[NUM_PLAYERS][2] = {{0}};
    int current_suit = -1;
    int next_to_play = 0;
    int tricks_won = 0;
    int opp_tricks_won = 0;

    void add_spot(int player, int suit);
    void compress();

    bool operator ==(const TrickState & ts) const;

    friend std::ostream & operator<<(std::ostream &, const Hand &);
};

class DDAnalyzer
{
  public:
    DDAnalyzer(const std::string & hand_string);
    DDAnalyzer(const std::string & hand_string, int trump);
    ~DDAnalyzer();
    bool can_make(int target);
    int analyze(int target_guess = 0);
    void play_card(int suit, int rank);
    void give_pitch(int player);

  protected:
    int alpha_beta(int alpha, int beta);
    void compute_legal_moves();
    void undo_play();
    int quick_tricks_on_lead() const;
    int quick_tricks_single_suit(TrickState & ts, int suit) const;

  private:
    int trump = -1;
    int total_tricks = 0;
    int depth = 0;
    int max_depth = 0;
    std::vector<TrickState> trick_states;

    struct TSHasher
    {
        size_t operator()(const TrickState & obj) const;
    };
    typedef std::unordered_map<TrickState, std::pair<int, int>, TSHasher> TTMap;
    TTMap tt;

    struct Stats
    {
        int ab_calls = 0;
    } stats;
};

#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(libdda, m) {
    py::class_<DDAnalyzer>(m, "DDAnalyzer")
        .def(py::init<const std::string &>())
        .def(py::init<const std::string &, int>())
        .def("can_make", &DDAnalyzer::can_make)
        .def("analyze", &DDAnalyzer::analyze, py::arg("target_guess") = 0)
        .def("play_card", &DDAnalyzer::play_card)
        .def("give_pitch", &DDAnalyzer::give_pitch);
}
