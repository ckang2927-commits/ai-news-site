import os, sys
sys.stdout.reconfigure(encoding="utf-8")
root = "C:/Users/kangg/Desktop/网站搭建/ai-news-site"
imgs = []
for r,d,f in os.walk(os.path.join(root, "docs")):
    for x in f:
        if x.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
            imgs.append(os.path.join(r, x))
print(f"Found {len(imgs)} images:")
for img in sorted(imgs):
    size = os.path.getsize(img)
    print(f"  {img.replace(root+'/docs/', '')} ({size/1024:.1f}KB)")

# Also check content directory for referenced images
content_imgs = []
for r,d,f in os.walk(os.path.join(root, "content")):
    for x in f:
        if x.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
            content_imgs.append(os.path.join(r, x))
print(f"\nContent images: {len(content_imgs)}")
for img in content_imgs:
    print(f"  {img}")