import re

filepath = r"C:\Users\kangg\Desktop\网站搭建\ai-news-site\docs\interact\index.html"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

print(f"File length: {len(content)}")

# Find startCam function boundaries
start = content.find("async function startCam() {")
end = content.find("function skipCam() {", start)
print(f"startCam: {start}, skipCam: {end}")

# Clean replacement for startCam
clean_startcam = """async function startCam() {
  prompt.classList.remove('show');
  guide.classList.add('hidden');
  distHint.classList.remove('hidden');
  debugCanvas.classList.add('show');

  try {
    const s = await navigator.mediaDevices.getUserMedia({video:{width:640,height:480,facingMode:'user'}});
    video.srcObject = s; await video.play();
    prog(60, '加载手势识别...');
    const hands = new Hands({ locateFile: f => \https://unpkg.com/@mediapipe/hands@0.4.1675469240/\\ });
    hands.setOptions({ maxNumHands: 1, modelComplexity: 1, minDetectionConfidence: 0.5, minTrackingConfidence: 0.3 });
    hands.onResults(onHand);
    const cam = new Camera(video, { onFrame: async () => { try { await hands.send({image:video}); } catch(e){} }, width: 640, height: 480 });
    prog(85, '就绪！'); await cam.start();
    if (isMobile) {
      clearTimeout(camFallbackTimer);
      camFallbackTimer = setTimeout(() => {
        if (idle > 2) {
          console.log('Camera timeout on mobile, switching to touch');
          try { video.srcObject.getTracks().forEach(t=>t.stop()); } catch(e){}
          glTxt.textContent = '🖱️ 触控模式 · 点击切换形态';
          debugCanvas.classList.remove('show');
          distHint.classList.add('hidden');
          setupMouse();
        }
      }, 10000);
    }
    prog(100); setTimeout(() => document.getElementById('loading').classList.add('hidden'), 200);
  } catch(e) {
    console.warn(e);
    glTxt.textContent = '🖱️ 鼠标模式 · 点击切换';
    debugCanvas.classList.remove('show');
    setupMouse(); prog(100); setTimeout(() => document.getElementById('loading').classList.add('hidden'), 200);
  }
}
"""

if start >= 0 and end >= 0:
    content = content[:start] + clean_startcam + "\n" + content[end:]
    print("startCam replaced successfully")
else:
    print("ERROR: Could not find boundaries")

# Fix touchEndFired for touchend
old_touch = "if (!touchMoved) cycleMode();\n  }, {passive:true});\n\n  // On mobile, also make gesture label tappable"
new_touch = "if (!touchMoved) { cycleMode(); touchEndFired = true; }\n  }, {passive:true});\n\n  // On mobile, also make gesture label tappable"
if old_touch in content:
    content = content.replace(old_touch, new_touch)
    print("Touch fix applied")
else:
    print("Touch pattern not found")

# Fix GL click
old_gl = "gl.addEventListener('click', e => { e.stopPropagation(); cycleMode(); });"
new_gl = "gl.addEventListener('click', e => { e.stopPropagation(); if (touchEndFired) { touchEndFired = false; return; } cycleMode(); });"
if old_gl in content:
    content = content.replace(old_gl, new_gl)
    print("GL click fix applied")
else:
    print("GL click pattern not found")

# Remove any leftover tasks-vision references  
content = re.sub(r'let FilesetResolver, HandLandmarker;\s*', '', content)
content = re.sub(r"window\._handLandmarker = null;\s*", '', content)
content = re.sub(r"\s*import \{ FilesetResolver, HandLandmarker \} from '[^']*';?\s*", '', content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("All fixes applied!")
