from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

class PlexSel:
	"""
	Controls a plex web server using Selenium with the intent of essentialy remote controlling a system
	"""
	def __init__(self, url, movie_base):
		"""
		Args:
			url: the base IP/Port to access the plex server (required) (eg: "http://192.168.0.10:32400")
			movie_base: I haven't quite figured out what this portion means to plex, but it's necessary to navigate a server.
				Mine is "server/<hash>/details?key=%2Flibrary%2Fmetadata%2F<Movie Index>"
				Yours can be found by navigating to your plex' ip addr and opening a movie and copying a url up to metadata%2F (Required)
		"""
		self._url = f"{url}/web/index.html#!/"
		self._driver = webdriver.Firefox()
		self._movie_base = movie_base

		# The CSS Selector values for every button we may want to press
		self._button_lookup = {
			"home" : '.HomeSourceLink-sourceLink-aaNRiO > div:nth-child(2) > div:nth-child(1)',
			"firstExperience" :  '.FirstRunExperienceStep-stepButton-yDEnXT',
			"startPlay" : 'button._76v8d68:nth-child(1)',
			"activeFullscreen" : 'div._64atrd0:nth-child(2) > button:nth-child(1) > svg:nth-child(1)',
			"activeToMini" : '.FullPlayerTopControls-topControls-Fp11QH > div:nth-child(1) > button:nth-child(1) > svg:nth-child(1)',
			"activeToMaxi" : '.MiniPlayerPoster-expandButton-FhcQi0 > svg:nth-child(1)',
			"activePlayPause" : '.PlayerIconButton-isPrimary-VXE1Uo > svg:nth-child(1)',
		}
	
	def __del__(self):
		self.close()

	# Wrapper functions to make working with Selenium easier

	def buttonExists(self, css_desc):
		return len(self._driver.find_elements(By.CSS_SELECTOR, css_desc)) > 0
	
	def buttonPress(self, css_desc):
		if not self.buttonExists(css_desc):
			return False
		self._driver.find_elements(By.CSS_SELECTOR, css_desc)[0].click()
		return True
	
	def timeoutPress(self, css_desc, timeout=15):
		start = time.time()
		now = start
		pressed = self.buttonPress(css_desc)
		while not pressed and ((now - start) <= timeout):
			pressed = self.buttonPress(css_desc)
			now = time.time()
		return pressed

	def pressHome(self, timeout=15):
		return self.timeoutPress(self._button_lookup["home"], timeout)
	
	def start(self):
		self._driver.get(self._url)
		while not self.pressHome(0):
			self.timeoutPress(self._button_lookup["firstExperience"], 1)
	
	def playMovie(self, timeout=15):
		return self.timeoutPress(self._button_lookup["startPlay"], timeout)

	def getMovieByIndex(self, index):
		self._driver.get(f"{self._url}{self._movie_base}{index}")

	def currentlyActive(self):
		return self.buttonExists(self._button_lookup["activePlayPause"])

	def currentlyPlaying(self):
		while not self.buttonExists(self._button_lookup["activePlayPause"]):
			time.sleep(1)
		help(self._driver.find_elems(By.CSS_SELECTOR, self._button_lookup["activePlayPause"])[0])

	def toggleFullscreen(self):
		#Will toggle the fullscreen status of the movie -- Will need to figure out how to track fullscreen status
		return self.timeoutPress(self._button_lookup["activeFullscreen"])
	
	def isMini(self):
		return self.currentlyActive() and self.buttonExists(self._button_lookup["activeToMaxi"])

	def toMini(self):
		if not self.isMaxi():
			return False
		return self.timeoutPress(self._button_lookup["activeToMini"], 1)

	def isMaxi(self):
		return self.currentlyActive() and self.buttonExists(self._button_lookup["activeToMini"])

	def toMaxi(self):
		if not self.isMini():
			return False
		return timeoutPress(self._button_lookup["activeToMaxi"], 1)

	def toggleMaxi(self):
		if self.isMaxi():
			return self.toMini()
		return self.toMaxi()

	def close(self):
		self._driver.close()
		

import json
if __name__ == "__main__":
	keys = {}
	with open("keys.json") as f:
		keys = json.load(f)
	ps = PlexSel(keys["url"], keys["movie_base"])
	ps.start()
	ps.getMovieByIndex(13224)
	ps.playMovie()
	while True:
		time.sleep(1)
