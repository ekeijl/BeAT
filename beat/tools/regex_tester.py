import re
def test_regex(regex, sample_data, stringReturn=True):
	try:
		if not regex:
			#regular expression is empty
			return ("" if stringReturn else None)
		compiled = re.compile(regex, re.MULTILINE + re.DOTALL)
		if not compiled:
			return ("Error: compilation failed" if stringReturn else None)
		match = compiled.match(sample_data)
		if match:
			dict = match.groupdict()
			res = '\n'.join([(i + ': ' + dict[i]) for i in sorted(dict.iterkeys())])
			return (res if stringReturn else dict)
		else:
			return ("Error: no match found" if stringReturn else None)
	except Exception as e:
		return "Error: %s"%e if stringReturn else None
