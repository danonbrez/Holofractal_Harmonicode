"""Pass 220 regression: exact HARMONICODE List-power source identity."""
import unittest
from native_projects.hhs_harmonicode_language.hhs_harmonicode_nested_expression_ast_v2 import parse_source

SOURCE = "List(x,x^2,y,y^4,z,z^2,w,w^4)^List(-List(0,1),List(0,1)-List(List(1,0),(-List(1,0)))/{{0,-1},List(List(-1,1),{{3,2},{-1,0}})},-(List((-List(0,1)),List(0,1)-List(List(1,0),(-List(1,0))))/{{0,-1},List(List(-1,1),{{3,2},{-1,0}})}+List(List(4,1,2,3),List(3,4,1,2),List(2,3,4,1),List(1,2,3,4))))"

class OrderedListPower(unittest.TestCase):
    def test_whole_list_power_preserved(self):
        ast = parse_source(SOURCE)
        self.assertFalse([x for x in ast["diagnostics"] if x["severity"] == "ERROR"])
        nodes = ast["nested_expression_nodes"]
        matches = [n for n in nodes if n["kind"] == "PowerSurface"
                   and n["source_span"]["start"] == 0
                   and n["source_span"]["end"] == len(SOURCE)]
        self.assertEqual(len(matches), 1)
        node = matches[0]
        self.assertEqual(node["operator"], "^")
        self.assertEqual([x["source_text"] for x in node["operands"]],
                         [SOURCE[:SOURCE.index("^List(-List")], SOURCE[SOURCE.index("^List(-List")+1:]])
        self.assertFalse(ast["canonical_admission_authority"])
        self.assertFalse(ast["capabilities"]["general_nested_expression_ast_complete"])

    def test_operand_order_changes_identity(self):
        changed = SOURCE.replace("List(x,x^2,y,y^4", "List(y,y^4,x,x^2", 1)
        self.assertNotEqual(parse_source(SOURCE)["ast_root_hash72"],
                            parse_source(changed)["ast_root_hash72"])

if __name__ == "__main__":
    unittest.main()
