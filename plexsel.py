from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
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
			"activeFullscreen" : 'div._64atrd0:nth-child(2) > button:nth-child(1)',
			"activeVideoArea" : '.PlayPauseOverlay-overlay-lF71cy',
			"activeToMini" : '.FullPlayerTopControls-topControls-Fp11QH > div:nth-child(1) > button:nth-child(1) > svg:nth-child(1)',
			"activeToMaxi" : '.MiniPlayerPoster-expandButton-FhcQi0 > svg:nth-child(1)',
			"activePlayPause" : '.PlayerIconButton-isPrimary-VXE1Uo',
			"startFromBeginning" : 'button.ListModalItem-listModalItem-yDiCT4:nth-child(2)',
			"activeStop" : 'button.PlayerIconButton-playerButton-zDmEsI:nth-child(6) > svg:nth-child(1)'
		}
	
	def __del__(self):
		self.close()

	# Wrapper functions to make working with Selenium easier
	def buttonExists(self, css_desc):
		# Returns true if a button exists at this point in time
		return len(self._driver.find_elements(By.CSS_SELECTOR, css_desc)) > 0
	
	def getButton(self, css_desc):
		if self.buttonExists(css_desc):
			return self._driver.find_element(By.CSS_SELECTOR, css_desc)
		return None
	
	def buttonPress(self, css_desc):
		# Presses a button if it exists
		if not self.buttonExists(css_desc):
			return False
		self._driver.find_elements(By.CSS_SELECTOR, css_desc)[0].click()
		return True
	
	def timeoutGetButton(self, css_desc, timeout=15):
		start = time.time()
		now = start
		button = self.getButton(css_desc)
		while button is None and ((now - start) <= timeout):
			button = self.getButton(css_desc)
			now = time.time()
		return button

	def timeoutPress(self, css_desc, timeout=15):
		# Waits for a button to exist and then presses it
		start = time.time()
		now = start
		pressed = self.buttonPress(css_desc)
		while not pressed and ((now - start) <= timeout):
			pressed = self.buttonPress(css_desc)
			now = time.time()
		return pressed

	def getDriver(self):
		return self._driver

	def pressHome(self, timeout=15):
		# Press the 'Home' button
		# TODO: Add logic to make this callable from anywhere
		return self.timeoutPress(self._button_lookup["home"], timeout)
	
	def start(self):
		# Starts up the selenium driver and navigates to the home page
		self._driver.get(self._url)
		while not self.pressHome(0):
			self.timeoutPress(self._button_lookup["firstExperience"], 1)
	
	def startFromBeginning(self, timeout=15):
		self.timeoutPress(self._button_lookup["startFromBeginning"], timeout)

	def playMovie(self, timeout=15):
		# Presses the "Play Movie" button to start playback
		button = self.timeoutGetButton(self._button_lookup["startPlay"])
		if button is None:
			return False
		name = button.accessible_name
		button.click()
		if name == "Resume":
			self.startFromBeginning()

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
		# States if video is actively playing
		button = self.timeoutGetButton(self._button_lookup["activePlayPause"]);
		if button is None:
			return False
		# The button would be "Play" if it was Paused and "Pause" if it's playing
		if button.accessible_name == "Pause":
			return True
		return False
	
	def activePlay(self):
		if not self.currentlyActive() or self.currentlyPlaying():
			return False
		return self.timeoutPress(self._button_lookup["activePlayPause"])
	
	def activePause(self):
		if self.currentlyPlaying():
			return self.timeoutPress(self._button_lookup["activePlayPause"])
		return False
	
	def activePlayPause(self):
		if not self.currentlyActive():
			return False
		return self.timeoutPress(self._button_lookup["activePlayPause"])
	
	def activeStop(self):
		if not self.currentlyActive():
			return False
		return self.timeoutPress(self._button_lookup["activeStop"])

	def toggleFullscreen(self):
		# Will toggle the fullscreen status of the movie
		# TODO: need to figure out how to track fullscreen status
		button = self.timeoutGetButton(self._button_lookup["activeVideoArea"])
		if button is None:
			return False
		action = ActionChains(self._driver)
		action.double_click(on_element = button)
		action.perform()
	
	def isActiveFullscreen(self):
		button = self.getButton(self._button_lookup["activeFullscreen"])
		if button is None:
			return False
		name = button.accessible_name
		return name == "Exit Fullscreen"
		# "Enter Fullscreen" is it's other name
		
	def activeFullscreen(self, setFullscreen=True):
		if not self.currentlyActive():
			return False
		if setFullscreen and not self.isMaxi():
			self.setMaxi()
		if setFullscreen and not self.isActiveFullscreen():
			return self.toggleFullscreen()
		if not setFullscreen and self.isActiveFullscreen():
			return self.toggleFullscreen()
		return False

	def isMini(self):
		# Determines if there is a video active and we're in Mini Mode
		return self.currentlyActive() and self.buttonExists(self._button_lookup["activeToMaxi"])

	def toMini(self):
		# FIXME: This is brokie cause the toMini button maynot be visible
		return False
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
		return self.timeoutPress(self._button_lookup["activeToMaxi"], 1)

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
elem = None
ps = None
if __name__ == "__main__":
	keys = {}
	with open("keys.json") as f:
		keys = json.load(f)
	ps = PlexSel(keys["url"], keys["movie_base"])
	ps.start()
	ps.getMovieByIndex(13224)
	ps.playMovie()
	#time.sleep(10)
	#elem = ps.currentlyPlaying()
