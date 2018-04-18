#!/usr/bin/env python
"""
2018-01-05 TL First version
"""

"""
Description:
This scripts downloads the No-Fly zones from droneluftrum by first acquirring an
access token and then using this for the actual download.
Library 'requests' installation, see 'README_requests.md'
License: BSD 3-Clause
"""

print('Importing libraries')
import requests
from requests.auth import HTTPBasicAuth
import json
from urllib.request import urlopen, URLError, HTTPError
import time # wait
import datetime # datetime.now
import sys # exit (use quit() when you only want to terminate spawning script, not all)
import os
print('Import done')

print_raw_response = False

def download():
	# # Get Access Token
	get_token_url = "https://www.droneluftrum.dk/oauth/token?grant_type=client_credentials"
	required_auth = HTTPBasicAuth('NaviairDroneWeb','NaviairDroneWeb')
	payload = {}
	# r = requests.post(url = get_token_url, verify=True, auth=required_auth, data=payload)
	try:
		r = requests.post(url = get_token_url,auth=required_auth,data=payload)
	except:
		print('Unexpected error in polling get_requests')

	if r.text == '0' or int(r.status_code) != 200: # Handle empty response
		print("No response or error code 200")
	else:
		if print_raw_response == True:
			print("--- Raw response start ---")
			print(r.text)
			print( "--- Raw response end ---")
		try:
			jsonformat = json.loads(r.text) # convert to json
		except:
			print('Unexpected error in parsing r.text as json')

		access_token = jsonformat["access_token"]
		token_type   = jsonformat["token_type"]

		if access_token != '' and access_token != '0':
			# print "Access token: "+jsonformat["access_token"]
			print("Access token acquired")

			#time.sleep(1)

			# # Get no-fly zones
			# Parse URL - NOTE added an extra '%' to escape '%20', could have been replaced with the corresponding ' ' (space)
			url = 'https://www.droneluftrum.dk//api/uaszones/exportKmlUasZones?Authorization={}%20{}'.format(token_type, access_token)
			#print('Trying URL: {}'.format(url))
			print('Attempting to download')

			try:
				response = urlopen(url)
			except HTTPError as e:
				result = '{}'.format(e.code)
			except URLError as e:
				result = '{}'.format(e.reason)
			else:
				print('No errors encountered during download, attempting to read result')
				result = response.read().decode('utf-8')

			if result == '400' or result == 400:
				print('Bad request, terminating')
				sys.exit()
			else:
				print('Result read')

				# Get datetime information (https://www.saltycrane.com/blog/2008/06/how-to-get-current-date-and-time-in/)
				now = datetime.datetime.now()
				# Save to file with proper naming
				print('Attempting to write file')
				dirname = os.path.dirname(__file__)
				directory = (dirname + '/' if dirname else '') + 'static/'
				if not os.path.exists(directory):
					os.makedirs(directory)
				file_name = directory + 'drone_nofly_dk.kml'
				file = open(file_name, 'w')
				file.write(result)
				file.close()
				print('File written: {}'.format(file_name))


if __name__ == '__main__':
	download()