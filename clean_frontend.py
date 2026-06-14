import re

# Clean hoemright.vue
p = r'F:/github好看网站/leleo-home-page-main/src/components/hoemright.vue'
with open(p, 'r', encoding='utf-8') as f:
    c = f.read()

# Remove search engine data
old_data = 'data() {\n\t\t\treturn {\n\t\t\t\tsearchQuery:'
idx = c.find(old_data)
if idx > 0:
    end = c.find('methods:', idx)
    end = c.rfind('}', idx, end)
    c = c[:idx] + 'data(){return{}},\n\t    ' + c[end+1:]

# Remove dead methods (performSearch, isLikelyUrl)
c = re.sub(r'performSearch[\s\S]*?isLikelyUrl[\s\S]*?\n\t\t\t}', '', c)

# Clean up double commas
c = c.replace(',,', ',').replace('\n\n\n', '\n\n')

# Remove duplicate CSS
c = c.replace('@import url(/css/app.less);\n@import url(/css/mobile.less);', '')

with open(p, 'w', encoding='utf-8') as f:
    f.write(c)
print('hoemright cleaned')

# Clean app.js - remove unused imports and dead code
p2 = r'F:/github好看网站/leleo-home-page-main/src/app.js'
with open(p2, 'r', encoding='utf-8') as f:
    c = f.read()

# Remove unused typewriter import from app.js (hoemright imports it)
c = c.replace("import typewriter from './components/typewriter.vue';\n", '')

# Remove musicLyric2 computed
c = re.sub(r',\n    musicLyric2[^}]*\}', '', c)

# Remove dead currentSong computed (currentMusicSong is used instead)
c = re.sub(r',\n    currentSong[^}]*\}', '', c)

# Remove jump method
c = re.sub(r',\n    jump[^}]*\}', '', c, flags=re.DOTALL)

# Remove projectcardsShow method
c = re.sub(r',\n    projectcardsShow[^}]*\}', '', c, flags=re.DOTALL)

# Remove unused isVdMuted
c = c.replace('this.isVdMuted = true;', '').replace('this.isVdMuted = false;', '')

with open(p2, 'w', encoding='utf-8') as f:
    f.write(c)
print('app.js cleaned')

# Remove unused style imports from hoemright
with open(p, 'r', encoding='utf-8') as f:
    c = f.read()

with open(p, 'w', encoding='utf-8') as f:
    f.write(c)
print('All frontend cleaned')
