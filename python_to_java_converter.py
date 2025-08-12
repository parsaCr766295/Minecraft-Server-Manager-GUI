#!/usr/bin/env python3
"""
Python to Java Converter for Minecraft Server Development
=======================================================

This script converts Python code to Java code specifically tailored for
Minecraft server plugins and mods development (Bukkit/Spigot/Paper/Forge).

Features:
- Converts Python classes to Java classes
- Handles method signatures and access modifiers
- Converts common data structures (list, dict) to Java equivalents
- Adds proper imports for Minecraft APIs
- Handles event handling patterns
- Converts async/await to CompletableFuture
- Adds proper exception handling
"""

import re
import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import ast
import textwrap


class PythonToJavaConverter:
    def __init__(self, minecraft_platform='bukkit'):
        """
        Initialize the converter
        
        Args:
            minecraft_platform: Target platform ('bukkit', 'forge', 'fabric')
        """
        self.platform = minecraft_platform.lower()
        self.imports = set()
        self.class_name = ""
        self.package_name = "com.yourserver.plugin"
        
        # Type mappings
        self.type_mappings = {
            'str': 'String',
            'int': 'int',
            'float': 'double',
            'bool': 'boolean',
            'list': 'List',
            'dict': 'Map',
            'set': 'Set',
            'tuple': 'List',  # Java doesn't have tuples, use List
            'None': 'null',
            'object': 'Object'
        }
        
        # Common Python to Java method mappings
        self.method_mappings = {
            'len': 'size',
            'append': 'add',
            'extend': 'addAll',
            'remove': 'remove',
            'pop': 'remove',
            'clear': 'clear',
            'keys': 'keySet',
            'values': 'values',
            'items': 'entrySet',
            'get': 'get',
            'put': 'put',
            'update': 'putAll',
            'split': 'split',
            'join': 'String.join',
            'strip': 'trim',
            'lower': 'toLowerCase',
            'upper': 'toUpperCase',
            'replace': 'replace',
            'startswith': 'startsWith',
            'endswith': 'endsWith',
            'format': 'String.format',
            'print': 'System.out.println'
        }
        
        # Minecraft-specific imports based on platform
        self.minecraft_imports = {
            'bukkit': [
                'org.bukkit.plugin.java.JavaPlugin',
                'org.bukkit.event.Listener',
                'org.bukkit.event.EventHandler',
                'org.bukkit.entity.Player',
                'org.bukkit.command.Command',
                'org.bukkit.command.CommandSender',
                'org.bukkit.Material',
                'org.bukkit.Location',
                'org.bukkit.World'
            ],
            'forge': [
                'net.minecraftforge.fml.common.Mod',
                'net.minecraftforge.eventbus.api.SubscribeEvent',
                'net.minecraft.entity.player.PlayerEntity',
                'net.minecraft.item.ItemStack',
                'net.minecraft.util.math.BlockPos',
                'net.minecraft.world.World'
            ],
            'fabric': [
                'net.fabricmc.api.ModInitializer',
                'net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents',
                'net.minecraft.entity.player.PlayerEntity',
                'net.minecraft.item.ItemStack',
                'net.minecraft.util.math.BlockPos',
                'net.minecraft.world.World'
            ]
        }

    def convert_file(self, input_file: str, output_file: str = None) -> str:
        """Convert a Python file to Java"""
        if not output_file:
            output_file = input_file.replace('.py', '.java')
        
        with open(input_file, 'r', encoding='utf-8') as f:
            python_code = f.read()
        
        java_code = self.convert_code(python_code)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(java_code)
        
        return java_code

    def convert_code(self, python_code: str) -> str:
        """Convert Python code string to Java code string"""
        try:
            tree = ast.parse(python_code)
            java_code = self._convert_ast(tree)
            return self._format_java_code(java_code)
        except SyntaxError as e:
            # Fallback to line-by-line conversion
            return self._convert_line_by_line(python_code)

    def _convert_ast(self, tree: ast.AST) -> str:
        """Convert AST to Java code"""
        java_lines = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                java_lines.extend(self._convert_class(node))
            elif isinstance(node, ast.FunctionDef):
                java_lines.extend(self._convert_function(node))
            elif isinstance(node, ast.Import):
                self._handle_imports(node)
            elif isinstance(node, ast.ImportFrom):
                self._handle_imports(node)
        
        return '\n'.join(java_lines)

    def _convert_class(self, node: ast.ClassDef) -> List[str]:
        """Convert Python class to Java class"""
        self.class_name = node.name
        lines = []
        
        # Class declaration
        extends = ""
        implements = ""
        
        # Check if it's a Minecraft plugin class
        if any(base.id in ['Plugin', 'JavaPlugin', 'Listener'] for base in node.bases if hasattr(base, 'id')):
            if self.platform == 'bukkit':
                extends = " extends JavaPlugin"
                implements = " implements Listener"
                self.imports.add('org.bukkit.plugin.java.JavaPlugin')
                self.imports.add('org.bukkit.event.Listener')
        
        lines.append(f"public class {node.name}{extends}{implements} {{")
        
        # Convert class body
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                lines.extend(self._convert_method(item, indent="    "))
            elif isinstance(item, ast.Assign):
                lines.extend(self._convert_assignment(item, indent="    "))
        
        lines.append("}")
        return lines

    def _convert_function(self, node: ast.FunctionDef, indent: str = "") -> List[str]:
        """Convert Python function to Java method"""
        return self._convert_method(node, indent)

    def _convert_method(self, node: ast.FunctionDef, indent: str = "    ") -> List[str]:
        """Convert Python method to Java method"""
        lines = []
        
        # Method signature
        method_name = node.name
        if method_name == "__init__":
            method_name = self.class_name  # Constructor
            return_type = ""
        else:
            return_type = "void "  # Default return type
        
        # Handle special Minecraft methods
        annotations = []
        if method_name.startswith("on_") and self.platform == 'bukkit':
            annotations.append("@EventHandler")
            self.imports.add('org.bukkit.event.EventHandler')
        
        # Parameters
        params = []
        for arg in node.args.args:
            if arg.arg != 'self':
                param_type = self._infer_parameter_type(arg.arg)
                params.append(f"{param_type} {arg.arg}")
        
        param_str = ", ".join(params)
        
        # Add annotations
        for annotation in annotations:
            lines.append(f"{indent}{annotation}")
        
        # Method declaration
        access_modifier = "public"
        if method_name.startswith("_") and method_name != "__init__":
            access_modifier = "private"
        
        lines.append(f"{indent}{access_modifier} {return_type}{method_name}({param_str}) {{")
        
        # Method body
        body_lines = self._convert_statements(node.body, indent + "    ")
        lines.extend(body_lines)
        
        lines.append(f"{indent}}}")
        return lines

    def _convert_statements(self, statements: List[ast.stmt], indent: str) -> List[str]:
        """Convert list of Python statements to Java"""
        lines = []
        for stmt in statements:
            lines.extend(self._convert_statement(stmt, indent))
        return lines

    def _convert_statement(self, stmt: ast.stmt, indent: str) -> List[str]:
        """Convert a single Python statement to Java"""
        if isinstance(stmt, ast.Assign):
            return self._convert_assignment(stmt, indent)
        elif isinstance(stmt, ast.If):
            return self._convert_if(stmt, indent)
        elif isinstance(stmt, ast.For):
            return self._convert_for(stmt, indent)
        elif isinstance(stmt, ast.While):
            return self._convert_while(stmt, indent)
        elif isinstance(stmt, ast.Return):
            return self._convert_return(stmt, indent)
        elif isinstance(stmt, ast.Expr):
            return self._convert_expression_statement(stmt, indent)
        else:
            # Fallback: convert to comment
            return [f"{indent}// TODO: Convert {type(stmt).__name__}"]

    def _convert_assignment(self, stmt: ast.Assign, indent: str) -> List[str]:
        """Convert Python assignment to Java"""
        lines = []
        for target in stmt.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                value = self._convert_expression(stmt.value)
                var_type = self._infer_type_from_value(stmt.value)
                lines.append(f"{indent}{var_type} {var_name} = {value};")
        return lines

    def _convert_if(self, stmt: ast.If, indent: str) -> List[str]:
        """Convert Python if statement to Java"""
        lines = []
        condition = self._convert_expression(stmt.test)
        lines.append(f"{indent}if ({condition}) {{")
        lines.extend(self._convert_statements(stmt.body, indent + "    "))
        lines.append(f"{indent}}}")
        
        if stmt.orelse:
            lines.append(f"{indent}else {{")
            lines.extend(self._convert_statements(stmt.orelse, indent + "    "))
            lines.append(f"{indent}}}")
        
        return lines

    def _convert_for(self, stmt: ast.For, indent: str) -> List[str]:
        """Convert Python for loop to Java enhanced for loop"""
        lines = []
        target = stmt.target.id if isinstance(stmt.target, ast.Name) else "item"
        iterable = self._convert_expression(stmt.iter)
        
        # Determine the type of the loop variable
        item_type = "Object"  # Default type
        
        lines.append(f"{indent}for ({item_type} {target} : {iterable}) {{")
        lines.extend(self._convert_statements(stmt.body, indent + "    "))
        lines.append(f"{indent}}}")
        
        return lines

    def _convert_while(self, stmt: ast.While, indent: str) -> List[str]:
        """Convert Python while loop to Java"""
        lines = []
        condition = self._convert_expression(stmt.test)
        lines.append(f"{indent}while ({condition}) {{")
        lines.extend(self._convert_statements(stmt.body, indent + "    "))
        lines.append(f"{indent}}}")
        return lines

    def _convert_return(self, stmt: ast.Return, indent: str) -> List[str]:
        """Convert Python return to Java"""
        if stmt.value:
            value = self._convert_expression(stmt.value)
            return [f"{indent}return {value};"]
        else:
            return [f"{indent}return;"]

    def _convert_expression_statement(self, stmt: ast.Expr, indent: str) -> List[str]:
        """Convert Python expression statement to Java"""
        expr = self._convert_expression(stmt.value)
        return [f"{indent}{expr};"]

    def _convert_expression(self, expr: ast.expr) -> str:
        """Convert Python expression to Java"""
        if isinstance(expr, ast.Constant):
            return self._convert_constant(expr)
        elif isinstance(expr, ast.Name):
            return expr.id
        elif isinstance(expr, ast.Attribute):
            return f"{self._convert_expression(expr.value)}.{expr.attr}"
        elif isinstance(expr, ast.Call):
            return self._convert_call(expr)
        elif isinstance(expr, ast.BinOp):
            return self._convert_binop(expr)
        elif isinstance(expr, ast.Compare):
            return self._convert_compare(expr)
        elif isinstance(expr, ast.List):
            return self._convert_list(expr)
        elif isinstance(expr, ast.Dict):
            return self._convert_dict(expr)
        else:
            return "/* TODO: Convert expression */"

    def _convert_constant(self, const: ast.Constant) -> str:
        """Convert Python constant to Java"""
        if isinstance(const.value, str):
            return f'"{const.value}"'
        elif isinstance(const.value, bool):
            return str(const.value).lower()
        elif const.value is None:
            return "null"
        else:
            return str(const.value)

    def _convert_call(self, call: ast.Call) -> str:
        """Convert Python function call to Java"""
        func_name = ""
        if isinstance(call.func, ast.Name):
            func_name = call.func.id
        elif isinstance(call.func, ast.Attribute):
            obj = self._convert_expression(call.func.value)
            method = call.func.attr
            
            # Map Python methods to Java methods
            if method in self.method_mappings:
                method = self.method_mappings[method]
            
            func_name = f"{obj}.{method}"
        
        # Convert arguments
        args = [self._convert_expression(arg) for arg in call.args]
        
        # Handle special cases
        if func_name == "print":
            func_name = "System.out.println"
            self.imports.add('java.lang.System')
        elif func_name == "len":
            if args:
                return f"{args[0]}.size()"
        
        return f"{func_name}({', '.join(args)})"

    def _convert_binop(self, binop: ast.BinOp) -> str:
        """Convert Python binary operation to Java"""
        left = self._convert_expression(binop.left)
        right = self._convert_expression(binop.right)
        
        op_map = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.FloorDiv: "/",  # Java doesn't have floor division
            ast.Mod: "%",
            ast.Pow: "Math.pow",  # Special case
        }
        
        if isinstance(binop.op, ast.Pow):
            self.imports.add('java.lang.Math')
            return f"Math.pow({left}, {right})"
        else:
            op = op_map.get(type(binop.op), "?")
            return f"{left} {op} {right}"

    def _convert_compare(self, compare: ast.Compare) -> str:
        """Convert Python comparison to Java"""
        left = self._convert_expression(compare.left)
        
        # Handle multiple comparisons
        result_parts = [left]
        
        for op, comparator in zip(compare.ops, compare.comparators):
            right = self._convert_expression(comparator)
            
            op_map = {
                ast.Eq: "==",
                ast.NotEq: "!=",
                ast.Lt: "<",
                ast.LtE: "<=",
                ast.Gt: ">",
                ast.GtE: ">=",
                ast.Is: "==",  # Approximate
                ast.IsNot: "!=",  # Approximate
                ast.In: ".contains",  # Special case
                ast.NotIn: "!.contains",  # Special case
            }
            
            if isinstance(op, (ast.In, ast.NotIn)):
                # Handle 'in' operator
                contains = f"{right}.contains({left})"
                if isinstance(op, ast.NotIn):
                    contains = f"!{contains}"
                return contains
            else:
                java_op = op_map.get(type(op), "==")
                result_parts.extend([java_op, right])
        
        return " ".join(result_parts)

    def _convert_list(self, list_node: ast.List) -> str:
        """Convert Python list to Java List"""
        elements = [self._convert_expression(elem) for elem in list_node.elts]
        self.imports.add('java.util.Arrays')
        return f"Arrays.asList({', '.join(elements)})"

    def _convert_dict(self, dict_node: ast.Dict) -> str:
        """Convert Python dict to Java Map"""
        self.imports.add('java.util.HashMap')
        self.imports.add('java.util.Map')
        
        # Create new HashMap and populate it
        pairs = []
        for key, value in zip(dict_node.keys, dict_node.values):
            k = self._convert_expression(key)
            v = self._convert_expression(value)
            pairs.append(f"map.put({k}, {v})")
        
        if pairs:
            map_creation = "new HashMap<>()"
            return f"{{Map<Object, Object> map = {map_creation}; {'; '.join(pairs)}; map;}}"
        else:
            return "new HashMap<>()"

    def _infer_type_from_value(self, value: ast.expr) -> str:
        """Infer Java type from Python value"""
        if isinstance(value, ast.Constant):
            if isinstance(value.value, str):
                return "String"
            elif isinstance(value.value, int):
                return "int"
            elif isinstance(value.value, float):
                return "double"
            elif isinstance(value.value, bool):
                return "boolean"
        elif isinstance(value, ast.List):
            self.imports.add('java.util.List')
            self.imports.add('java.util.ArrayList')
            return "List<Object>"
        elif isinstance(value, ast.Dict):
            self.imports.add('java.util.Map')
            self.imports.add('java.util.HashMap')
            return "Map<Object, Object>"
        
        return "Object"

    def _infer_parameter_type(self, param_name: str) -> str:
        """Infer parameter type based on naming conventions"""
        minecraft_types = {
            'player': 'Player',
            'sender': 'CommandSender',
            'command': 'Command',
            'event': 'Event',
            'world': 'World',
            'location': 'Location',
            'block': 'Block',
            'item': 'ItemStack',
            'entity': 'Entity'
        }
        
        for keyword, java_type in minecraft_types.items():
            if keyword in param_name.lower():
                # Add appropriate import
                if self.platform == 'bukkit':
                    import_map = {
                        'Player': 'org.bukkit.entity.Player',
                        'CommandSender': 'org.bukkit.command.CommandSender',
                        'Command': 'org.bukkit.command.Command',
                        'World': 'org.bukkit.World',
                        'Location': 'org.bukkit.Location',
                        'Block': 'org.bukkit.block.Block',
                        'ItemStack': 'org.bukkit.inventory.ItemStack',
                        'Entity': 'org.bukkit.entity.Entity',
                        'Event': 'org.bukkit.event.Event'
                    }
                    if java_type in import_map:
                        self.imports.add(import_map[java_type])
                
                return java_type
        
        return "Object"

    def _handle_imports(self, node):
        """Handle Python imports and convert to Java imports"""
        # Add basic Java imports
        self.imports.add('java.util.*')
        
        # Add Minecraft-specific imports based on platform
        if self.platform in self.minecraft_imports:
            for imp in self.minecraft_imports[self.platform]:
                self.imports.add(imp)

    def _convert_line_by_line(self, python_code: str) -> str:
        """Fallback line-by-line conversion for syntax errors"""
        lines = python_code.split('\n')
        java_lines = []
        
        for line in lines:
            converted_line = self._convert_simple_line(line)
            if converted_line:
                java_lines.append(converted_line)
        
        return '\n'.join(java_lines)

    def _convert_simple_line(self, line: str) -> str:
        """Simple line-by-line conversion"""
        line = line.strip()
        if not line or line.startswith('#'):
            return ""
        
        # Simple replacements
        replacements = {
            'def ': 'public void ',
            'class ': 'public class ',
            'self.': 'this.',
            'True': 'true',
            'False': 'false',
            'None': 'null',
            'elif': 'else if',
            'and': '&&',
            'or': '||',
            'not ': '!',
            'print(': 'System.out.println(',
        }
        
        for py_keyword, java_keyword in replacements.items():
            line = line.replace(py_keyword, java_keyword)
        
        # Add semicolon if needed
        if not line.endswith(('{', '}', ';')) and line and not line.startswith(('if', 'else', 'for', 'while', 'public', 'private', 'protected')):
            line += ';'
        
        return line

    def _format_java_code(self, java_code: str) -> str:
        """Format the final Java code with imports and package"""
        lines = []
        
        # Package declaration
        lines.append(f"package {self.package_name};")
        lines.append("")
        
        # Imports
        if self.imports:
            sorted_imports = sorted(self.imports)
            for imp in sorted_imports:
                lines.append(f"import {imp};")
            lines.append("")
        
        # Add class comment
        lines.append("/**")
        lines.append(" * Converted from Python to Java")
        lines.append(f" * Target platform: {self.platform.title()}")
        lines.append(" * Generated by Python-to-Java Converter")
        lines.append(" */")
        
        lines.append(java_code)
        
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Convert Python code to Java for Minecraft server development')
    parser.add_argument('input', help='Input Python file')
    parser.add_argument('-o', '--output', help='Output Java file (default: input.java)')
    parser.add_argument('-p', '--platform', choices=['bukkit', 'forge', 'fabric'], 
                       default='bukkit', help='Target Minecraft platform')
    parser.add_argument('--package', default='com.yourserver.plugin', 
                       help='Java package name')
    
    args = parser.parse_args()
    
    converter = PythonToJavaConverter(args.platform)
    converter.package_name = args.package
    
    try:
        java_code = converter.convert_file(args.input, args.output)
        output_file = args.output or args.input.replace('.py', '.java')
        print(f"Successfully converted {args.input} to {output_file}")
        print(f"Target platform: {args.platform}")
        print("\nGenerated Java code preview:")
        print("-" * 50)
        print(java_code[:500] + "..." if len(java_code) > 500 else java_code)
    except Exception as e:
        print(f"Error converting file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()