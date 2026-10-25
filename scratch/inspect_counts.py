import ast

with open('myapp/views.py', 'r', encoding='utf-8') as f:
    code = f.read()

tree = ast.parse(code)
funcs = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}

def inspect_dashboard(name):
    if name not in funcs:
        print(f"Function {name} not found!")
        return
    node = funcs[name]
    src = ast.get_source_segment(code, node)
    print(f"==================== {name} (lines {node.lineno} - {node.end_lineno}) ====================")
    # Print lines that define counts or context
    for i, line in enumerate(src.splitlines()):
        if any(k in line for k in ['count', 'context', 'total', 'mothers', 'children', 'records', 'kits', 'vaccin', 'render']):
            print(f"{node.lineno + i:4d}: {line}")
    print("\n")

inspect_dashboard('adminhome')
inspect_dashboard('ashaworker_home')
inspect_dashboard('teacher_home')
inspect_dashboard('userhome')
inspect_dashboard('vaccination_records')
