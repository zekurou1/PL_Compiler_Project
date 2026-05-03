#!/usr/bin/env python3
"""
app.py — Flask web server for the compiler with real-time execution.

Provides a web interface where users can write programs and see output in real-time.
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
            'error': None
        })
    
    try:
        # Stage 1: Lexer
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        # Stage 2: Parser
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Stage 3: Semantic Analysis
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        # Stage 4: Interpreter
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        return jsonify({
            'success': True,
            'output': output,
            'error': None
        })
    
    except CompilerError as exc:
        return jsonify({
            'success': False,
            'output': [],
            'error': str(exc)
        })
    
    except Exception as exc:
        return jsonify({
            'success': False,
            'output': [],
            'error': f'[InternalError] {exc}'
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
