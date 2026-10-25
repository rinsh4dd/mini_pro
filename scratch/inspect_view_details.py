import ast

with open('myapp/views.py', 'r', encoding='utf-8') as f:
    code = f.read()

tree = ast.parse(code)
funcs = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}

def print_fn(name):
    if name in funcs:
        node = funcs[name]
        src = ast.get_source_segment(code, node)
        print(f"==================== {name} ====================")
        lines = src.splitlines()
        for i, l in enumerate(lines[:80]):
            print(f"{i+1:3d}: {l}")
        if len(lines) > 80:
            print(f"... ({len(lines)-80} more lines)")
        print("\n")

print_fn('add_asha')
print_fn('user_registartion')
print_fn('manage_pregnancy')
print_fn('register_newborn')
print_fn('child_growth_record_view')
print_fn('add_nutrition_kit')
