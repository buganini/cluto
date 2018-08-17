class CRanges(object):
	"""
		Continuous ranges
	"""

	def __init__(self):
		self.ranges = []

	def __str__(self):
		return str(self.ranges)

	def __eq__(self, target):
		if type(target) == list:
			return self.ranges == target
		elif type(target) == Ranges:
			return self.ranges == target.ranges
		else:
			return self is target

	def add(self, a, b):
		if a==b:
			return
		pos = -1
		for i in  range(len(self.ranges)):
			if a <= self.ranges[i][1] or a <= self.ranges[i][0]:
				pos = i
				break
		if pos != -1:
			if a == self.ranges[pos][0]:
				if b > self.ranges[pos][1]:
					self.ranges[pos][1] = b
			else:
				self.ranges.insert(pos, [a, b])
		else:
			pos = len(self.ranges) - 1
			self.ranges.append([a, b])
		while 0 <= pos and pos < len(self.ranges)-1:
			if self.ranges[pos][1] >= self.ranges[pos+1][0]:
				self.ranges[pos][0] = min(self.ranges[pos][0], self.ranges[pos+1][0])
				self.ranges[pos][1] = max(self.ranges[pos][1], self.ranges[pos+1][1])
				self.ranges.pop(pos+1)
			else:
				break

	def contains(self, x):
		if len(self.ranges) == 0:
			return 0
		for r in self.ranges:
			if r[0] <= x and x <= r[1]:
				return 2
		if self.ranges[0][0] <= x and x <= self.ranges[-1][1]:
			return 1
		return 0

if __name__ == "__main__":
	r = CRanges()
	assert r == []

	r.add(0, 0)
	assert r == []

	r.add(1, 11)
	assert r == [[1,11]]

	r.add(3, 12)
	assert r == [[1,12]]

	r.add(0, 9)
	assert r == [[0, 12]]

	r.add(30, 39)
	assert r == [[0, 12], [30, 39]]
	assert r.contains(-1) == 0
	assert r.contains(13) == 1
	assert r.contains(5) == 2

	r.add(55, 56)
	assert r == [[0, 12], [30, 39], [55, 56]]

	r.add(80, 89)
	assert r == [[0, 12], [30, 39], [55, 56], [80, 89]]

	r.add(60, 69)
	assert r == [[0, 12], [30, 39], [55, 56], [60, 69], [80, 89]]

	r.add(70, 80)
	assert r == [[0, 12], [30, 39], [55, 56], [60, 69], [70, 89]]

	r.add(69, 70)
	assert r == [[0, 12], [30, 39], [55, 56], [60, 89]]

	r.add(70, 80)
	assert r == [[0, 12], [30, 39], [55, 56], [60, 89]]

	r.add(0, 100)
	assert r == [[0, 100]]

	print("All tests passed.")
