=================
What is Gsocial
=================

It is an application made of Django which will relay between GreeAPI and the game applications.

On setting
---------------
What you have to set in setting.py::

    #Specify the debug mode
    OPENSOCIAL_DEBUG = True

    #Specify the sandbox mode
    OPENSOCIAL_SANDBOX = True

    #Specify the container you use
    OPENSOCIAL_CONTAINER = 'sb.gree'

    #Specify the ID
    APP_ID = '13145'

    #Specify the CONSUMER_KEY
    CONSUMER_KEY = "14ab41f03a54"

    #Specify the CONSUMER_KEY
    CONSUMER_SECRET = "ac62b878eb9d4d9697bfeaef6de58bb1"

APIs that gsocial will relay
-----------------------------

・ Activity_.

・ AuthDevice_.

・ BlackList_.

・ Inspection_.

・ Message_.

・ Payment_.

・ People_.

・ Request_.

How to use APIs
---------------------------

.. _Activity:
*Activity*

1. Send Activity ::   

    from gsocial.utils.activity import Activity
    Activity(request).send(userid, title, url=None)

    input
        request: Django`s request object
        userid: opensocial_owner_id
        title: the title of activity
    output
        None 

.. _AuthDevice:

*AuthDevice*

1. Check whether terminal authentication has done::
    from gsocial.utils.authdevice.api import get_auth_device_api
    get_auth_device_api(request).is_auth_device
    input
        request: Django`s request object
    output
        True: Alerady authorized
        False: Unautorized


2. Do the terminal authentication::
    from gsocial.utils.authdevice.api import get_auth_device_api
    get_auth_device_api(request).check_auth_device
    input
        request: Django`s request object
    output
        True: terminal authentication done
        False: terminal authentication was not implemented


.. _BlackList:
*BlackList*

1. Check whether User A has registered User B as "Blacklist".
    from gsocial.utils.blacklist import BlackList
    BlackList(request).blacklist_check(userid, target_userid)
    input
        request: Django`s request object
        userid: ID of User A
        target_userid: ID of User B
        caching:Do caching or not. defalut:True
        cache_update: Update cache or not. defalut: False
    output
        True: User B is registerd
        False: User B is unregistered


.. _Inspection:
*Inspection*

1. Submit text::
    from gsocial.utils.inspection import Inspection
    Inspection(request).post(userid, message)
    input
        request: Django`s request object
        userid: opensocialowner_id of the post
        message: content of the post 
    output
        text_id of inspectionAPI  

2. text updateing ::
    from gsocial.utils.inspection import Inspection
    Inspection(request).put(userid, text_id, message)
    input
        request: Django`s request object 
        text_id: text_id of subjected text 
        userid: opensocial_owner_id
        message: content of the post 
    output
        None

3. text deleting ::
    from gsocial.utils.inspection import Inspection
    Inspection(request).delete(userid, text_id, message)
    input
        request: Django`s request object
        text_id: inspection_id
        userid: opensocialowner_id
    output
        None

4. Get the texts:: 
    from gsocial.utils.inspection import inspection
    Inspection(request).gets_dict(userid, text_ids)
    input
        request: Django`s request object 
        text_ids: a list of text_id
        userid: opensocial_owner_id
        caching: Do caching or not. default:True
        retry_count: How many times will you retry if API was unaccessable 
    output
        {text_id:(data, json, entry)}

        ※ data, json, entry is hash

        sample of json, entry, data
            {
                "entry": [
                  {
                    "textId": "0123456-1",
                    "appId": "1001",
                    "authorId": "0123456",
                    "ownerId": "0123456",
                    "data": "自由な入力文",
                    "status": "0",
                    "ctime": "2010-04-29T14:41:00",
                    "mtime": "2010-04-29T14:41:00"
                  }
                ]
            }



5. Get several texts ::
    from gsocial.utils.inspection import inspection
    Inspection(request).gets_dict(userid, text_ids)

    input
        request: Django`s request object 
        text_ids: a list of text_id 
        userid: opensocial_owner_id
        caching: Do caching or not. defalut:True
        retry_count: How many times will you retry if API was unaccessable.
    output
        [text_id:(data, json), ...]
        ※ data, json, is hash

6. Get several texts::
    from gsocial.utils.inspection import inspection
    Inspection(request).gets(userid, text_ids)

    input
        request: Django`s request object 
        text_ids: A list of text_id
        userid: opensocial_owner_id
        caching: Do caching or not. defalut:True
        retry_count: How many times will you retry if API was unaccessable.
    output
        [text_id:(data, json, entry), ...]
        ※ data, json, entry is hash

