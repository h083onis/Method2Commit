from tree_sitter import Language, Parser
import  tree_sitter_java as tsjava

JAVA_LANGUAGE = Language(tsjava.language())
parser = Parser(JAVA_LANGUAGE)

def extract_node_info(node, ast_txt):
    ast_txt += '('+node.type
    if len(node.children) == 0:
        ast_txt += ', '+node.text.decode("utf8", errors='ignore')
    for child in node.children:
        ast_txt = extract_node_info(child, ast_txt)
    ast_txt += ')'
    return ast_txt

def dfs(node, method_list, class_name): # Depth-First Search「深さ優先探索」
    if node.type == 'class_declaration':
        for child in node.children:
            if child.type == 'identifier':
                class_name = child.text.decode("utf8", errors='ignore')
    if node.type == 'method_declaration':
        method_dict = {}
        method_dict['class_name'] = class_name
        method_name = ''
        for child in node.children:
            if child.type == 'identifier' or child.type == 'formal_parameters':
                method_name += child.text.decode("utf8", errors='ignore')
        method_dict['method_name'] = method_name
        method_dict['content'] = node.text.decode("utf8", errors='ignore')
        ast_txt = ''
        method_dict['ast'] = extract_node_info(node, ast_txt)
        method_dict['position'] = [node.start_point, node.end_point]
        method_list.append(method_dict)
        return
    
    [dfs(child, method_list, class_name) for child in node.children]
    
def get_method_list(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    code = bytes(code, "utf8", errors='ignore')
    tree = parser.parse(code)
    method_list = []
    class_name = ''
    dfs(tree.root_node, method_list, class_name)
    return method_list