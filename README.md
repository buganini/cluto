# macOS
```
brew install sip-install
pip install -r requirements.txt
```

# Dependencies
```
	Python3
	PyQT5
	PyQT5-Poppler
	PIL
	xpdfimport from LibreOffice/OpenOffice.org
```

# Query Language
```
	${KEY}: local variable
	@{KEY}: lexical variable (inherit from parent)
	#{KEY}: list of children's local variable
	%{KEY}: item properties:
		CONTENT: content (image or text)
		TYPE: area type
		WIDTH: image width
		HEIGHT: image height
		FILE: original file path
		LEVEL:	level
		COUNT: number of children
		ORDER: children are well ordered
		PAGE: page number in pdf file, always 0 for other file type
		INDEX: index in siblings, started from 1
		HASH: assigned hash string
		TITLE: title (filename and page number, if available)
		THIS: item itself
		PARENT: item's parent
	Operators:
		[]
		,
		+
		-
		==
		!=
		&&
		||
		!
		>=
		>
		<=
		<
	Data Types:
		String: "string"
		Non-negative Integer: 1
		List: "a", 1
		Single-item list: 1,
	Functions:
		CHILD
			child(%{this}, 1) -> first child of this item
		ABS
			abs(-1) -> 1
		CONCAT
			concat("abc", "def") -> "abcdef"
			concat(["abc", "def"], ["123", "456"]) -> ["abc123", "def456"]
		JOIN
			join(" ",("a","b")) -> "a b"
		BASENAME
			basename("a/b/c.d") -> "c.d"
		DIRNAME
			basename("a/b/c.d") -> "a/b"
		PREFIX
			prefix("c.d") -> "c"
		SUFFIX
			suffix("c.d") -> "d"
		PATHJOIN
			pathjoin("a/b","c.d") -> "a/b/c.d"
		LEN
			len("a","b","abc") -> 3
		LIST_HAS
			list_has(("a","b"),"a") -> true
			list_has(("a","b"),"c") -> false
		SPLIT
			split(";","a;b") -> ("a","b")
		SLICE
			slice(("a","b","c","d"),1) -> ("b","c","d")
			slice(("a","b","c","d"),1,2) -> ("b","c")
		REPLACE
			replace("a","b","abc") -> "bbc"
		REGEX_REPLACE
			regex_replace("[bc]+","z","abcdcbe") -> "azdze"
		TEXT
			TEXT(content) -> text
		COALESCE
			coalesce(("", "a","b", "", "c")) -> "a"
		FIELD
			field("foo", "name:blah\nfoo: bar\nhoho") -> "bar"
		REJECT_FIELD
			reject_field("aa", "aa:bb\ncc:dd") -> "cc:dd"
			reject_field(("aa","ee"), "aa:bb\ncc:dd\nee:ff") -> "cc:dd"
		REJECT
			reject("aa", "aa\nbb\ncc\ndd") -> "bb\ncc\ndd"
			reject(("aa","cc"), "aa\nbb\ncc\ndd") -> "bb\ndd"
		LOOKUP
			lookup("k,v.csv", k) -> v
		ENSURE
			ensure("foo", "a\nb", 1) -> "a\nfoo b"
			ensure("foo", "foo a\nb", 1) -> "foo a\nb"
		PRINT
			print(x) -> x # output to stdout
```