#!/usr/bin/python

testnetid = ('test netid', 'test password') # User and pass - make multiple copies of this file for tests with multiple users

from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions

# Function to login with netid
def weblogin(d, user = testnetid[0], pwd = testnetid[1]):

	userid = user
	password = pwd

	try:
		userbox = d.find_element_by_id('weblogin_netid')
		userbox.send_keys(userid)
	except selenium.common.exceptions.NoSuchElementException:
		e = d.find_element_by_xpath('//li[@class="login-static-name"]/span')
		if (e.text == userid):
			pass
		else:
			raise Exception('The browser has a pre-filled netID which does not match the one provided')
	passbox = d.find_element_by_id('weblogin_password')

	passbox.send_keys(password)
	
	passbox.send_keys(Keys.RETURN)


def prelogin(d):
	d.get('https://weblogin.washington.edu/')
	weblogin(d)



