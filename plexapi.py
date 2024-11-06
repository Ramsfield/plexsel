"""
PlexAPI

Uses Request calls to interact with a server. This has no intent to be a 1:1 of the API.
Just of things I need
"""
import requests
import json

if __name__ == "__main__":
	keys = {}
	with open("keys.json") as f:
		keys = json.load(f)
