import praw
import time
from pprint import pprint
import gspread
reddit = praw.Reddit('script for flairing brand new accounts in a subreddit. By: /u/exoendo')

gc = gspread.login("[GOOGLE USERNAME]", "[GOOGLE PASSWORD]")
#Assistance Verification
spreadsheet = gc.open('Page Two Assistance Verification - Starting July 2014')
removedsheet = gc.open('Already Removed').sheet1
worksheet = spreadsheet.get_worksheet(0)

########################################## CONFIGURATION ##################################################

USERNAME = '[REDDIT USERNAME]'			# YOUR REDDIT USERNAME
PASSWORD = '[REDDIT PASSWORD]'			# YOUR REDDIT PASSWORD
SUBREDDIT = 'assistance'				# SUBREDDIT TO POST TO (NO 'r/' ETC.. JUST NAME)
FLAIR_TEXT = 'New User'					# FLAIR TEXT YOU WANT FOR NEWBIES
NEWUSER_CLASS = "newuser"
REGISTERED_CLASS = "registered"
REGISTEREDNEWUSER_CLASS = "registerednewuser"
REQUEST_TEXT = 'request'
REGISTERED_TEXT = 'registered'
DAYS = 60						# AGE OF ACCOUNTS WE FLAIR (LESS THAN AND EQUAL TO)
WAIT_TIME = 900						# TIME (IN SECONDS) TO WAIT EACH TIME WE RUN THIS

MESSAGE = '***Your post has been removed because you did not register. Please fill out the following form:***\n\n[https://docs.google.com/forms/d/1P31DGkQ8L1xD_rNZTFdn_ES2BoNydtW74_8poBITk2U/viewform?c=0&w=1](https://docs.google.com/forms/d/1P31DGkQ8L1xD_rNZTFdn_ES2BoNydtW74_8poBITk2U/viewform?c=0&w=1)\n\n***Contact the mods after you have completed this form and we will reinstate your post.***\n\n[http://www.reddit.com/message/compose?to=%2Fr%2FAssistance](http://www.reddit.com/message/compose?to=%2Fr%2FAssistance)\n\n*Please do not reply to this. I am a bot*'

############################################################################################################

# Boiler Plate
reddit.login(username=USERNAME, password=PASSWORD)
subreddit = reddit.get_subreddit(SUBREDDIT)
already_checked = set()

print ("There are " + str(worksheet.row_count) + " entries")
try:
    # Flair Newbies
    print ('\nChecking new queue..')

    for link in subreddit.get_new(limit=10):
	if link.link_flair_css_class != REQUEST_TEXT:
            print (link.link_flair_css_class)
	    continue
        user = reddit.get_redditor(str(link.author))
        newb = False
        if subreddit.get_flair(user)['flair_css_class'] == NEWUSER_CLASS or subreddit.get_flair(user)['flair_css_class'] == REGISTEREDNEWUSER_CLASS :
            newb = True
            print (user.name + ' already noob')
        if not newb:
            # Getting Account Age:
            difference_seconds = time.time() - user.created_utc
            account_age_days = difference_seconds / 86400
            if account_age_days > int(DAYS):
                already_checked.add(str(user.name))
            else:
		if subreddit.get_flair(user)['flair_css_class'] == REGISTERED_CLASS:
                    subreddit.set_flair(user, flair_css_class = REGISTEREDNEWUSER_CLASS)
                else:
                    subreddit.set_flair(user, flair_css_class = NEWUSER_CLASS)
                
                #already_checked.add(str(user.name))
                print (subreddit.get_flair(user))
                #print ('--> Flaired %s as %s.' % (str(user.name), FLAIR_TEXT))
        print ("done noob checking phase")
        if link.link_flair_css_class == REQUEST_TEXT :
            if subreddit.get_flair(user)['flair_css_class'] == REGISTERED_CLASS or subreddit.get_flair(user)['flair_css_class'] == REGISTEREDNEWUSER_CLASS :
                print (str(user.name) + " is already registered!")
                garbage = 0
            else :
		print (str(user.name) + " doesn't have the registered flair. Checking it out")
                loaded = 0
                #approved = set()
		approved = []
                while loaded == 0:
                    try:
			print("trying to load")
                        #approved = worksheet.col_values(2)
			cells = worksheet.range('B'+str(worksheet.row_count-500)+':B'+str(worksheet.row_count))
                        loaded = 1
                    except:
			print("loading exception")
                        loaded = 0
                found = False
		print ("translating cells")
		for cell in cells:
		    approved.append(str(cell.value))
		print ("loaded the spreadsheet for checking")
                for string in approved:
                    if string != None:
                        if string.lower() == user.name.lower():
                            found = True
			    print (str(user.name) + " was in the sheet")
                            break
                del approved[:]
		print ("done the checking phase")
                if found == True:
                    print (str(user.name) + " is being flaired as registered!")
                    if subreddit.get_flair(user)['flair_css_class'] == NEWUSER_CLASS:
                        subreddit.set_flair(user,flair_css_class = REGISTEREDNEWUSER_CLASS)
                    else:
                        subreddit.set_flair(user,flair_css_class= REGISTERED_CLASS)
                else:
		    print ("needing to check the already removed sheet")
                    idList = removedsheet.col_values(1)
                    found = False
                    for string in idList:
                        if string.lower() == str(link.id).lower():
                            found = True
                            break
                    del idList[:]
                    if (found == True):
                        garbage = 0
                        print('They were not on the list, but I have removed this post already')
                    else:
                        reddit.send_message(user.name,'r/Assistance BOT Message',MESSAGE, captcha = None)
                        print("Sent message to " + user.name)
                        removedsheet.add_rows(1)
                        removedsheet.update_cell(removedsheet.row_count,1,link.id)
                        link.remove()

    # Un-flair Aged Accounts
    print ('\nChecking flaired users..')

    for item in subreddit.get_flair_list(limit=None):
        if item['flair_css_class'] != NEWUSER_CLASS and item['flair_css_class'] != REGISTEREDNEWUSER_CLASS:
            continue
        user = reddit.get_redditor(item['user'])
        difference_seconds = time.time() - user.created_utc
        account_age_days = difference_seconds / 86400

        if account_age_days <= int(DAYS):
            continue
        if subreddit.get_flair(user)['flair_css_class'] == NEWUSER_CLASS:
            subreddit.delete_flair(str(user.name))
        else:
            subreddit.set_flair(user, flair_css_class = REGISTERED_CLASS)
        print ('--> Deleted flair for user %s.' % (str(user.name)))

    print ('\nAll done.')
    pauseMinutes = int(WAIT_TIME) / 60
        #print ('Pausing for %i minutes.' %pauseMinutes)
        #time.sleep(int(WAIT_TIME))

except Exception as e:
    print (str(e))
