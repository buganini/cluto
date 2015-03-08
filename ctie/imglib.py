default_threshold = 30
default_padding = 5

def leftTrim(im, x1, y1, x2, y2, threshold=default_threshold, padding=default_padding):
	stop=False
	for a in xrange(x1,x2):
		last=im.getpixel((a,y1))
		for i in xrange(y1,y2):
			c=im.getpixel((a,i))
			if abs(c-last)>threshold:
				stop=True
				break
			last=c
		if stop:
			break
	nx1=a-padding
	return max(nx1,x1)

def rightTrim(im, x1, y1, x2, y2, threshold=default_threshold, padding=default_padding):
	stop=False
	for a in xrange(x2,x1,-1):
		last=im.getpixel((a-1,y1))
		for i in xrange(y1,y2):
			c=im.getpixel((a-1,i))
			if abs(c-last)>threshold:
				stop=True
				break
			last=c
		if stop:
			break
	nx2=a+padding
	return min(nx2, x2)

def topTrim(im, x1, y1, x2, y2, threshold=default_threshold, padding=default_padding):
	stop=False
	for a in xrange(y1,y2):
		last=im.getpixel((x1,a))
		for i in xrange(x1,x2):
			c=im.getpixel((i,a))
			if abs(c-last)>threshold:
				stop=True
				break
			last=c
		if stop:
			break
	ny1=a-padding
	return max(ny1,y1)

def bottomTrim(im, x1, y1, x2, y2, threshold=default_threshold, padding=default_padding):
	stop=False
	for a in xrange(y2,y1,-1):
		last=im.getpixel((x1,a-1))
		for i in xrange(x1,x2):
			c=im.getpixel((i,a-1))
			if abs(c-last)>threshold:
				stop=True
				break
			last=c
		if stop:
			break
	ny2=a+padding
	return min(ny2, y2)
