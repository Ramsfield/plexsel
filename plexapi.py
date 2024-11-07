"""
PlexAPI

Uses Request calls to interact with a server. This has no intent to be a 1:1 of the API.
Just of things I need
"""
import json
import requests
import threading
import time
import xml.dom.minidom
import xmltodict
from thefuzz import process

THREAD_WAIT_SECONDS = 60 * 20 # Update every 20 minutes

class PlexAPI:
	def __init__(self, base_url, token):
		self._url = base_url
		self._token = token
		self._movies = {}
		self._lastUpdated = None
		self.updateMovieList()
		self._updateThread = threading.Timer(THREAD_WAIT_SECONDS, self.updateMovieList)
		self._updateThread.start()

	def __del__(self):
		self._updateThread.cancel()
	
	def getXmlRequest(self, path):
		resp = requests.get(f"{self._url}/{path}?X-Plex-Token={self._token}")
		if not resp.ok:
			return None
		return resp.content
	
	def getXmlPrettyRequest(self, path):
		resp = self.getXmlRequest(path)
		if resp is None:
			return resp
		dom = xml.dom.minidom.parseString(resp)
		return dom.toprettyxml()
	
	def getRequestJson(self, path):
		resp = self.getXmlRequest(path)
		if resp is None:
			return resp
		return xmltodict.parse(resp)

	def updateMovieList(self):
		"""
		Function to update the self._movies list
		"""
		try:
			self._movies = self.getRequestJson("library/sections/1/all")['MediaContainer']['Video']
			self._lastUpdated = time.time()
			print(f"Updated Movie List at {self._lastUpdated} with {len(self._movies)} items")
		except:
			print(f"UpdateMovieList encountered an error.")

	def getMovieIndexList(self):
		movies = { i["@title"] : i["@ratingKey"] for i in self._movies }
		return movies
	
	def getMovieIndexByTitle(self, title):
		movies = self.getMovieIndexList()
		if title in movies:
			return movies[title]
		return None
	
	def getMovieTitleFuzz(self, title, count=5):
		movies = self.getMovieIndexList()
		return [ i[0] for i in process.extract(title, movies.keys(), limit = count) ]

p = None
if __name__ == "__main__":
	keys = {}
	with open("keys.json") as f:
		keys = json.load(f)
	p = PlexAPI(keys["url"], keys["token"])
	
