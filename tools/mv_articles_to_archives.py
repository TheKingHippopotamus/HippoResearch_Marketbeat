"""
The Archive tools is simple.  
Every 2 days the tools are cleaning the article folder from the oldest and moving them to  /Users/kinghippo/Documents/rssFeed/marketBit_archives/public/archive 
the tool are manage with json for Tracking . 
- first the tool are checking the corrent date & time . 
- the tool search in articles folder if have any article in the folder are old more 2 days (48 hours (counting from 00:05 at the night))
- if the tool find a file are oldenst then 2 days he move the files to  /Users/kinghippo/Documents/rssFeed/marketBit_archives/public/archive 
_ add to json Tracking documentation 
- if not find a file also adding the "not find any ..." json Tracking documentation  

"""