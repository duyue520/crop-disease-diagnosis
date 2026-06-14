p=r'F:/github好看网站/leleo-home-page-main/src/components/BlogPage.vue'
with open(p,'r',encoding='utf-8') as f: content=f.read()

# 1. Remove cover upload section
old = '<div class="cover-section mb-3">'
idx = content.find(old)
if idx > 0:
    end = content.find('</v-img>\n          </div>', idx)
    if end < 0: end = content.find('</div>\n          <v-text-field', idx)
    end = content.find('\n          <v-text-field', idx)
    content = content[:idx] + content[end:]

# 2. Replace renderMarkdown
old_md = "    renderMarkdown(t){\n      return (t || '').replace(/\\\\n/g, '<br>').replace(/^### (.+)/gm, '<h4>$1</h4>').replace(/\\\\*\\\\*(.+?)\\\\*\\\\*/g, '<strong>$1</strong>');\n    },"
new_md = '''    renderMarkdown(t){
      if(!t)return'';
      t=t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      t=t.replace(/^### (.+)$/gm,'<h4>$1</h4>');
      t=t.replace(/^## (.+)$/gm,'<h3>$1</h3>');
      t=t.replace(/^# (.+)$/gm,'<h2>$1</h2>');
      t=t.replace(/\\*\\*(.+?)\\*\\*/g,'<strong>$1</strong>');
      t=t.replace(/`(.+?)`/g,'<code>$1</code>');
      t=t.replace(/^- (.+)$/gm,'<li>$1</li>');
      t=t.replace(/(<li>.*<\\/li>\\n?)+/g,'<ul>$&</ul>');
      t=t.replace(/^> (.+)$/gm,'<blockquote>$1</blockquote>');
      t=t.replace(/^---$/gm,'<hr/>');
      t=t.replace(/\\[(.+?)\\]\\((.+?)\\)/g,'<a href=\"$2\" target=\"_blank\">$1</a>');
      return '<div class=\"md-body\">'+t.replace(/\\n\\n/g,'</p><p>').replace(/\\n/g,'<br>').replace(/^(.+)$/gm,'<p>$1</p>')+'</div>';
    },'''
content = content.replace(old_md, new_md)

# 3. Replace hardcoded sunshine with random cover
content = content.replace("a.cover_url||'/img/sunshine.jpg'", "a.cover_url||randomCover()")
content = content.replace("article.cover_url||'/img/sunshine.jpg'", "article.cover_url||randomCover()")

# 4. Add covers init
old_data = "editing:false,editId:null"
content = content.replace(old_data, old_data+",covers:[]")

# 5. Add initCovers and randomCover before mounted
old_mounted = "  watch:{visible(v){if(v){this.load('')}}},\n  mounted(){}"
new_mounted = '''  watch:{visible(v){if(v){this.load('');this.initCovers()}}},
  methods:{initCovers(){for(let i=1;i<=20;i++)this.covers.push('/covers/OIP-C ('+i+').webp')},
  randomCover(){return this.covers.length?this.covers[Math.floor(Math.random()*this.covers.length)]:'/img/sunshine.jpg'},'''
content = content.replace(old_mounted, new_mounted)

# 6. Add cover CSS
old_css = '.detail-cover{filter:brightness(0.5)}'
content = content.replace(old_css, old_css+'\n.md-body p{font-size:16px;line-height:2;color:#444;margin:0 0 16px;text-indent:2em}\n.md-body h2,.md-body h3,.md-body h4{color:#2e7d32;margin:24px 0 12px}\n.md-body blockquote{border-left:4px solid #2e7d32;background:#f1f8e9;padding:12px 16px;margin:12px 0;border-radius:0 8px 8px 0;color:#555}\n.md-body code{background:#f5f5f5;padding:2px 6px;border-radius:4px;color:#e91e63}\n.md-body ul{padding-left:24px;margin:12px 0}\n.md-body li{margin:6px 0;line-height:1.8}\n.md-body hr{border:none;border-top:2px dashed #e0e0e0;margin:24px 0}')

with open(p,'w',encoding='utf-8') as f: f.write(content)
print('BlogPage updated successfully')
