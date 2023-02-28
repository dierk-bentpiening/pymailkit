![Logo](https://i.ibb.co/mCgPJVh/pymailkit.png)

# Usage and Documentation
pymailkit is an library for making Mailing in Python easy and straight forward.
The idea behind pymailkit was to build a Library for creating custom python based email clients. 
pymailkit was designed to have just pure python dependencies and just a bunch of third party dependencies. 
pymailkit supports different styles of mailing routines and mailing flows

***Warning***: This is in the moment a public development, a stable release will be ready soon.
***Documentation:*** will be extended from time to time.
----------------------------------------------------------------
## Introduction and Usage

pymailkit includes all methods required to be implementing a email application, actually the smtp stack is implemented, the imap parts are in development and will be available soon.
Actually pymailkit is beable to implement the moost cases from sending a email from a template up to a queued email notifications trasmission sevice.
pymailkit uses acutal asynchronous computation capabilities of python 3.9+
### Dependencies and Requirements

#### Development Requirements:
pymailkit uses [pipenv](https://pipenv.pypa.io/en/latest/) as mangement for dependencys and virtual environment management. For Asynncronous testing the pytest-asyncio and pytest-async plugin is required.

Testing is done with [pytest](https://docs.pytest.org/en/7.2.x/), all test classed are inside pymailkit/tests module.
For building pymailkit library python 3.9+ is required, there is not support for python versions before version 3.9.

For codeformating i use [black](https://github.com/psf/black)

#### library dependencies:
1. [schedule](https://schedule.readthedocs.io/en/stable/) - Schedule is used for implementation of the mailmessage scheduler.
2. [pathlib](https://docs.python.org/3/library/pathlib.html) - Used for bedder path checking and combination.
### Future dependencies
3. [cryptography](https://docs.python.org/3/library/cryptography) - Cryptogryphography will be used for future mail_encryption features.

### Included Moduls
1. email - MailingClasses 
2. event - Event Classes, for handling events.
3. mailaccount - All classes implementing Account Entity
4. mailbackend - All backend classes implementing a mailing method.
5. message - All messages classes implementing E-Mail Message Entity.
6. tests - All tests classes.
7. tools - Helper Classes

### Base Entities
- MailAccount
    - Represents a MailAccount to use!
- MailMessage
    - Represents an E-Mail Message to send.
      - Includes several object methods to use:
          1. `generate_messages()` returns list of generated finalized message for sending. sender has been injected into the message. **Attributes:** self, eventstream,random_sender_address: bool = False, sender=None
          2. `_to_json()` returns message object serialized as JSON. **Attributes:** self
          3. `_to_pdf()` returns message object serialized as PDF. **Attributes:** self ***Currently in development***
          4. `_to_markdown()` returns message object serialized as Markdown. **Attributes:** self ***Currently in development***
- SentMessageReport
  - Represents an Report about the sendet message with the message and mailaccount used included

### Base Classes

### Supported Modes / Mailing Classes / Daemon
The mailer is based on one main class the daemon class, this class gets extended by the lower level routine classes.
The MailerDaemon includes following Methods:
- `generate_message_from template(’templatename')`
  - Generates an MailMessage object from given template. Template has to be included in template directory or custom directory. Template is an JSON File including all needed informations for generating a message. Function returns an MailMessage object which can be sendet after defining sender_account or setting `use_default_sender_address=True` if an default MailAccount is defined.
  - `add_to_accountpool(mailaccount)` this method adds a new mailaccount to the pool of accounts. Argument has to be an MailAccount object.
- Following attributes can be set and get:
  - `custom_template_dir` Sets or gets the custom template directory, it is an empty string by default. Attribute must be a path.
  - `schedulerlist` get currently running schduler objects inside a list.
- Simple Mailer
  - SimpleMailer is like the name suggested a simple mailer for sending a single or multiple messages with one command.
  - simple_mailer main function is the `send_mail()`function. send_mail accepts a list of messages and send them to the specified recipient.
  - ***arguments:*** self, mailmessage: MailMessage, sender=None reporting=False
- Scheduled Mailer
- Queued Mailer

#### MailerDaemon (BaseClass for all Mailer classes)
This is the base class including all base functionalities and attributes for sending mail over smtp.
The MailerDaemon class gets inherited by the functional mailing classes.

#### Simple Mailer
Simple Mailer is like the name suggest a simple mailer class offering simple mailer functions like sending mail in the standard way, or send mail with random account from mailaccount pool.
Default method for sending a mail with the SimpleMailer class is the `send_mail()` method.

### Scheduled Mailer
Scheduled Mailer is a scheduled mailing service it sends defined mails based on the specified schedule. Schdule will set over a string as argument with the method call.
The main method to use of the schedules mailer class is the 'scheduled_mailer()' method.
Following arguments can be set: self, mailmessage: MailMessage schedule_every: str, schedule_time: str = None, sender=None.

## TODO
- [ ] Custom Exception Classes for business logic based exceptions.
- [ ] MailMessage Encryption.
- [ ] SMTP SSL Interface.
- [ ] Microsoft MSAL Integration. (General oauth support) 