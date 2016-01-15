=============================
listenclosely
=============================

CI:

.. image:: https://img.shields.io/travis/jlmadurga/listenclosely.svg
        :target: https://travis-ci.org/jlmadurga/listenclosely

.. image:: http://codecov.io/github/jlmadurga/listenclosely/coverage.svg?branch=master 
    :alt: Coverage
    :target: http://codecov.io/github/jlmadurga/listenclosely?branch=master
  
.. image:: https://requires.io/github/jlmadurga/listenclosely/requirements.svg?branch=master
     :target: https://requires.io/github/jlmadurga/listenclosely/requirements/?branch=master
     :alt: Requirements Status
     
PyPI:


.. image:: https://img.shields.io/pypi/v/listenclosely.svg
        :target: https://pypi.python.org/pypi/listenclosely

Docs:

.. image:: https://readthedocs.org/projects/listenclosely/badge/?version=latest
        :target: https://readthedocs.org/projects/listenclosely/?badge=latest
        :alt: Documentation Status


Listenclosely is a django-app that works as a middleman to connect instant messaging clients. Think on a Call Center/Customer Service using
using instant messaging... exactly what it does. 

 * It is simple, connects *Askers* with online *Agents* until the *Chat* is considered as terminated and the *Agent* is released to attend other *Asker* chats. 

 * It is flexible, so you can define your own strategies to assign *Agents* to *Askers* and your own messaging backend services.
 

 
Messaging Services integrated:

 * Whatsapp https://github.com/jlmadurga/listenclosely-whatsapp
 
 * Telegram https://github.com/jlmadurga/listenclosely-telegram

Documentation
-------------

The full documentation is at https://listenclosely.readthedocs.org.

.. image:: https://raw.github.com/jlmadurga/listenclosely/master/docs/imgs/diagram.png
        :target: https://listenclosely.readthedocs.org
        
* Asker1 is chatting with the Busy Agent
* Asker2 try to chat but no free Agent was free so is waiting with a Pending chat to be attended by an agent
* Asker3 is opening a chat and Online Agent will be assigned to the chat

	
Quickstart
----------

Install listenclosely::

    pip install listenclosely

Then use it in a project::

    import listenclosely
    
Add it to django apps and migrate::

	INSTALLED_APPS = [
		...
    	'listenclosely',
    	...
	]
	python manage.py migrate
	
Select, install and configure service backend ::

	LISTENCLOSELY_MESSAGE_SERVICE_BACKEND = "listenclosely_telegram.service.TelegramMessageServiceBackend"
	
Define your agent strategy or define your own::

	LISTENCLOSELY_AGENT_STRATEGY = 'listenclosely.strategies.first_free.FirstFreeAgentStrategy'

Add step to your celery app::

	from listenclosely.celery import ListenCloselyAppStep
	app.steps['worker'].add(ListenCloselyAppStep)
	
Start your celery app usign gevent::

	celery --app=demo_app.celery:app worker -P gevent 

Call listen task or define a celery scheduler to execute::
	
	from listenclosely import tasks
	tasks.listen.delay()


Features
--------

* Connects *Askers* and *Agents*  in chats to establish a *Chat*
* Strategies to find *Agent* to attend new *Asker* chat. Define your own strategies
* Messaging Service Backend: Define your own messaging service backend implementations.
* Cron tasks for attending pending chats and to terminate obsolete chats to release *Agents*

Running Tests
--------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements/test.txt
    (myenv) $ make test


