import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import re

with open("src/build.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find build function and look for calls
idx = content.find("def build()")
end = content.find("if __name__", idx)
build_func = content[idx:end]
for i, line in enumerate(build_func.split("\n")):
    s = line.strip()
    if "list_page(" in s or "index_page(" in s or "detail_page(" in s:
        print(s[:200])