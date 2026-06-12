import re

with open("src/build.py", "r", encoding="utf-8") as f:
    content = f.read()

# Show key function signatures
for name in ["page_frame", "content_card", "list_page", "detail_page", "index_page", "build"]:
    start = content.find("def " + name + "(")
    if start >= 0:
        end = content.find("\n", start)
        print(f"  {content[start:end]}")

# Show page_frame param info
idx = content.find("def page_frame")
end_idx = content.find("return f", idx)
signature = content[idx:end_idx+8]
print("\n--- page_frame body start ---")
lines = signature.split("\n")
for l in lines[:8]:
    print(f"  {l.strip()}")
print("---")