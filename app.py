#!/usr/bin/env python3
"""
app.py — Flask web server for CoolCompiler with real-time execution.

Provides a web IDE where users can write programs and see output in real-time.
"""

from flask import Flask, render_template, request, jsonify
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from lexer import Lexer
from parser import Parser
from analyzer import SemanticAnalyzer
from interpreter import Interpreter
from error import CompilerError

app = Flask(__name__)


@app.route('/')
def index():
    """Serve the main compiler interface."""
    return render_template('index.html')


@app.route('/api/compile', methods=['POST'])
def compile_code():
    """
    Compile and execute user code.
    
    Expected JSON:
        {
            "code": "let x = 10; print(x);"
        }
    
    Returns JSON:
        {
            "success": true/false,
            "output": [...],
            "error": "error message" (if failed)
        }
    """
    data = request.get_json()
    code = data.get('code', '')
    
    if not code.strip():
        return jsonify({
            'success': True,
            'output': [],
            'error': None,
            'stages': [],
            'tokens_count': 0
        })
    
    stages = []
    try:
        stages = []
        
        # Stage 1: Lexer
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        stages.append({
            'name': 'Lexer',
            'status': 'success',
            'details': f'{len(tokens)} tokens generated'
        })
        
        # Stage 2: Parser
        parser = Parser(tokens)
        ast = parser.parse()
        stages.append({
            'name': 'Parser',
            'status': 'success',
            'details': 'AST built successfully'
        })
        
        # Stage 3: Semantic Analysis
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        stages.append({
            'name': 'Semantic Analysis',
            'status': 'success',
            'details': 'Type checking passed'
        })
        
        # Stage 4: Interpreter
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        stages.append({
            'name': 'Execution',
            'status': 'success',
            'details': f'{len(output)} output lines'
        })
        
        return jsonify({
            'success': True,
            'output': output,
            'error': None,
            'stages': stages,
            'tokens_count': len(tokens)
        })
    
    except CompilerError as exc:
        return jsonify({
            'success': False,
            'output': [],
            'error': str(exc),
            'stages': stages if 'stages' in locals() else [],
            'tokens_count': 0
        })
    
    except Exception as exc:
        return jsonify({
            'success': False,
            'output': [],
            'error': f'[InternalError] {exc}',
            'stages': stages if 'stages' in locals() else [],
            'tokens_count': 0
        })


@app.route('/api/samples', methods=['GET'])
def get_samples():
    """Return available sample programs."""
    samples = {
        'hello': {
            'name': 'Hello World',
            'code': 'let greeting = "Hello, World!";\nprint(greeting);'
        },
        'arithmetic': {
            'name': 'Arithmetic',
            'code': 'let a = 10;\nlet b = 3;\nprint(a + b);\nprint(a - b);\nprint(a * b);\nprint(a / b);'
        },
        'conditions': {
            'name': 'If/Else',
            'code': 'let x = 15;\nif (x > 10) {\n    print("x is greater than 10");\n} else {\n    print("x is 10 or less");\n}'
        },
        'loop': {
            'name': 'While Loop',
            'code': 'let i = 1;\nwhile (i <= 5) {\n    print(i);\n    let i = i + 1;\n}'
        },
        'variables': {
            'name': 'Variables & Strings',
            'code': 'let name = "Alice";\nlet age = 25;\nlet msg = "Hello, " + name + "!";\nprint(msg);\nprint(age);'
        }
    }
    return jsonify(samples)


if __name__ == '__main__':
    print("Starting compiler web server at http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(debug=True, port=5000)
