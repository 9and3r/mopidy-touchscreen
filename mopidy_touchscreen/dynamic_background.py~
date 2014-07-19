import random

class DynamicBackground():

	def __init__(self):
		self.current=[0,0,0]
		self.target=[0,0,0]
		for x in range(0, 3):
			self.target[x]=random.randint(0,255)

	def drawBackground(self,surface):
		same = True
		for x in range(0, 3):
			if self.current[x]> self.target[x]:
				self.current[x]=self.current[x]-1
			elif self.current[x]<self.target[x]:
				self.current[x]=self.current[x]+1
			if(self.current != self.target):
				same = False
		if same:
			for x in range(0, 3):
				self.target[x]=random.randint(0,255)
		surface.fill(self.current)

		