.. _Message:
*Message*

1. Send message to an user:: 
    from gsocial.utils.message import Message
    Message().send(sender_osuser_id, osuser_id, title, body, relative_mobile_url)

    input
        sender_osuser_id: ID of sender(not indispensable)
        osuser_id: id of subjected user
        title: title of message 
        body: content of message 
        relative_mobile_url: url of the link that display the message 
    output
        return value of oauth_requst


2. Send to several users(Max 20 people) ::
    from gsocial.utils.message import Message
    Message().send(sender_osuser_id, osuser_id, title, body, relative_mobile_url)
    
    input
        sender_osuser_id: ID of sender(not indispensable)
        osuser_ids: a list of ids of subjected users
        title: title of message 
        body: content of message 
        relative_mobile_url: url of the link that display the message 
    output              
        return value of oauth_requst


.. _Payment:
*Payment*

1. Start the payment processing   
   Save the payment information on record and return the url of payment(platform side)    
   ::

    from gsocial.utils.payment import Payment
        pay_cls = Payment(request)
        res = pay_cls.request_payment(
        osuser_id = request.osuser.userid
        item_id = 1
        item_name = "name of item"
        item_point = 100
        item_description = "description of item"
        item_image_url = "http://%s" % settings.SITE_DOMAIN
        callback_path = reverse("debug_opensocial_payment_callback")
        finish_path = reverse("debug_opensocial_payment_finish")
        item_message = "Message(only for GREE) default=''"
        item_quantity = 1
        is_test = False
        )

    input
        request: Django request instance
        osuser_id: ID of OpensocialUser
        item_id: Item ID
        item_name: Name of item
        item_point: Price of item
        item_description： Description of item
        item_image_url: Url of item image
        callback_url: Callback url
        finish_url: FinishURL which is used after the payment processing 
        item_message: Message(Only for GREE) default='' 
        item_quantity: Number of item default=1
        is_test: Test flag(Only for mixi) default=False
    output
        payment_url: the URL of payment(platform side)

2. Payment callback processing   
   Callback processing from the URL of payment 
   Update the PaymentStatus
   ::

    from gsocial.utils.payment import Payment
    Payment(request).callback()
    input
        request: Django`s request object
    output
        True:  Purchase done                                                                                                                           
        False: Purchase canceled

3. Payment finish processing   
   Payment finish processing after the callback
   ::

    from gsocial.utils.payment import Payment
    Payment(request).finish()
    input
        request: Django`s request obejct
    output
        True: Purchase done                                                                                                                                          
        False: Purchase canceled

