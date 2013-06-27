kome
=========

kome is a python library to output the logs of the users.

Concept
--------

kome define two types of logs.One is called Actionlog,and another is called derived log.

Actionlog is the log of user`s actions,while derived log is the outcomes of the actions.
Each log map single log to single user.In other word,kome does only output user releated logs.

Actionlog
--------------

Actionlog is the log of user`s actions:paid,did Gache,did battle,did help someone...etc

You need to follow a simple rule to use Actionlog that you must not output log from non-acted user.For instance,if A attack B,you may outout the log of A but not B,as 
A commit the action of attacking while B did not commit any action.


Derived log
---------------

Derived log is the outomes of the actions:Item increased as user "paid",card increased as user "do gacha",money increase as user "participate" in battle....etc

You may easily find out that deicative log is related to some particuler action.Key concept it that user`s action will bring some sort of consequence such as increase or decrease of 
items ,cards,or points.

Structure
-----------

Sender,ActionLog,Derivedlog are the three main class.

Sender is to determine the output address of log.You may choose syslog,fluentd or sysout depends on your situations.

ActionLog is the class to output action logs.User`s action will be outputted by this class.

DerivedLog is the class to outout dericative logs. 
DerivedLog is returned with related actionlog,eachtime you set to do so. 

Usage
--------

1. Initialize log output ::

 sender = Sender({ 'type': 'syslogp',
                   'app': 'gokudo_gree' })

2. Create action log. ::

 actlog = ActionLog(sender, userid, device)

3. Output actionlog   ::

 actd = actlog.do_gacha(PaymentType.FREE, 10)

4. Output dericativelog,if needed::

 actd.dec_gachaticket('GACHA', ticket_id)

Use middleware
-----------------

You may use Django`s middleware ,to output logs more easily with less settings.The main difference with normal usage is that it won`t output the log except every procedure in view function is done.This is how you use it::

 from kome.middleware.actionlog import get_actlog,get_derivedlog
 
 def view(self, request):
     #use get_actlog or get_derivedlog, 
     #to get action log or derived log 
     actlog = get_actlog('aaa')
     actd = get_derivedlog('aaa')

     #You may use derived log in advance.
     actd.dec_gachaticket('GACHA', ticket_id)

     # If you need Exception
     do_process()

     #If successed output action log
     #if failed doesn`t out put anything.
     actlog.do_gacha(PaymentType.FREE, 10)

     # Different name return different action log or derived log
     actd = get_derivedlog('bbb')
     actd.dec_gachaticket('GACHA', ticket_id)
     # No action log,no derived log.Will not be recognised.
     # get_actlog('bbb').do_gacha(PaymentType.FREE, 10)

     # process_response of middleware will execute every process.

This is how you set up::

1. set middleware ::

 MIDDLEWARE_CLASSES = (
   ...
   'kome.middleware.actionlog.ActionLogMiddleware'
 }

2. set log output address to middleware

::

 import kome.middleware.actionlog
 kome.middleware.actionlog.sender = sender

3. Get ActionLog from Django`s view function.

::

 from kome.middleware.actionlog import get_actlog,get_derivedlog
 
 def view(self, request):
     actlog = get_actlog('aaa')
     actd = get_derivedlog('aaa')


Outout of custom log     
-----------------------

You can add your own custom logs to output,in case your new event use a special log which is not in the standard kome library or else.

Example :: 

 #A custom log for event 8
 actd = actlog.log("e8_caravan_execute", # The first argument is the event name
                    # and other argument is your customs. 
                    caravan_id="12",
                    color="red",
                    before_jewel=5,
                    after_jewel=2,
                    success=True)
  actd.inc_card(...) # Output increased cards as derived log.
