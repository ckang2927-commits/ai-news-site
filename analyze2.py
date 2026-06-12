import re

with open("src/build.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find list_page
start = content.find("def list_page(")
end = content.find("def ", start + 10)
func = content[start:end]
print(func[:500])
print("...")
# Find index_page
start = content.find("def index_page(")
end = content.find("def ", start + 10)
func = content[start:end]
print("\n--- index_page ---")
print(func[:300])
print("...")

# Find build function calls
idx = content.find("def build()")
end = content.find("if __name__", idx)
build_func = content[idx:end]
# Find where list_page is called
calls = build_func.split("\n")
for i, line in enumerate(calls):
    if "list_page(" in line or "index_page(" in line or "detail_page(" in line:
        print(f"\nBuild call: {line.strip()}")