4. Confirmation of Payment informtion  
   ::

    from gsocial.utils.payment import Payment
    Payment(request).is_success()
    input
        request: Django`S request obejct
    output
        True:  Purchase done                                                                                                                          
        False: Purchase canceled

.. _People:
*People*

1. Get the information of the user   ::

    from gsocial.utils.people import People
    People(request).get_myself()
    input
        userid: Subjected opensocial_owner_id
        fields: The information of field(None specify means get everything) default: None
           If only getting ext id,and nickname
              'id,nickname'
        caching: Do caching or not. defalut:True
        cache_update: Update cache or not. defalut: False
    output
         A hash like this:
         {
         "id": "0123456",
         "nickname": "Applcation of Gree"
         }
         
        

2. ユーザーAがユーザーBとソーシャル友達か確認
2. Check whether User A and User B is friend.
   ::

    from gsocial.utils.people import People 
    People(request).get_friend(userid, friend_userid):
    input
        userid: opensocial_owner_id of User A
        friend_userid: opensocial_owner_id of User B
        caching: Do caching or not. defalut:True
        cache_update: Update caching or not.defalut: False
    output
        If no information: None 
        If information:a hash like this will return
            {
            "nickname": "Nami",
            "profileUrl": "http://gree.jp/0123457",
            "thumbnailUrl": "http://gree.jp/img/0123457.jpg"
            }

3. Get the friend information

   You can`t cache on Gsocial due to the technological specification.
   A request will get 100 friend informaiton,for maximum 10 times.

   ::

    from gsocial.utils.people import People 
    People(request).get_friends(self, userid, has_app=True, fields=None)
    input
        userid: opensocial_owner_id
        has_app: Whether subejected user should have already installed application. defalut:True
        fields: Field information youl want to get(None specify means get every information) default:None
           If only getting ext id,and nickname
              'id,nickname'
    output
        Provided you can get:
            {
            "totalResults": 4,
            "itemsPerPage": 5,
            "entry": [
              {
                "nickname": "aaa",
                "profileUrl": "http://gree.jp/0123457",
                "thumbnailUrl": "http://gree.jp/img/0123457.jpg"
              },
              {
                "nickname": "bbb",
                "profileUrl": "http://gree.jp/0123458",
                "thumbnailUrl": "http://gree.jp/img/0123458.jpg"
              },
              {
                "nickname": "ccc",
                "profileUrl": "http://gree.jp/0123459",
                "thumbnailUrl": "http://gree.jp/img/0123459.jpg"
              },
              {
                "nickname": "ddd",
                "profileUrl": "http://gree.jp/0123460",
                "thumbnailUrl": "http://gree.jp/img/0123460.jpg"
              }
              ]
             }
        Provided you could not get:
            {
            "totalResults": 0,
            "itemsPerPage": 0,
            "entry": [],
            "error": True
             }

4. Get the "entry" informaton of friend 
  ::
    from gsocial.utils.people import People 
    People(request).get_friends_entry(self, userid, has_app=True, fields=None)
    input
        userid: opensocial_owner_id
        has_app: Whether subejected user should have already installed application. defalut:True
        fields: Field information youl want to get(None specify means get every information) default:None
           If only getting ext id,and nickname
              'id,nickname'
    output
        Provided you could get:
            [
              {
                "nickname": "aaa",
                "profileUrl": "http://gree.jp/0123457",
                "thumbnailUrl": "http://gree.jp/img/0123457.jpg"
              },
              {
                "nickname": "bbb",
                "profileUrl": "http://gree.jp/0123458",
                "thumbnailUrl": "http://gree.jp/img/0123458.jpg"
              },
              {
                "nickname": "ccc",
                "profileUrl": "http://gree.jp/0123459",
                "thumbnailUrl": "http://gree.jp/img/0123459.jpg"
              },
              {
                "nickname": "ddd",
                "profileUrl": "http://gree.jp/0123460",
                "thumbnailUrl": "http://gree.jp/img/0123460.jpg"
              }
            ]
        Provided you could not get:
            []

5. Get the friend information according to the paginate 
   Return the already-using-application friends information for specified numbers.
   You can change page or limit to do paginate.
   ::

    from gsocial.utils.people import People 
    People(request).get_friends_entry(self, userid, has_app=True, fields=None)
    input
        userid: opensocial_owner_id
        page: Specify the page defalut:1
        limit: Max number of information defalut:10
        has_app: Whether subjected user should have already installed application. defalut:True
        fields: Field information youl want to get(None specify means get every information) default:None
           If only getting ext id,and nickname
              'id,nickname'
    output
        Provided you could get:
            [
              {
                "nickname": "aaa",
                "profileUrl": "http://gree.jp/0123457",
                "thumbnailUrl": "http://gree.jp/img/0123457.jpg"
              },
              {
                "nickname": "bbb",
                "profileUrl": "http://gree.jp/0123458",
                "thumbnailUrl": "http://gree.jp/img/0123458.jpg"
              },
              {
                "nickname": "ccc",
                "profileUrl": "http://gree.jp/0123459",
                "thumbnailUrl": "http://gree.jp/img/0123459.jpg"
              },
              {
                "nickname": "ddd",
                "profileUrl": "http://gree.jp/0123460",
                "thumbnailUrl": "http://gree.jp/img/0123460.jpg"
              }
            ]
        Provided you could not get:
            []


6. Get the number of friends using the application   ::

    from gsocial.utils.people import People 
    People(request).get_friends_totalresults(userid)
    input
        userid: opensocial_owner_id
        has_app: Whether subjected user should have already installed application. defalut:True
        fields: Field information youl want to get(None specify means get every information) default:None
           If only getting ext id,and nickname
              'id,nickname'
    output
        Provided you could get:number of people
        Provided you could not get: 0

