# Notify-after-render

DESCRIPTION
"Notify after render" send different internet notifications after an automatic long render and afford to be during this time away from the computer.

IMPORTANT NOTE !
Because renders are made automatically, this add-on need the use of "Auto save render" add-on together. But the two add-ons are independant in operations.

Installation
Enable the script

Download the latest version of "Notify after render" from the link above.
Open Blender and go to the addons tab in User Preferences.
Click the Install Addon button at the bottom of the addons panel and find the *.zip file probably in your download folder.
Then enter "Notify" in the search field. And activate the Render: Notify after render addon by checking the checkbox next right to it.
You should now have 5 buttons below the presentation: This is the 3 choices of notifications and 2 for tools, if you activate them, preferences must appear to the right.


In Blender the Notification buttons appear at the bottom of the Properties > Render panel that looks something like below.

How to Use
Notify after render ui.png
Simply define the preferences of your internet services when you want to use it. This preferences are saved with the blender config as the add-on is not disabled.

During your job with Blender, you need simply choose what buttons to activate in the main render panel without to go in the user preferences and ...... go to make your course in city shops, off' course with your cellphone (and solid batteries).


You must receive ->
- a sms or an email ("Blender has finished!") with a message like this:

At :Sun, 26 Apr 2015 11:26:06 +0200, your render [ TestBlend_001.png ] is ready!

And if "Use Dropbox" is checked, you could go to the web site of your dropbox service and see the result....and send it to your customer, friends, ... may be.

Warning: You must make some try of your setups to verify all run well.

Preferences
SMS service URL: Url created by your cellphone provider to send sms to your cellphone (warning: without the message in the link, please, the add-on make its own):

https ://smsapi.free-mobile.fr/sendmsg?user=XXXXXXXX&pass=XXXXXXXXXXXXXX


Mail: The adress mail you want to send a notification (like xxx@yyy.zzz).

Password: Your personal password to this mail account.

SMTP server: The name of your SMTP serveur (conventionnal like smtp.yyy.zzz).


Dropbox folder path: Choose the created folder in your desktop folder of your dropbox service to send the image rendering. Warning: Only absolute path!


Tools to Load/Save
You remark if you disabled (willingly or by error) the add-on, all your preferences are lost like other add-ons (normally). That's why I create a load/save preferences tool to avoid to re-do the long process. In plus, you could archiving several preferences files according to the internets services used.

How
The preferences file extension is .nar

To start, fill preferences and use the "Save" button to choose where to save your preferences. In the window that opens, you discover an option at the bottom left, To save -> With specifications.

Enabled: The file name you choose will be added to the name standard like this: notify_after_render_xxxxxx.nar.

Disabled: The preferences will be saved in a file notify_after_render.nar unique name.

Must be known!
SMS notification: Exemple of this service is here at the FreeMobile provider: Freebox

If your cellphone is a verizon cellphone, you can receive a sms by a mail account filter setup like this too: http://answers.google.com/answers/threadview/id/730149.html so this SMS parameter is unusable for you but send Mail yes and add a filter for SMS!


Mail notification: Issue by example at GMAIL, you could activated a special security rules to prevent sending email through unprotected Application. Then if this service is activated, go in your gmail prefs and disabled it absolutelly:

http://sitarchi.free.fr/scripts/img/gmail_security.png


Use of a Dropbox service: Several dropbox service like Dropbox Inc., GoogleDrive, oodrive, onedrive, Box, etc... use a "desktop application" to sync with their website, that's why we can copy the "render of "auto save render" add-on to a special dropbox folder. It's the process of my add-on. You must create this dropbox folder before the use of Blender off'course!

Release Notes
1.0.0 – First public release
