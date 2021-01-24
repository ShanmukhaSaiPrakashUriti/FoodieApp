from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import zomatopy
import json

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class ActionVerifyCity(Action) :
    def name(self):
        return 'action_verify_city'
	
    def run(self, dispatcher, tracker, domain):
        cities = ['ahmedabad', 'bangalore', 'chennai', 'delhi', 'hyderabad','kolkata', 'mumbai', 'pune', 'agra',
        'ajmer', 'aligarh', 'amravati', 'amritsar', 'asansol', 'aurangabad', 'bareilly', 'belgaum', 'bhavnagar', 
        'bhiwandi', 'bhopal', 'bhubaneswar', 'bikaner', 'bilaspur', 'bokaro', 'chandigarh', 'coimbatore', 'cuttack', 
        'dehradun', 'dhanbad', 'bhilai', 'durgapur', 'dindigul', 'erode', 'faridabad', 'firozabad', 'ghaziabad', 
        'gorakhpur', 'gulbarga', 'guntur', 'gwalior', 'gurgaon', 'guwahati', 'hamirpur',	'hubli–dharwad', 'indore',
        'jabalpur', 'jaipur', 'jalandhar', 'jammu', 'jamnagar', 'jamshedpur', 'jhansi',	'jodhpur', 'kakinada', 'kannur',
        'kanpur', 'karnal', 'kochi', 'kolhapur', 'kollam', 'kozhikode', 'kurnool', 'ludhiana', 'lucknow', 'madurai', 
        'malappuram', 'mathura', 'mangalore',  'meerut', 'moradabad', 'mysore', 'nagpur', 'nanded', 'nashik', 'nellore', 
        'noida', 'patna', 'pondicherry',	 'purulia', 'prayagraj', 'raipur', 'rajkot',	'rajahmundry', 'ranchi',
        'rourkela', 'salem', 'sangli',	 'shimla', 'siliguri', 'solapur', 'srinagar', 'surat', 'thanjavur', 'thiruvananthapuram', 'thrissur',
        'tiruchirappalli','tirunelveli', 'tiruvannamalai', 'ujjain', 'vijapur', 'vadodara', 'varanasi', 'vasai-virar City', 
        'vijayawada', 'visakhapatnam', 'vellore',	'warangal']
           
        loc = tracker.get_slot('location')
        
        if(loc.lower() not in cities):
            dispatcher.utter_message("Sorry ! We do not operate in that area yet.Can you specify some other location")
            return [SlotSet('location',None), SlotSet('valid_location',False)]
        else:
            return [SlotSet('location',loc),SlotSet('valid_location',True)]

class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_search_restaurants'
		
	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"0c86ab66477137a1932d60111ad07b96"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		price = tracker.get_slot('price')
		location_detail=zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
		cuisines_dict={'american':1,'chinese':25,'mexican':73,'italian':55,'north indian':50,'south indian':85}
		results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), limit=1500)
		d = json.loads(results)
		response=""
		price_min = 0
		price_max = 99999
		if price == 'low':
			price_max = 300
		elif price == 'mid':
			price_min = 300
			price_max = 700
		elif price == 'high':
			price_min = 700
		else:
			price_min = 300
			price_max = 9999
		iter = 0
		res_found = 0
		while(True):
			results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine.lower())), limit=20,start=iter*20+1)
			d = json.loads(results)
			if (d['results_found'] == 0 & iter == 0):
				response= "no results"
			elif d['results_found'] == 0 :
				break;
			else:
				for restaurant in d['restaurants']:
					if restaurant['restaurant']['average_cost_for_two'] > price_min and restaurant['restaurant']['average_cost_for_two'] < price_max :
							response=response+ "Found "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+" has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating'] +"\n"
							res_found = res_found +1
					if res_found==5:
						break;
			if res_found==5:
				break;
			else:
				iter = iter + 1
		if res_found == 0:
			response= "no results"
			dispatcher.utter_message("-----"+response)
			return [SlotSet('location',None),SlotSet('cuisine',None),SlotSet('price',None)];
				
		
		dispatcher.utter_message("-----"+response)
		return [SlotSet('location',loc),SlotSet('cuisine',cuisine),SlotSet('price',price)]

class ActionSendEmail(Action):
	def name(self):
		return 'action_send_email'
		
	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"0c86ab66477137a1932d60111ad07b96"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		price = tracker.get_slot('price')
		email = tracker.get_slot('emailid')
		location_detail=zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
		cuisines_dict={'american':1,'chinese':25,'mexican':73,'italian':55,'north indian':50,'south indian':85}
		response=""
		subject = "Top "+ cuisine + " restaurants in " + loc
		price_min = 0
		price_max = 99999
		if price == 'low':
			price_max = 300
		elif price == 'mid':
			price_min = 300
			price_max = 700
		elif price == 'high':
			price_min = 700
		else:
			price_min = 300
			price_max = 9999
		iter = 0
		rest_found = 0
		
		while(True):
			results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine.lower())), limit = 20,start=iter*20+1)
			found = json.loads(results)
			if found['results_found'] == 0 & iter== 0:
				response= "no results"
			elif found['results_found'] == 0 :
				break;
			else:
				for restaurant in found['restaurants']:
					if restaurant['restaurant']['average_cost_for_two'] > price_min and restaurant['restaurant']['average_cost_for_two'] < price_max :
							response=response+ str(rest_found+1) +". "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+" has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating'] +" and average cost for two people is " + str(restaurant['restaurant']['average_cost_for_two']) +"\n"
							rest_found = rest_found +1
					if rest_found==10:
						break;
			if rest_found==10:
				break;
			else:
				itr = iter+1
		if rest_found == 0:
			response= "no results"

		sendmai = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		sendmai.login("chatbots.nlp@gmail.com", "Chat@1234")
		msg = EmailMessage()
		msg['Subject'] = subject 
		msg['From'] = "chatbots.nlp@gmail.com"
		msg['To'] = email
		msg.set_content(response)
		sendmai.sendmail('chatbots.nlp@gmail.com',email,msg.as_string())
		dispatcher.utter_message("Mail Sent. Thank You!!!")
		return ;