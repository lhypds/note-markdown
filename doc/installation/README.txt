
macOS: Opening the App for the First Time
==========================================


As Apple blocks apps not signed with an Apple Developer certificate.  
An "Apple Developer Certificate" cost 99$ per year...
Sorry, but, I don't want to pay.  


To open it anyway, follow these steps:


Method 1: System Preferences
----------------------------------------------------------
1. Try to run the app. You will see a warning dialog — click "OK".
2. Open System Preferences > Security & Privacy.
3. Click the "General" tab.
4. You will see a message like:
   '"note" was blocked from use because it is not from an identified developer.'
5. Click "Open Anyway".
6. A confirmation dialog will appear — click "Open" to confirm.


Method 3: Terminal (any macOS version)
---------------------------------------
Run the following command to remove the quarantine attribute:

    xattr -d com.apple.quarantine /path/to/note

Replace /path/to/note with the actual path to the binary. After this, you
can run the app normally.

Note: You only need to do this once per installation.
