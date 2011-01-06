import re
def test_regex(regex, sample_data):
	try:
		if not regex:
			#regular expression is empty
			return ""
		compiled = re.compile(regex, re.MULTILINE + re.DOTALL)
		if not compiled:
			return "Error: compilation failed"
		match = compiled.match(sample_data)
		if match:
			dict = match.groupdict()
			return '\n'.join([(i + ': ' + dict[i]) for i in sorted(dict.iterkeys())])
		else:
			return "Error: no results"
	except Exception as e:
		return "Error: %s"%e
