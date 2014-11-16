import praw
import gspread
import time
import sys
from pprint import pprint

#def dump(obj):
  #for attr in dir(obj):
    #print "obj.%s = %s" % (attr, getattr(obj, attr))


gc = gspread.login("[GOOGLE ACCOUNT EMAIL]", "[GOOGLE ACCOUNT PASSWORD")
#Assistance Verification
spreadsheet = gc.open('Santa\'s Little Helpers Registration (Responses)')
removedsheet = gc.open('Already Removed').sheet1
worksheet = spreadsheet.get_worksheet(0)
print ("There are " + str(worksheet.row_count) + " entries")

user_agent = ("SLH Verifier u/yes_it_is_weird")
r = praw.Reddit(user_agent=user_agent)
key_words = ['[request]']
r.login('[REDDIT USERNAME]','[REDDIT PASSWORD]')
print("made it")

alreadyprocessed = []
subreddit = r.get_subreddit('SantasLittleHelpers')

flared = 0
lastLoad = time.clock()
print("reloaded spreadsheet")
while True:
    time.sleep(30)
    gottenContent = True
    try:
      submissions = subreddit.get_new(limit = 5)
    except:
      print("Error gathering content. Continuing to try!")
      gottenContent = False
    if gottenContent == False:
      continue
    for submission in submissions:
        if str(submission.link_flair_css_class) == 'request':
            redditor = submission.author
            try:
              flair = r.get_flair(subreddit,redditor)
            except:
              print("problem getting flair")
              break
            #r.set_flair(redditor,subreddit,'Registered')
        
            if (str(flair.get('flair_css_class')) == 'registered'):
                garbage = 0
            else:
                loaded = 0
                while loaded == 0:
                  try:
                    approved = worksheet.col_values(2)
                    loaded = 1
                  except:
                    loaded = 0
                #print("reloaded spreadsheet")
                found = False
                for string in approved:
                    if string != None:
                      if string.lower() == redditor.name.lower():
                          found = True
                          break
                del approved[:]
                if found == True:
                    print(redditor.name + " was on the list. Adding flair. Total(" + str(flared)+ ")")
                    flared += 1
                    subreddit.set_flair(redditor,flair_css_class='registered', flair_text = '')
                else:
                    idList = removedsheet.col_values(1)
                    found = False
                    for string in idList:
                        if string.lower() == str(submission.id).lower():
                            found = True
                            break
                    del idList[:]
                    if (found == True):
                      garbage = 0
                      #print('They were not on the list, but I have removed this post already')
                    else:   
                      #print(redditor.name + " is not on the list. Taking action")
                      checking = 1
                      message = '***Your post has been removed because you did not register. Please fill out the following form:***\n\n[https://docs.google.com/forms/d/154YjCdV-0zSDrCA7C5P_EiuXZIOGMD2MEniRquAHniI/viewForm](https://docs.google.com/forms/d/154YjCdV-0zSDrCA7C5P_EiuXZIOGMD2MEniRquAHniI/viewForm)\n\n***Contact the mods after you have completed this form and we will reinstate your post.***\n\n[http://www.reddit.com/message/compose?to=%2Fr%2FSantasLittleHelpers](http://www.reddit.com/message/compose?to=%2Fr%2FiSantasLittleHelpers)'
                      r.send_message(submission.author,'r/Santas Little Helpers Mod Message',message,captcha = None)
                      print("Sent message to " + submission.author.name)
                      removedsheet.add_rows(1)
                      removedsheet.update_cell(removedsheet.row_count,1,submission.id)
                      submission.remove()
        #else:
            #print("found one that wasn't a request")
    break;
