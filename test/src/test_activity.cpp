#include <fmt/base.h>
#include <stdexcept>

#include <taskflow/taskflow.hpp>
#include <activity_data.hpp>

int main(int argc, char* argv[]) {
    if (argc != 5) {
        throw std::runtime_error("Expected 5 arguments");
    }

    std::string input_file{argv[1]};
    std::string output_file{argv[2]};
    std::string output_file_sorted{argv[3]};
    std::string output_file_par_sorted{argv[4]};

    test::ActivityTable table1;
    {
        fmt::println("reading from input_file = {}", input_file);
        test::ActivityTableCsvReader reader(input_file);
        while (reader.read_batch(table1)) {
            // pass
        }
    }
    fmt::println("table1.size() = {}", table1.size());

    test::ActivityTable table2;
    {
        fmt::println("reading from input_file = {}", input_file);
        test::ActivityTableCsvReader reader(input_file);
        while (reader.read_batch(table2)) {
            // pass
        }
    }
    fmt::println("table.size() = {}", table2.size());

    {
        fmt::println("writing to output_file = {}", output_file);
        test::ActivityTableCsvWriter writer(output_file);
        auto batch = writer.build_batch(table1);
        writer.write_batch(batch);
    }

    auto compare = [](auto a, auto b) {
        return a.lid() < b.lid() || (a.lid() == b.lid() && a.start_time() < b.start_time());
    };

    table1.sort(compare);

    tf::Executor executor;
    table2.par_sort(executor, compare);

    {
        fmt::println("writing to output_file_sorted = {}", output_file_sorted);
        test::ActivityTableCsvWriter writer(output_file_sorted);
        auto batch = writer.build_batch(table1);
        writer.write_batch(batch);
    }

    {
        fmt::println("writing to output_file_par_sorted = {}", output_file_par_sorted);
        test::ActivityTableCsvWriter writer(output_file_par_sorted);
        auto batch = writer.build_batch(table1);
        writer.write_batch(batch);
    }

    return 0;
}
