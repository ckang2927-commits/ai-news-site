import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open("src/build.py", "r", encoding="utf-8") as f:
    content = f.read()

# More careful replacement for the main section
old_main_marker = '  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6 relative" style="z-index:1;">'
new_main_block = '''  <script>
    {search_js}
    var isHm = ''' + "'" + "{str(nav_depth == 0).lower()}" + "'" + ''';
    var scp = isHm === "true" ? null : "''' + "{html_escape(title)}" + '''";
    document.addEventListener("DOMContentLoaded", function() { initSearch("globalSearch", "globalDropdown", scp); });
  </script>
  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6 relative" style="z-index:1;">
    {body_html}
  </main>'''

content = content.replace(old_main_marker, new_main_block)

# Now also fix the search JS code string to not use f-string braces
# The search JS is stored in a variable and should work fine since f-string only looks at the template

with open("src/build.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed!")