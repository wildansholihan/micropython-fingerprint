import os

# Disable REPL on serial (USB) connection
try:
    os.remove('/boot.py')
except Exception:
    pass

# Ensure code.py is run on boot
with open('/boot.py', 'w') as f:
    f.write("""
import code

# Automatically run the code.py script
code.run('code.py')
""")
