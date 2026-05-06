# CoolCompiler - Web Frontend

A modern, real-time web interface for CoolCompiler.

## Features

✨ **Real-Time Execution** — Write code and see results instantly  
🎨 **Beautiful UI** — Clean, modern design with purple gradient theme  
📋 **Sample Programs** — Pre-loaded examples to learn the language  
❌ **Error Display** — Detailed error messages with line and column information  
⌨️ **Keyboard Shortcuts** — Ctrl+Enter to run code  
📱 **Responsive Design** — Works on desktop and tablet devices  
🔍 **Syntax Reference** — Built-in language grammar guide  

## Setup

### 1. Install Flask

```bash
python -m pip install Flask Werkzeug
```

### 2. Start the Web Server

```bash
python app.py
```

The server will start at `http://localhost:5000`

### 3. Open in Browser

Navigate to `http://localhost:5000` in your web browser.

## Usage

1. **Write Code** — Type or paste code in the left editor panel
2. **Run** — Click the "▶ Run" button or press Ctrl+Enter
3. **View Output** — Results appear in the right output panel
4. **Load Samples** — Use the "Load Sample..." dropdown for example programs
5. **Check Errors** — Errors display in a red error box below the output

## File Structure

```
app.py                      ← Flask server
templates/
  └── index.html           ← Main web page
static/
  ├── style.css            ← Styling
  └── script.js            ← Client-side logic
```

## Supported Language Features

| Feature | Syntax | Example |
|---------|--------|---------|
| Variables | `let name = value;` | `let x = 10;` |
| Print | `print(expr);` | `print(x);` |
| Arithmetic | `+`, `-`, `*`, `/` | `x + y` |
| Comparison | `==`, `!=`, `>`, `<`, `>=`, `<=` | `x > 5` |
| Conditions | `if (...) { ... } else { ... }` | `if (x > 0) { print("positive"); }` |
| Loops | `while (...) { ... }` | `while (i < 10) { print(i); }` |
| Boolean Logic | `true`, `false`, `&&`, `||`, `!` | `x > 5 && y < 10` |
| Strings | `"text"` + concatenation | `"Hello" + " World"` |

## Example Programs

### Hello World
```
let greeting = "Hello, World!";
print(greeting);
```

### Arithmetic
```
let a = 10;
let b = 3;
print(a + b);
print(a - b);
print(a * b);
print(a / b);
```

### Conditions
```
let x = 15;
if (x > 10) {
    print("x is greater than 10");
} else {
    print("x is 10 or less");
}
```

### Loop
```
let i = 1;
while (i <= 5) {
    print(i);
    let i = i + 1;
}
```

## API Endpoints

### POST `/api/compile`

Compile and execute code.

**Request:**
```json
{
    "code": "let x = 10; print(x);"
}
```

**Response (Success):**
```json
{
    "success": true,
    "output": ["10"],
    "error": null
}
```

**Response (Error):**
```json
{
    "success": false,
    "output": [],
    "error": "[SemanticError] (line 1, col 7) Use of undeclared variable 'x'"
}
```

### GET `/api/samples`

Get available sample programs.

**Response:**
```json
{
    "hello": {
        "name": "Hello World",
        "code": "let greeting = \"Hello, World!\";\nprint(greeting);"
    },
    ...
}
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Enter | Run code |
| Ctrl+A | Select all (in editor) |

## Troubleshooting

**Port 5000 already in use:**
- Kill the process: `lsof -ti:5000 | xargs kill -9`
- Or modify the port in `app.py` (change `port=5000` to another port)

**Connection refused:**
- Ensure the Flask server is running (`python app.py`)
- Check that you're using the correct URL (`http://localhost:5000`)

**Code doesn't run:**
- Check the error message in the red error box
- Verify syntax matches the Language Syntax Reference
- Ensure all variables are declared before use

## Development Notes

- The web server runs in debug mode for development
- File changes automatically reload the server
- For production, use a proper WSGI server like Gunicorn

## Command Line Alternative

If you prefer the command-line interface:

```bash
python main.py program.txt
python main.py --debug program.txt
```

## License

This project is for educational purposes.
