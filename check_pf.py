import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open("src/build.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the page_frame return statement
idx = content.find('def page_frame(title, body_html, nav_depth=0, og_desc=None, og_image=None):')
end = content.find("\ndef ", idx + 10)
func = content[idx:end]
print("Page_frame has search_data param:", "search_data" in func)
print()
# Show the variables section
vars_start = func.find("np = nav_prefix")
vars_end = func.find("return f")
print(func[vars_start:vars_end])