#include <string>

class DDAnalyzer
{
  public:
    DDAnalyzer(const std::string & hand_string, int trump);
    int analyze(int total_tricks = 0);

  protected:
    int alpha_beta(int alpha, int beta, int depth);

  private:
    int total_tricks;
    int max_depth;
};

#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(example, m) {
    py::class_<DDAnalyzer>(m, "DDAnalyzer")
        .def(py::init<const std::string &, int>())
        .def("analyze", &DDAnalyzer::analyze);
}
