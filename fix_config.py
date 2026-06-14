p = r'F:/github好看网站/leleo-home-page-main/src/config.js'
with open(p, 'r', encoding='utf-8') as f:
    c = f.read()

# Find the disease card position
idx = c.find('叶片病害诊断')
# Find the next '],' which closes projectcards
close_array = c.find('],', idx)
# Keep everything up to and including '],'
good_part = c[:close_array+2]

# Add clean ending
clean_end = '''

		statement: ["备案号：XXICP备123456789号", "Copyright © 2025 Leleo"],
	}

export default config
'''
result = good_part + clean_end

with open(p, 'w', encoding='utf-8') as f:
    f.write(result)

# Verify
opens = result.count('{')
closes = result.count('}')
print(f'Braces: {opens}/{closes} {"OK" if opens==closes else "FAIL"}')