.. _Request:
*Request*

1. Create parameter for Request
   ::

    from gsocial.utils.request import Request
    Request(request).create_request_data(
        title = 'test',
        body = 'Help me!!',
        callbackurl = Callback URL,
        mobile_url = Url for feature phone 
        touch_url = url for smart phone
    )
    input
        You can set the following arguments.
          'title': value,
          'body': value,        
          'callbackurl': value, 
          'mobile_url': value,  
          'touch_url': value,   
          'mobile_image': value,
          'touch_image': value, 
          'list_type': value,   
          'to_user_id': value,  
          'editable': value,    
          'expire_time': value, 
          'backto_url': value,  

    output
        Return hash of the arguments.
        ext
        Setting title,body,callbackurl,mobile_url,touch_url will return a hash like following.
        {
            'title': value,
            'body': value,        
            'callbackurl': value, 
            'mobile_url': value,  
            'touch_url': value,   
        }

How to use Templatetags
---------------------------

.. _ひとことサービス:
*"Hitokoto" service*

1. Create a form for Hitokoto（for FP） ::

    inputd
	callbackurl :the URL which will be redirected after posting message
	body_value : the message
	submit_value : letters on submit button
	image_urls_640 : a URL of 640px size image defalut: None
	image_urls_240 : a URL of 240px size image defalut: None
	image_urls_75 : a URL of 75px size image defalut: None

    output
    return the created form

    templates will be like this
        {% load hitokoto %}
    	{% get_hitokoto_form callbackurl body_value submit_value image_urls_240 %}

2. Create a link for Hitokoto（for SP） ::

    input
	callbackurl : the URL which will be redirected after posting message
	body_value : the message
	submit_value : letters on submit button
	image_urls_640 : a URL of 640px size image defalut: None
	image_urls_240 : a URL of 240px size image defalut: None
	image_urls_75 : a URL of 75px size image defalut: None

    output
	return the created　link

    templates will be like this
        {% load hitokoto %}
	    {% get_hitokoto_form_sp callbackurl body_value submit_value image_urls_240 %}


.. _リクエストサービス:
*request service*

1. Create request form (for FP）

   You can`t use request form as templatetags as it conatins some images or pictures.

   Following is a sample source cord.
   ::

    input
	request_users : A list of Users you want to send a request(a parameter to be handed to to_user_id[])

	submit_value : letters on submit button
	title : title of request（indispensable）
	body : the content
	callbackurl :a URL which will be redirected after the request.
	mobile_url : a URL which will be redirected after the click(FP)
	touch_url : a URL which will be redirected after the click（SP）
	option_params : optional dictionary
             backto_url   : a URL of application after the "request sent confirmtaion" page
             mobile_image : a URL of images.this URL will be attached in the message.(FP)
             touch_image  : a URL of images.this URL will be attached in the message.(SP)
             list_type    : the type of User whom request will be send
             editable     : Whether User can edit the message or not?
             expire_time  : Expired date of request(UTC FORMAT)

    output
	return the created form

    the templates will be like this:
	{% load request %}
	{% get_request_form request_users submit_value title body callbackurl mobile_url touch_url option_params %}

2. Create request link（for SP）

   This version will just create links, so you can use it as templatetags as well.
   ::

    input
	request_users : A list of Users you want to send a request(a parameter to be handed to to_user_id[])

    	submit_value : letters on submit button
    	title : title of request（indispensable）
    	body : the content
    	callbackurl :a URL which will be redirected after the request.
    	mobile_url : a URL which will be redirected after the click(FP)
    	touch_url : a URL which will be redirected after the click（SP）
    	option_params : optional dictionary
                 backto_url   : a URL of application after the "request sent confirmtaion" page
                 mobile_image : a URL of images.this URL will be attached in the message.(FP)
                 touch_image  : a URL of images.this URL will be attached in the message.(SP)
                 list_type    : the type of User whom request will be send
                 editable     : Whether User can edit the message or not?
                 expire_time  : Expired date of request(UTC FORMAT)

    output
	return the created link

    the template will be like this:
	{% load request %}
	{% get_request_form request_users submit_value title body callbackurl mobile_url touch_url option_params %}
