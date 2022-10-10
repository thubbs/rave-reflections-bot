import json
import random
import textwrap
import tweepy
from datetime import date

def make_post(chosen_id, data):
	chosen_comment = (next(item for item in data['content'] if item["id"] == chosen_id))
	# If comment, quote marks and URL fit in single tweet
	if len(chosen_comment['comment']) <= 254:
		post_content = "\'" + chosen_comment['comment'] + "\' " + chosen_comment['URL']
		thread = False
	else:
		thread = True
		post_content = textwrap.wrap(chosen_comment['comment'], 248, break_long_words=False)
		for i, line in enumerate(post_content):
			# If first tweet
			if i == 0:
				post_content[0] = "\'" + post_content[0] + " ...\'" 
				# Add '1 of y' tweet thread indicator in format 'x/y'
				post_content[0] = post_content[0] + " 1/" + str(len(post_content))
				post_content[0] = post_content[0] + " " + chosen_comment['URL']
			# If last tweet
			elif (i + 1) == len(post_content): 
				post_content[i] = "\'... " + post_content[i] + "\'" 
				# Add 'y of y' tweet thread indicator in format 'x/y'
				post_content[i] = post_content[i] + " " + str(len(post_content)) + "/" + str(len(post_content))
			else: 
				post_content[i] = "\'... " + post_content[i] + " ...\'" 
				post_content[i] = post_content[i] + " " + str(i+1) + "/" + str(len(post_content)) #add 'x of y' tweet thread indicator in format 'x/y'	
	just_post(post_content, thread)
	#just_post_test(post_content, thread)
	update_JSON(chosen_id, data)

def update_JSON(chosen_id, data):
	today = date.today()
	date_stamp = today.strftime("%Y-%m-%d")
	for item in data['content']:
		if item['id'] == chosen_id:
			item['lastPosted'] = date_stamp
	# Remove temporary ids before writing back to json
	for item in data['content']:
		del item['id']
	a_file = open("data.json", "w")
	json.dump(data, a_file, indent=4, sort_keys=False)
	a_file.close()

def just_post(msg, thread):
	f = open('config.json')
	config = json.load(f)
	f.close()

	client = tweepy.Client(consumer_key=config['consumer_key'], consumer_secret=config['consumer_secret'], access_token=config['access_token'], access_token_secret=config['access_token_secret'])

	if thread == False:
		client.create_tweet(text=msg)
	else:
		for i, post in enumerate(msg):
			if i == 0:
				response = client.create_tweet(text=post)
			else:
				tweet_id = response.data['id']
				response = client.create_tweet(text=post, in_reply_to_tweet_id=tweet_id)

def just_post_test(msg, thread):
	if thread == False:
		print(msg)
	else:
		for post in msg:
			print(post)

def main():
	f = open('data.json')
	data = json.load(f)
	f.close()

	# Iterating through the list of dicts, adding ids for handling
	for i, item in enumerate(data['content']):
		item["id"] = i

	unposted_ids = []
	for x in data['content']:
	    if x['lastPosted'] == "null":
	    	unposted_ids.append(x['id'])

	# If there are unposted comments, choose a random one, otherwise choose least recent post
	if len(unposted_ids) != 0:
		random_unposted_id = random.choice(unposted_ids)
		make_post(random_unposted_id, data)
	else:
		#sort by lastPosted
		data['content'] = sorted(data['content'],key=lambda k: k['lastPosted'])
		posted_id = data['content'][0]['id']
		make_post(posted_id, data)

if __name__ == "__main__":
    main()