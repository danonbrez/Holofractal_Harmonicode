#ifndef HHS_PASS220_I086_ORDERED_BOUNDARY_TREE_V1_HPP
#define HHS_PASS220_I086_ORDERED_BOUNDARY_TREE_V1_HPP
#include "hhs_pass220_i086_universal_constraint_source_v1.hpp"
#include <cstddef>
#include <cstdint>
#include <string_view>
#include <vector>
namespace hhs::lane5::reciprocal_nesting {
struct OrderedBoundaryNode final {
    BoundaryKind kind{};
    std::size_t begin{};
    std::size_t end{};
    std::uint32_t depth{};
    std::int32_t parent{-1};
    std::int32_t paired_group{-1};
};
struct OrderedBoundaryTree final {
    std::vector<OrderedBoundaryNode> nodes;
    bool valid{};
};
// Source-ordered UTF-8 byte spans; no evaluation of native gates or scalars.
inline OrderedBoundaryTree parse_ordered_boundaries(std::string_view source) {
    OrderedBoundaryTree tree{};
    std::vector<std::size_t> stack;
    for (std::size_t i=0; i<source.size(); ++i) {
        const auto parent=stack.empty() ? -1 : static_cast<std::int32_t>(stack.back());
        if(source[i]=='(') {
            const auto index=tree.nodes.size();
            tree.nodes.push_back({BoundaryKind::Open,i,0,
                static_cast<std::uint32_t>(stack.size()),parent,-1});
            stack.push_back(index);
        } else if(source[i]==')') {
            if(stack.empty()) return tree;
            const auto index=stack.back(); stack.pop_back();
            tree.nodes[index].end=i+1;
            tree.nodes[index].paired_group=static_cast<std::int32_t>(index);
        } else if(source[i]=='=') {
            const bool gate=(i+1<source.size() && source[i+1]=='=');
            tree.nodes.push_back({gate?BoundaryKind::Gate:BoundaryKind::Equality,
                i,i+(gate?2U:1U),static_cast<std::uint32_t>(stack.size()),parent,-1});
            if(gate) ++i;
        }
    }
    if(!stack.empty()) return tree;
    tree.valid=true; return tree;
}
inline bool validate_ordered_tree(std::string_view source, const OrderedBoundaryTree& tree) {
    if(!tree.valid) return false;
    std::size_t previous=0; bool first=true;
    for(std::size_t i=0;i<tree.nodes.size();++i) {
        const auto& n=tree.nodes[i];
        if(n.begin>=source.size() || n.end>source.size() || n.end<=n.begin) return false;
        if(!first && n.begin<=previous) return false;
        first=false; previous=n.begin;
        if(n.parent>=0) {
            if(static_cast<std::size_t>(n.parent)>=i) return false;
            const auto& p=tree.nodes[static_cast<std::size_t>(n.parent)];
            if(p.kind!=BoundaryKind::Open || n.begin<=p.begin || n.end>=p.end ||
               n.depth!=p.depth+1) return false;
        } else if(n.depth!=0) return false;
        if(n.kind==BoundaryKind::Open) {
            if(source[n.begin]!='(' || source[n.end-1]!=')') return false;
        } else if(n.kind==BoundaryKind::Gate) {
            if(source.substr(n.begin,2)!="==") return false;
        } else if(n.kind==BoundaryKind::Equality) {
            if(source[n.begin]!='=') return false;
        } else return false;
    }
    return true;
}
} // namespace hhs::lane5::reciprocal_nesting
#endif
