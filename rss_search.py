#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import time, sys, os, urllib2
import xml.etree.ElementTree as ET

class rss_search:
	def __init__(self,default=False):
		if default:
			pass

		self.case_sens = False
		self.pages = []
		self.keywords = []


	def __call__(self):
		# Currently wipes every time called
		self.titles = []
		self.descriptions = []
		self.links = []
		# categories?

		for i in range(len(self.pages)):
			page_current = self.pages[i]
			data = self.fetch_page(page_current)
			if data is not None:
				self.search_page(data)

	def search_page(self,data):
			root  = data.getroot()
			items = root.findall('channel/item')

			# Maybe optimize later
			titles = []
			descriptions = []
			links = []
			for item in items:
				titles.append(item.findtext('title'))
				descriptions.append(item.findtext('description'))
				links.append(item.findtext('link'))

		    # print len(titles),len(descriptions),len(links)
			for j in range(len(self.keywords)):
				keyword = self.keywords[j]
				for k in range(len(titles)):
					
					# Better searching
					title = self.search_func(keyword,titles[k])
					desc  = self.search_func(keyword,descriptions[k])

					if title or desc:
						self.titles.append(titles[k])
						self.descriptions.append(descriptions[k])
						self.links.append(links[k])

	def search_func(self,keyword, string):
		if not self.case_sens:
			keyword = keyword.lower()
			string  = string.lower()
		if len(keyword.split()) > 1:
			if keyword in string:
				return True
		else:
			string = string.replace('-',' ')
			words  = string.split()
			words  = [w.strip(',.:;') for w in words]
			if any(keyword == s for s in words):
				return True

		return False

	def set_keywords(self, key_string):
		keys = key_string.split(',')
		self.keywords = [keys[i].strip() for i in range(len(keys))]

	def set_pages(self, page_string):
		page = page_string.split(', ')
		self.pages = [page[i].strip() for i in range(len(page))]

	def fetch_page(self, page):
		try:
			response = urllib2.urlopen(page,timeout=5)
			data = ET.parse(response)
		except urllib2.URLError:
			print 'Cannot fetch webpage: %s' %page
			data = None
		except ValueError:
			print 'Something wrong with URL: %s' %page
			data = None
		return data