p = r'F:/github好看网站/leleo-home-page-main/src/config.js'
with open(p, 'r', encoding='utf-8') as f:
    c = f.read()

old_url = '梨冻紧,Wiz_H张子豪 - Follow.mp3'
new_url = '7paste&live_nine - 罗生门-0ad1b38d4a32.mp3'
old_lrc = '罗生门(follow)-梨冻梨&wiz子豪-歌词.lrc'
new_lrc = '罗生门 (follow)-7paste&live_nine-歌词.lrc'

c = c.replace(old_url, new_url)
c = c.replace(old_lrc, new_lrc)

with open(p, 'w', encoding='utf-8') as f:
    f.write(c)

# Verify
for line in c.split('\n'):
    if 'Follow' in line or '罗生' in line:
        print(line.strip()[:120])
