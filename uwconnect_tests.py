#!/usr/bin/python

import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import netid
import netid2
import netid3
import time
from selenium.common.exceptions import NoSuchElementException

class UWConnectTests(unittest.TestCase):

# import pdb; pdb.set_trace()
    def setUp(self):
        self.driver = webdriver.Firefox()
        netid.prelogin(self.driver)
        time.sleep(1)
        
    def cleanUp(self):
        self.driver.close()
    
    def _create_new_request(self, comment):
        driver = self.driver
        driver.get("https://uweval.service-now.com/navpage.do")
        time.sleep(4)
       
        # Click "Create New Request"
        self._switch_frame("gsft_nav")
        try:
		    driver.find_element_by_id("de03be546fcb510054aafd16ad3ee452").click()
        except:
		    driver.find_element_by_id("div.c0ff19b26f76510054aafd16ad3ee447").click()
		    time.sleep(2)
		    driver.find_element_by_id("de03be546fcb510054aafd16ad3ee452").click()
        time.sleep(5)
        
        # Select "All" for CI Class Category
        self._switch_frame("gsft_main")
        time.sleep(1)
        driver.find_element_by_id("sys_select.u_simple_requests.u_cmdb_ci_class_category").send_keys("a")
        
        # Enter Caller
        driver.find_element_by_id("sys_display.u_simple_requests.u_caller").send_keys("Lyndon Coolidge")
        
        # Enter a description
        driver.find_element_by_id("u_simple_requests.short_description").send_keys(comment)
        
        # Enter "IT Connect" for Configuration item
        driver.find_element_by_id("sys_display.u_simple_requests.cmdb_ci").send_keys("IT Connect")
        time.sleep(2)
        
        # Save request number to look up later
        return driver.find_element_by_id("sys_readonly.u_simple_requests.number").get_attribute('value')
    
    # Change to the correct iFrame in uweval    
    def _switch_frame(self, frame):
        self.driver.switch_to_default_content()
        self.driver.switch_to.frame(frame)
    
    # Verify that requests are listed with the correct tag in IT Connect
    def _verify_request_tag(self, request_number, tag):
        self.driver.get("https://www.washington.edu/itconnect-test/myrequest/%s" % request_number)
        time.sleep(7)
        self.assertIn(tag, self.driver.find_element_by_class_name("request_status").text)
    
    # Change the state of the request in uweval   
    def _change_request_state(self, request_number, value):
        self._search_request(request_number)
        # Change request state
        self.driver.find_element_by_id("u_simple_requests.state").send_keys(value)
    
    # Search for the request on uweval and then edit it
    def _search_request(self, request_number):
        driver = self.driver
        driver.maximize_window()
        # Return to uweval
        driver.get("https://uweval.service-now.com/navpage.do")
        time.sleep(4)
        
        # Click "All" to see all Service Requests
        self._switch_frame("gsft_nav")
        try:
		    driver.find_element_by_id("21ec2c746f4f510054aafd16ad3ee436").click()
        except:
		    driver.find_element_by_id("div.c0ff19b26f76510054aafd16ad3ee447").click()
		    time.sleep(2)
		    driver.find_element_by_id("21ec2c746f4f510054aafd16ad3ee436").click()
        time.sleep(4)
        
        # Search for the request
        self._switch_frame("gsft_main")
        driver.find_element_by_class_name("list_search_select").send_keys("nu")
        elem = driver.find_element_by_class_name("list_search_text")
        # The name or NetID for the caller will be entered
        elem.send_keys(request_number)
        elem.send_keys(Keys.RETURN)
        time.sleep(3)
        driver.find_element_by_link_text(request_number).click()
        time.sleep(3)
    
    # Return to uweval and change the state of the request to "Resolved"    
    def _resolve_request(self, request_number):
        driver = self.driver
        self._change_request_state(request_number, "r")
        driver.find_element_by_id("u_simple_requests.comments").send_keys("This is a test.")
        driver.find_element_by_id("u_simple_requests.u_close_code").send_keys("c")
        # Update request
        driver.find_element_by_id("sysverb_update").click()
        time.sleep(3)
    
    # Create an incident request
    def _incident_request(self):
        driver = self.driver
        driver.maximize_window()
        time.sleep(2)
        self._switch_frame("gsft_nav")
        driver.find_element_by_id("14641d70c611228501114133b3cc88a1").click()
        driver.find_element_by_id("14641d70c611228501114133b3cc88a1").click()
        time.sleep(4)
        
        # Select "All" for CI Class Category
        self._switch_frame("gsft_main")
        driver.find_element_by_id("sys_select.incident.u_cmdb_ci_class_category").send_keys("a")
        
        # Enter Caller
        driver.find_element_by_id("sys_display.incident.caller_id").send_keys("Lyndon Coolidge")
        
        # Enter a description
        driver.find_element_by_id("incident.short_description").send_keys("This is an incident test.")
        
        # Enter "IT Connect" for Configuration item
        driver.find_element_by_id("sys_display.incident.cmdb_ci").send_keys("IT Connect")
        time.sleep(2)
        
        # Enter "IT Connect Development" for Assignment Group
        driver.find_element_by_id("sys_display.incident.assignment_group").send_keys("IT Connect Development")
        time.sleep(2)
        
        # Save incident number to look up later
        return driver.find_element_by_id("sys_readonly.incident.number").get_attribute("value")
    
    
    # Asserts that one user cannot see the requests of other users    
    def test01_assert_one_user_cannot_see_another_users_request(self):
        driver = self.driver
        
        # Create new request
        request_number = self._create_new_request("This is a test")
        #request_number = "REQ0084900"
        
        # Click button to submit request
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        try:
            driver.find_element_by_id("sysverb_insert").click()
        except:
            time.sleep(1)
        time.sleep(3)
        self._verify_request_tag(request_number, "Active")
        
        # Login as a different user (lisatest)
        driver.close()
        driver = webdriver.Firefox()
        time.sleep(1)
        netid2.prelogin(driver)
        time.sleep(1)
        driver.get("https://www.washington.edu/itconnect-test/myrequests/")
        time.sleep(3)
        
        # Verify request does not display in lists on IT Connect
        try:
            self.assertNotIn(request_number, driver.find_element_by_id("primary").text)
        except:
            self.assertIn("You have no current requests with UW-IT.", driver.find_element_by_id("primary").text)
        
        # Verify user gets message that the request is not one of their current requests
        driver.get("https://www.washington.edu/itconnect-test/myrequest/%s" % request_number)
        self.assertIn("is not one of your current requests.", driver.find_element_by_id("primary").text)
    
    
    # broken: uwconnect doesn't update the request with the "Awaiting User Info" tag
    # MyRequests - Assert that the correct status is displayed for tickets
    @unittest.expectedFailure
    def test02_create_active_request_on_uweval(self):
        driver = self.driver
        # Create new request
        request_number = self._create_new_request("This is a test")
        #request_number = "REQ0084927"
        # Click button to submit request
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        try:
            driver.find_element_by_id("sysverb_insert").click()
        except:
            time.sleep(1)
        time.sleep(5)
        
        # Go to IT Connect and verify request is listed with "Active" tag
        self._verify_request_tag(request_number, "Active")
        
        # **uweval is broken - request status doesn't update to "awaiting user info"
        # Return to uweval and change the state of the request to "Awaiting User Info"
        self._change_request_state(request_number, "aw")
        # Update request
        driver.find_element_by_id("sysverb_update").click()
        time.sleep(3)
        
        # Go to IT Connect and verify request is listed with "Awaiting User Info" tag
        self._verify_request_tag(request_number, "Awaiting User Info")
        
        # Return to uweval and change the state of the request to "Resolved"
        self._resolve_request(request_number)
        
        # Go to IT Connect and verify request is listed with "Resolved" tag
        self._verify_request_tag(request_number, "Resolved")
        
        # Return to uweval and change the request state back to "Active"
        self._change_request_state(request_number, "ac")
        
        # Change the caller to another user
        driver.find_element_by_id("sys_display.u_simple_requests.u_caller").clear()
        driver.find_element_by_id("sys_display.u_simple_requests.u_caller").send_keys("lisatest")
        # Add original caller NetID to watch list
        driver.find_element_by_id("add_me_locked.u_simple_requests.watch_list").click()
        time.sleep(3)
        # Update request
        driver.find_element_by_id("sysverb_update").click()
        time.sleep(3)
        
        # Return to itconnect and verify requested is listed with "Active" and "Watching" tags
        self._verify_request_tag(request_number, "label label-success")
        self._verify_request_tag(request_number, "label label-warning")
    
    
    # broken: watcher's get a notification that they aren't allowed to see the request
    # Assert that both the caller and members of the watch list can comment on a ticket and are 
    # displayed correctly
    #@unittest.expectedFailure
    def test03_assert_caller_and_watchers_can_comment(self):
        driver = self.driver
        
        # Create new request
        request_number = self._create_new_request("This is a test")
        #request_number = "REQ0180623"
        
        # Click button to submit request
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        try:
            driver.find_element_by_id("sysverb_insert").click()
        except:
            time.sleep(1)
        time.sleep(5)
        
        self._search_request(request_number)
        
        # Add user1, user2, and user3 to watch list
        self._switch_frame("gsft_main")
        driver.find_element_by_id("u_simple_requests.watch_list_unlock").click()
        driver.find_element_by_id("text.value.u_simple_requests.watch_list").send_keys("lisatest@uw.edu")
        driver.find_element_by_id("text.value.u_simple_requests.watch_list").send_keys(Keys.RETURN)
        driver.find_element_by_id("text.value.u_simple_requests.watch_list").send_keys("janeho@uw.edu")
        driver.find_element_by_id("text.value.u_simple_requests.watch_list").send_keys(Keys.RETURN)
        
        driver.find_element_by_id("sysverb_update").click()
        time.sleep(2)
        
        # Verify created incident shows in list on IT-Connect
        driver.get("http://www.washington.edu/itconnect-test/myrequests")
        time.sleep(2)
        self.assertIn(request_number, driver.find_element_by_id("primary").text)
        
        # Add a comment and submit it
        driver.get("https://www.washington.edu/itconnect-test/myrequest/%s" % request_number)
        driver.find_element_by_class_name("form-control").send_keys("Testing as Caller")
        driver.find_element_by_tag_name("button").click()
        self.assertIn("Testing as Caller", driver.find_element_by_id("primary").text)
        self.assertIn("lyndcoo", driver.find_element_by_id("primary").text)
        
        # Log out and log in using user2's NedtID
        driver.close()
        driver = webdriver.Firefox()
        
        # Login as a different user (lisatest)
        netid2.prelogin(driver)
        time.sleep(3)
        
        # Return to the request page and add a comment
        driver.get("https://www.washington.edu/itconnect-test/myrequest/%s" % request_number)
        driver.find_element_by_class_name("form-control").send_keys("Testing as Watcher1")
        driver.find_element_by_tag_name("button").click()
        self.assertIn("Testing as Watcher1", driver.find_element_by_id("primary").text)
        self.assertIn("lisatest", driver.find_element_by_id("primary").text)
        
        # Log out and log in using user3's NedtID
        driver.close()
        driver = webdriver.Firefox()
        
        # Login as a third user (janeho)
        netid3.prelogin(driver)
        time.sleep(3)
        
        # Return to the request page and add a comment
        driver.get("https://www.washington.edu/itconnect-test/myrequest/%s" % request_number)
        driver.find_element_by_class_name("form-control").send_keys("Testing as Watcher2")
        driver.find_element_by_tag_name("button").click()
        self.assertIn("Testing as Watcher2", driver.find_element_by_id("primary").text)
        self.assertIn("janeho", driver.find_element_by_id("primary").text)
    
    # Asserts that refreshing the page after submitting a comment does not post the comment twice
    def test04_assert_reloading_page_after_submitting_comment_does_not_post_comment_twice(self):
        driver = self.driver
        
        # Create new request
        request_number = self._create_new_request("This is a double comment test")
       
	    # Click button to submit request
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        try:
            driver.find_element_by_id("sysverb_insert").click()
        except:
            time.sleep(1)
        time.sleep(5)
        #request_number = "REQ0084927"
        
        # Verify created request shows in list
        driver.get("http://www.washington.edu/itconnect-test/myrequests")
        time.sleep(2)
        self.assertIn(request_number, driver.find_element_by_id("primary").text)
        
        # Add a comment and submit it
        driver.get("https://www.washington.edu/itconnect-test/myrequest/%s" % request_number)
        driver.find_element_by_class_name("form-control").send_keys("I should only see this once.")
        driver.find_element_by_tag_name("button").click()
        self.assertIn("I should only see this once.", driver.find_element_by_id("primary").text)
        
        # Refresh the page and verify the comment isn't posted twice
        driver.refresh()
        elem = driver.find_elements_by_xpath("//li[contains(.,'I should only see this once.')]")
        assert len(elem) == 1
    
    
    def test05_assert_requests_and_incidents_displayed_in_separate_lists(self):
        driver = self.driver
        
        # Create new request
        request_number = self._create_new_request("This is a test.")
        # Click button to submit request
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        try:
            driver.find_element_by_id("sysverb_insert").click()
        except:
            time.sleep(1)
        time.sleep(5)
        
        driver.get("https://uweval.service-now.com/navpage.do")
        time.sleep(3)
        #request_number = "REQ0180626"
        
        # Save incident number to look up later
        incident_number = self._incident_request()
        
        # Submit incident
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(3)
        #incident_number = "INC0074689"
        
        # Verify created incident shows in list on IT-Connect
        driver.get("http://www.washington.edu/itconnect-test/myrequests")
        time.sleep(2)
        self.assertIn(incident_number, driver.find_element_by_id("primary").text)
        
        # Verify created request shows in list
        self.assertIn(request_number, driver.find_element_by_id("primary").text)
        
        # Verify that incidents and requests are shown in different lists
        lists = driver.find_elements_by_class_name("request-list")
        x=1
        for comment in lists:
            text = comment.find_elements_by_css_selector("request-list-number>span")
            if x == 1:
                for element in text:
                    self.assertIn("INC", element.text)
            if x == 2:
                for element in text:
                    self.assertIn("REQ", element.text)
            x+=1
        
    
    
    # Verify that comments are sorted chronologically, descending
    def test01_assert_comments_sorted_chronologically_descending(self):
        driver = self.driver
        
        # Create new request
        request_number = self._create_new_request("This is a test")
        
        # Click button to submit request
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        try:
            driver.find_element_by_id("sysverb_insert").click()
        except:
            time.sleep(1)
        time.sleep(5)
        #request_number = "REQ0084914"
        
        # Add a comment and submit it
        driver.get("https://www.washington.edu/itconnect-test/myrequest/%s" % request_number)
        
        driver.find_element_by_class_name("form-control").send_keys("First")
        driver.find_element_by_tag_name("button").click()
        assert "First" in driver.page_source
        
        # Add a second comment and submit it
        driver.find_element_by_class_name("form-control").send_keys("Second")
        driver.find_element_by_tag_name("button").click()
        assert "Second" in driver.page_source
        
        
        # Verify the second comment is listed above the first
        comments = driver.find_elements_by_class_name("media")
        for comment in comments:
            text = comment.find_element_by_css_selector("pre").text
            if text == "Second":
                second_comment = comment
            if text == "First":
                first_comment = comment
        
        first_date_comment = first_comment.find_element_by_class_name("create-date").text
        second_date_comment = second_comment.find_element_by_class_name("create-date").text
        
        first_date = time.strptime(first_date_comment, "%m-%d-%Y %H:%M:%S")
        second_date = time.strptime(second_date_comment, "%m-%d-%Y %H:%M:%S")
        
        assert first_date < second_date
    
    @unittest.expectedFailure    
    def test07_assert_ticket_attachments_displayed_correctly_and_downloadable(self):
        driver = self.driver
        # Create new request with file attached
        request_number = self._create_new_request("This is an attachments test")
        driver.find_element_by_id("header_add_attachment").click()
        driver.find_element_by_id("header_add_attachment").click()
        time.sleep(3)
        driver.find_element_by_id("attachFile").send_keys("/home/amelia/bitcoin.pdf")
        driver.find_element_by_id("attachButton").click()
        driver.find_element_by_id("closeButton").click()
        time.sleep(3)
        
        # Click button to submit request
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        try:
            driver.find_element_by_id("sysverb_insert").click()
        except:
            time.sleep(1)
        time.sleep(5)
        
        # Restart the browser
        driver.close()
        driver = webdriver.Firefox()
        netid.prelogin(driver)
        time.sleep(3)
        
        # Go to IT Connect
        driver.get("https://www.washington.edu/itconnect-test/myrequests/")
        
        # Verify created request shows in list
        assert request_number in driver.page_source
        
        driver.get("https://www.washington.edu/itconnect-test/myrequest/%s" % request_number)
        
        # Attachments aren't showing up in IT Connect
    
    
    # NOT WORKING: Getting the "connection refused" error
    def test08_assert_uwit_support_staff_comments_anonymized(self):
        driver = self.driver
        
        # Create new request
        request_number = self._create_new_request("This is a test.")
        # Click button to submit request
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        driver.find_element_by_id("sysverb_insert").click()
        time.sleep(2)
        try:
            driver.find_element_by_id("sysverb_insert").click()
        except:
            time.sleep(1)
        time.sleep(5)
        #request_number = "REQ0084838"
        
        # Log in as a different user and add a comment
        driver.close()
        driver = webdriver.Firefox()
        self.driver = driver
        netid2.prelogin(driver)
        time.sleep(3)
        driver.get("https://uweval.service-now.com/navpage.do")
        self._search_request(request_number)
        
        # Add a comment
        driver.find_element_by_id("u_simple_requests.comments").send_keys("Testing as Support Staff")
        driver.find_element_by_id("sysverb_update").click()
        time.sleep(3)
        
        # Log out and log in as orginial user
        driver.close()
        driver = webdriver.Firefox()
        self.driver = driver
        netid.prelogin(driver)
        time.sleep(1)
        
        # Go to itconnect and verify request is in the list
        driver.get("http://www.washington.edu/itconnect-test/myrequests")
        self.assertIn(request_number, driver.page_source)
        
        driver.get("https://www.washington.edu/itconnect-test/myrequest/%s" % request_number)
        time.sleep(3)
        
        self.assertIn("Testing as Support Staff", driver.find_element_by_class_name("media").text)
        self.assertIn("UW-IT SUPPORT STAFF", driver.find_element_by_class_name("media").text)
    

if __name__ == '__main__':  
    unittest.main()  
