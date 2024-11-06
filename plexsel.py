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
		# Returns true if a button exists at this point in time
		return len(self._driver.find_elements(By.CSS_SELECTOR, css_desc)) > 0
	
	def buttonPress(self, css_desc):
		# Presses a button if it exists
		if not self.buttonExists(css_desc):
			return False
		self._driver.find_elements(By.CSS_SELECTOR, css_desc)[0].click()
		return True
	
	def timeoutPress(self, css_desc, timeout=15):
		# Waits for a button to exist and then presses it
		start = time.time()
		now = start
		pressed = self.buttonPress(css_desc)
		while not pressed and ((now - start) <= timeout):
			pressed = self.buttonPress(css_desc)
			now = time.time()
		return pressed

	def pressHome(self, timeout=15):
		# Press the 'Home' button
		# TODO: Add logic to make this callable from anywhere
		return self.timeoutPress(self._button_lookup["home"], timeout)
	
	def start(self):
		# Starts up the selenium driver and navigates to the home page
		self._driver.get(self._url)
		while not self.pressHome(0):
			self.timeoutPress(self._button_lookup["firstExperience"], 1)
	
	def playMovie(self, timeout=15):
		# Presses the "Play Movie" button to start playback
		return self.timeoutPress(self._button_lookup["startPlay"], timeout)

	def getMovieByIndex(self, index):
		# Navigates to a movie's url. This uses the movie index from the plex server api
		# this api will have no knowledge of the plex server stuff, it expects you to know
		# what movie index you feed it
		# TODO: Make sure this works from any page
		self._driver.get(f"{self._url}{self._movie_base}{index}")

	def currentlyActive(self):
		# Determines if a video is active
		return self.buttonExists(self._button_lookup["activePlayPause"])

	def currentlyPlaying(self):
		# FIXME: Figure out wether or not the video is actually playing
		while not self.buttonExists(self._button_lookup["activePlayPause"]):
			time.sleep(1)
		help(self._driver.find_elems(By.CSS_SELECTOR, self._button_lookup["activePlayPause"])[0])

	def toggleFullscreen(self):
		# Will toggle the fullscreen status of the movie
		# TODO: need to figure out how to track fullscreen status
		return self.timeoutPress(self._button_lookup["activeFullscreen"])
	
	def isMini(self):
		# Determines if there is a video active and we're in Mini Mode
		return self.currentlyActive() and self.buttonExists(self._button_lookup["activeToMaxi"])

	def toMini(self):
		# Sets to mini mode if we're in maxi mode
		if not self.isMaxi():
			return False
		return self.timeoutPress(self._button_lookup["activeToMini"], 1)

	def isMaxi(self):
		# Determines if we're in Maxi Mode
		return self.currentlyActive() and self.buttonExists(self._button_lookup["activeToMini"])

	def toMaxi(self):
		# Sets to max mode
		if not self.isMini():
			return False
		return timeoutPress(self._button_lookup["activeToMaxi"], 1)

	def toggleMaxi(self):
		# Toggles player between mini and maxi
		if self.isMaxi():
			return self.toMini()
		elif self.isMini():
			return self.toMaxi()
		return False

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
