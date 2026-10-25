import re
import ast

with open('myapp/views.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's inspect functions: add_asha, edit_asha, add_anganwadi, edit_anganwadi, user_registartion, edit_user_profile,
# manage_pregnancy, register_newborn, child_growth_record_view, add_nutrition_kit, add_vaccination, schedule_vaccination

target_funcs = [
    'add_asha', 'edit_asha', 'add_anganwadi', 'edit_anganwadi',
    'user_registartion', 'edit_user_profile', 'manage_pregnancy',
    'register_newborn', 'child_growth_record_view', 'add_nutrition_kit',
    'add_vaccination', 'schedule_vaccination', 'update_kit_status', 'decrease_stock'
]

tree = ast.parse(code)
func_nodes = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}

for name in target_funcs:
    if name in func_nodes:
        fn = func_nodes[name]
        fn_code = ast.get_source_segment(code, fn)
        print(f"=== FUNCTION: {name} (lines {fn.lineno} - {fn.end_lineno}) ===")
        # Extract messages.error or validation if-checks
        errors = re.findall(r'messages\.error\([^,]+,\s*([^\)]+)\)', fn_code)
        print("  Error messages:", errors)
        # Check regex or condition checks
        checks = [line.strip() for line in fn_code.splitlines() if 'if ' in line and ('error' in line or 'not ' in line or 'len(' in line or 'regex' in line or '<' in line or '>' in line)]
        print("  Validation checks sample:", checks[:5])
        print()
