#include "dda.h"

DDAnalyzer::DDAnalyzer(const std::string & hand_string) :
    DDAnalyzer(hand_string, -1)
{
}

DDAnalyzer::DDAnalyzer(const std::string & hand_string, int trump) :
    trump(trump)
{
    printf("%s\n", hand_string.c_str());
}

int DDAnalyzer::analyze(int _total_tricks/* = 0*/)
{
    total_tricks = _total_tricks;
    return 0;
}

int alpha_beta(int alpha, int beta, int depth)
{
    return 0;
}
