META WHATSAPP
=============

Introduction
------------


Setup of WhatsApp Graph API.
----------------------------

In Meta Configuaration
----------------------

1.Create Facebook Developer Account.

create a Facebook developer account using your Facebook account.

Developer account link- https://developers.facebook.com/

![facebook_developer_account.jpeg](static/description/image/facebook_developer_account.jpeg)

2.Create And Register App

    create and register app using create app button. If you already have an App
that you want to use with WhatsApp, you can skip the next section.

![create app1.jpeg](static/description/image/create app1.jpeg)
![create app2.jpeg](static/description/image/create app2.jpeg)

First select app type, you will find multiple option as mentioned below,
choose one type according to your need and click on next.

![create app3.jpeg](static/description/image/create app3.jpeg)
![create app4.jpeg](static/description/image/create app4.jpeg)

3.Facebook credentials

After creating app, open that apps to
see credential.
my apps => apps => all apps.

![create app5.jpeg](static/description/image/create app5.jpeg)

4.Dashboard

To add a product(WhatsApp).

1. First select your app
2. Go to product--> add a product
3. Now find WhatsApp and click on setup

![create app6.jpeg](static/description/image/create app6.jpeg)

5.Facebook Credential Screen

We will use these credential
during creating provider. To see credentials, and add the phone number. follow these steps:
Go to WhatsApp --> API Setup.

![create app7.jpeg](static/description/image/create app7.jpeg)
![create app8.jpeg](static/description/image/create app8.jpeg)

In the image above, we have a temporary Access token, Phone number ID, and WhatsApp
Business Account ID that you must fill out when creating a provide after installing Graph API.

![create app8.1.1.jpeg](static/description/image/create app8.1.1.jpeg)

6.Generate Permanent Access Token in WhatsApp Cloud API

![create app9.jpeg](static/description/image/create app9.jpeg)

Using edit button add callback url and Verify token same as odoo configured webhook url and webhook verify token.

![create app 10(webhook url and token adding popup).jpeg](static/description/image/create app 10(webhook url and token adding popup).jpeg)
![create app10.1.jpeg](static/description/image/create app10.1.jpeg)

Enable the messages in webhook field for access the received messages.

![create app11(webhook fields).jpeg](static/description/image/create app11(webhook fields).jpeg)

**If you want to create new provider then you need to create new app in Facebook
and repeat all step.**

9.Whatsapp Manager

![whatsapp template1.jpeg](static/description/image/whatsapp template1.jpeg)

Add the Whatsapp Message Template from whatsapp => account tools => Message Template. Here you can Create/Edit/Delete WhatsApp Message Templates
According to Facebook policy.if you use the WhatsApp API and want to connect with
someone, you can only send templates until he/she replies/acknowledges you.
![template_2.png](static/description/image/template_2.png)

create template clicked view

![whatsapp template3.jpeg](static/description/image/whatsapp template3.jpeg)

WhatsApp Configuaration in odoo
-------------------------------

In app, WhatsApp -> Configuration -> Account Configuration.

![odooconfiguration.jpeg](static/description/image/odooconfiguration.jpeg)

Here set the App details that App Id,App Token,Account Id,Phone Number Id,Webhook Token.

1.Test Connection and Synchronize

![conf_whatsapp_1.png](static/description/image/conf_whatsapp_1.png)

In top right side have a button for Checking Test Connection.It check all credentials and its all are correct it changed as green colour.

After 'Test Connection' Button Have a 'Synchronize' button for linking all predefined templates into the app.

3.Lines and Other Info

![lines.jpeg](static/description/image/lines.jpeg)
![attachment-btn.png](static/description/image/attachment-btn.png)

In lines, set specific models for enables the whatsapp message option.Also we can deactivate the activation.Update the changes for the models using Update button.Groups used in lines that, set specific users for access the whatsapp message action.

In Other Info, set the attachment that will can recieve or not for recievable message.

Templates
---------

In app, WhatsApp -> Configuration -> Templates.

![Templates.png](static/description/image/Templates.png)
![sychronize_button_template.png](static/description/image/sychronize_button_template.png)
![preview.png](static/description/image/preview.png)

Here can see all synchronized whatsapp Templates.And also we can synchronize each template using Synchronize button inside form view. 

The preview of the template is visible by clicking on preview button on the top right side.

WhatsApp Logs
-------------
In WhatsApp -> Logs, see all whatsapp messages detailed both send and recieved.

![log tree view.jpeg](static/description/image/log tree view.jpeg)
![log form view.jpeg](static/description/image/log form view.jpeg)

WhatsApp Sales
--------------

1.Activate the model in whatsapp configuration lines.we can send message for a single partner or multiple partners

![lines.jpeg](static/description/image/lines.jpeg)

2.After activating the model in whatsapp configuration lines, we can see the whatsapp message action in sale order action.

![sale_whatsapp_message_action.png](static/description/image/sale_whatsapp_message_action.png)

3.Click on the action and send message using opened popup window.

Types of Message Mode:

-> Session Mode : Used for Sending Text messages
-> Template Mode : Used for sending image,video,document etc. using specific template.

Session mode and Template mode:

![sending_message_view.png](static/description/image/sending_message_view.png)

Here we can select multiple partners in recipients and message content in Text message.




