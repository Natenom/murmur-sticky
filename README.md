# sticky.py

Do not use this script, try the version which was ported to MuMo: https://github.com/Natenom/mumo-sticky.

## Description
A user who gets the sticky status can't do more than sitting in one special channel.
Even admins will loose their permissions while in ST status :)

## Features
* While in sticky status, nobody can do anything else than talking in the sticky channel.
* A user can't remove his sticky status even if he is an admin.
* A user, even if admin, can't set another user to sticky status while he is in this status.
* Sticky status is stored over reconnects.
* When reconnecting, a sticky user gets a warning that he is still in sticky status.
* Uses callbacks to display two context menu entries.
* You can't set sticky on yourself.
* When the status is removed the user switches back to the previous channel.

## What you need to do
* Create a channel somewhere in your server tree...
* Create a group "stickyusers" and add ACL entries which deny everything except Speak and Enter in your sticky channel (and Traverse for all prior levels).
* Set st_channel= to the id of your sticky channel.
* Set st_group= to the name of your "stickyusers" group.
* Change the other self explaining stuff to your needs.
* Have fun :)

