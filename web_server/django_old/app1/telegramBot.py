import sys, os
import json
import requests
import time
import logging
from logging.handlers import RotatingFileHandler

#------------------------------------------------------------------------------
# Because this script have to be run in a separate process from manage.py
# you need to set up a Django environnement to use the Class defined in
# the Django models. It is necesssary to interact witht the Django database
#------------------------------------------------------------------------------
# to get the projet.settings it is necessary to add the parent directory
# to the python path
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    sys.path.append(os.path.abspath('..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")
import django
django.setup()

from app1.models import Telegram, Update_id, Profile, Alert
from django.utils.translation import gettext as _
from django.utils import translation
from django.conf import settings


botid = "bot988625521:AAHf4DF2kwocwEL89TVJoOvNxTRPZxF0g94"
getupdateurl = ("https://api.telegram.org/%s/getUpdates" % (botid))
sendmessageurl = ( "https://api.telegram.org/%s/sendMessage" % (botid))
sendphotourl = "https://api.telegram.org/{}/sendPhoto".format(botid)

def SendChatPhoto(tochatid_in, tousername_in,tofirstname_in,tolastname_in, photo_in):
    try:
        files = photo_in
        data = {'chat_id' :tochatid_in }
        requests.post(sendphotourl,data =data,  files=files)
    except Exception as repex:
        logger.warning(('Error while send Message: {}'.format(repex)))


def SendChatMessage(tochatid_in, tousername_in,tofirstname_in,tolastname_in, message_in):
    try:
        params =[('chat_id', tochatid_in ), ('text',message_in)]
        requests.get(sendmessageurl,params)
    except Exception as repex:
        logger.warning(('Error while send Message: {}'.format(repex)))

# ICI Controler que le userid plus bas existe dans la DB Protecia et stocker les usersinfos dans la
# BDD d'Protecia (l'object JSON de newuser par exemple)
# 1 - il peut y avoir N   telegram user -> 1  Protecia User
# 2 - un user Telegram peut etre present pour plusieurs Protecia User
# pour notifier potentiellement plusieurs personnes

def CommandRegister(fromuserid_in,fromusername_in, fromchatid_in, fromfirstname_in,fromlastname_in,token):
    try:
        logger.warning(("REGISTERING user  %s %s as user ID=%d" % ( fromfirstname_in , fromlastname_in, fromchatid_in)))
        profile = Profile.objects.get(telegram_token=token) # exception if invalid token
        translation.activate(profile.language)
        if Telegram.objects.filter(profile=profile, chat_id = fromchatid_in ).exists():
            SendChatMessage(fromchatid_in, fromusername_in, fromfirstname_in,fromlastname_in, _('Already registered'))
        else :
            Telegram(profile=profile, chat_id=fromchatid_in, name=fromfirstname_in+' '+fromlastname_in).save()
            SendChatMessage(fromchatid_in, fromusername_in, fromfirstname_in,fromlastname_in, _('Ok you are registered ') + '{}'.format(fromfirstname_in) + _(' as Protecia Telegram token : ') +  '{}'.format(token))
    except Profile.DoesNotExist as ex:
        SendChatMessage(fromchatid_in,fromusername_in, fromfirstname_in, fromlastname_in, "%s  , this is not a correct Protecia UserID" % (fromfirstname_in))
        logger.warning("Error in CommandRegister: %s" % (format(ex)))

def ConsummeMessage(obj):
    ofrom = obj['from']
    fromfirstname = ofrom.get('first_name', "[first name]")
    fromlastname=ofrom.get('last_name' , "[last name]")
    fromusername=ofrom.get( 'username' , "[username]")
    fromuserid=obj['from']['id']
    if ('text' in obj):
        text = obj['text']
    chatid=obj['chat']['id']
    profile=Telegram.objects.filter(chat_id=chatid).first().profile
    translation.activate(profile.language)
    logger.info("Message from  [%s %s(%s)] %s" % (fromfirstname,fromlastname,fromusername,text))
    regcmd=text[0:9]
    if (regcmd == "/register"):
        CommandRegister(fromuserid,fromusername, chatid, fromfirstname,fromlastname,text[10:])
        return True
    helpcmd=text[0:5]
    if (helpcmd == "/help"):
        SendChatMessage(chatid,fromusername, fromfirstname,fromlastname,
                        "{},".format(fromfirstname) +
                        _("Commands are:") + "\n /register" + _("[Protecia UserID]")+ " =>" +
                        _("Register your Protecia Account") + "\n" )
        return True
    startcmd=text[0:6]
    if (startcmd == "/start"):
        SendChatMessage(chatid, fromusername, fromfirstname,fromlastname,
                        _("Hi") + "{}".format(fromfirstname)+ 
                        ", \n" +
                        _("I am Protecia Bot. You shall first register your Protecia user ID in order to receive  Protecia notifications.") +
                        "\n\n" +
                        _("Type") +  "/help" +
                        _("to start."))
        SendChatMessage(chatid, fromusername, fromfirstname,fromlastname,
                        "("+
                        _("For your information, your Telegram user id is: ")+
                        "{}".format(fromuserid)+
                        ")")
        return True
    if text[0:4]=="stop" or text[0:4]=="Stop":
        alert =  Alert.objects.filter(client=profile.client)
        is_alert = not any([ i.active for i in alert])
        if is_alert:
             SendChatMessage(chatid, fromusername, fromfirstname,fromlastname,
                             "{}".format(fromfirstname)+
                             ", "+
                             _("There isn't any active alarm. The place is quiet.") )
        else :
           for a in alert :
               a.active = False
               a.save()
           SendChatMessage(chatid, fromusername, fromfirstname,fromlastname,
                           "{}".format(fromfirstname) +","+
                           _("Alarm is stop."))
        return True
    # Unknown Command
    SendChatMessage(chatid, fromusername, fromfirstname,fromlastname,
                    "{}".format(fromfirstname)+" ,"+
                    _("I don't understand this command , type")+
                    " /help")
    return False

def main(freq):
    try :
        update_id=Update_id.objects.get()
    except Update_id.DoesNotExist :
        Update_id(id_number = 0).save()
        update_id=Update_id.objects.get()
        pass
    while ( True ) :
        try:
            url = '{}?offset={}'.format(getupdateurl, update_id.id_number)
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            logger.warning('Exception calling URL {}'.format(url))
            pass
        if r.status_code == 200:
            try:
                obj = json.loads(r.text)
                if (obj['ok'] == True):
                    for o in obj['result'] :
                        if ('update_id' in o):
                            logger.info(str(o['update_id']))
                            update_id.id_number =  o['update_id']
                            update_id.save()
                        try:
                            if ('message' in o):
                                ConsummeMessage(o['message'])
                                update_id.id_number +=1
                                logger.info('consumme message in : {}'.format(url))
                        except Exception as e:
                            logger.warning('Error while parsing result {}'.format(e))
                            pass
            except Exception as rqe:
                logger.warning('Object is not a Json object: {}'.format(rqe))
        time.sleep(freq)

# start the process
if __name__ == '__main__':
    ####### log #######
    if settings.DEBUG :
        level=logging.DEBUG
    else:
        level=logging.WARNING
    logger = logging.getLogger('telegram')
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    file_handler = RotatingFileHandler(os.path.join(settings.BASE_DIR,'log','telegram.log'), 'a', 10000000, 1)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    ####################
    main(2)
