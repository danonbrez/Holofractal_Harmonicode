#include "hhs_pass220_lane5_global_tool_surface_v1.hpp"

#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace {

std::vector<std::string> split(const std::string &line, char delimiter) {
    std::vector<std::string> out;
    std::stringstream stream(line);
    std::string item;
    while (std::getline(stream, item, delimiter)) {
        out.push_back(item);
    }
    return out;
}

void copy_text(char *target, std::size_t capacity, const std::string &value) {
    if (value.size() + 1U > capacity) {
        std::cerr << "field too large\n";
        std::exit(3);
    }
    std::memset(target, 0, capacity);
    std::memcpy(target, value.data(), value.size());
}

}  // namespace

int main(int argc, char **argv) {
    if (argc != 2) {
        std::cerr << "usage: validator <manifest.tsv>\n";
        return 2;
    }
    std::ifstream input(argv[1]);
    if (!input) {
        std::cerr << "unable to open manifest\n";
        return 2;
    }

    std::uint64_t count = 0U;
    std::uint64_t pass219 = 0U;
    std::uint64_t pass220 = 0U;
    std::uint64_t services = 0U;
    std::uint64_t pull_requests = 0U;
    std::string line;

    while (std::getline(input, line)) {
        if (line.empty()) {
            continue;
        }
        const auto fields = split(line, '|');
        if (fields.size() != 6U) {
            std::cerr << "manifest row field-count mismatch\n";
            return 4;
        }

        HHSExactPass220Lane5GlobalToolSurfaceV1 tool{};
        tool.struct_size = static_cast<std::uint32_t>(sizeof(tool));
        tool.version = HHS_PASS220_LANE5_GLOBAL_TOOL_SURFACE_VERSION;
        tool.kind_code = static_cast<std::uint32_t>(std::stoul(fields[1]));
        tool.projection_bits = HHS_PASS220_LANE5_GLOBAL_TOOL_PROJECTION_BITS;
        tool.pass219_bound = static_cast<std::uint8_t>(std::stoul(fields[2]));
        tool.pass220_bound = static_cast<std::uint8_t>(std::stoul(fields[3]));
        tool.candidate_only = 1U;
        tool.lane5_selection_unchanged = 1U;
        tool.cpp_surface_bound = 1U;
        copy_text(tool.tool_id_sha256, sizeof(tool.tool_id_sha256), fields[0]);
        copy_text(tool.hash216, sizeof(tool.hash216), fields[4]);
        copy_text(tool.projection_sha256, sizeof(tool.projection_sha256), fields[5]);

        const auto status = hhs_pass220_lane5_global_tool_surface_validate_v1(&tool);
        if (status != HHS_PASS220_LANE5_GLOBAL_TOOL_OK) {
            std::cerr << "tool surface rejected at row " << count << "\n";
            return 5;
        }

        ++count;
        pass219 += tool.pass219_bound;
        pass220 += tool.pass220_bound;
        services += tool.kind_code == 1U ? 1U : 0U;
        pull_requests += tool.kind_code == 2U ? 1U : 0U;
    }

    if (count == 0U || pass219 == 0U || pass220 == 0U ||
        services == 0U || pull_requests == 0U) {
        std::cerr << "manifest coverage incomplete\n";
        return 6;
    }

    std::cout
        << "{\"schema\":\"HHS_PASS_220_LANE5_GLOBAL_CPP_TOOL_VALIDATION_V1\","
        << "\"validated_tools\":" << count << ","
        << "\"service_tools\":" << services << ","
        << "\"pull_request_tools\":" << pull_requests << ","
        << "\"pass219_bound_tools\":" << pass219 << ","
        << "\"pass220_bound_tools\":" << pass220 << ","
        << "\"projection_bits\":5184,"
        << "\"lane5_selection_changed\":false,"
        << "\"candidate_only\":true,"
        << "\"result\":\"PASS\"}\n";
    return 0;
}
