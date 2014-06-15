# Description: request_foursquare_data.py gets some foursquare information about venues and users.
# Colaborators: Saulo Ricci
# Date: 01/02/2011

from logger.logger import Logger
from requester.requester import requester
import sys
import re
import simplejson as json
import datetime
import random
import time
import os

_4SQ_VENUE_URL = 'https://api.foursquare.com/v2/venues/%s?client_id=%s&client_secret=%s'
_4SQ_VENUE_TIPS_URL = 'https://api.foursquare.com/v2/venues/%s/tips?client_id=%s&client_secret=%s&offset=%s'
_4SQ_VENUE_PHOTOS_URL = 'https://api.foursquare.com/v2/venues/%s/photos?client_id=%s&client_secret=%s&offset=%s&group=venue'
_4SQ_VENUE_LINKS_URL = 'https://api.foursquare.com/v2/venues/%s/links?client_id=%s&client_secret=%s'
_4SQ_VENUE_HTML_URL = 'https://foursquare.com/venue/%s'
_4SQ_USER_HTML_URL = 'https://foursquare.com/user/%s'
_4SQ_VENUE_HTML_PATTERN = '^http[^:*]://foursquare.com/venue/([0-9]+)$'
_4SQ_USER_URL = 'https://api.foursquare.com/v2/users/%s?oauth_token=%s'
_4SQ_USER_TIPS_URL = 'https://api.foursquare.com/v2/users/%s/tips?oauth_token=%s&offset=%s&limit=500'
_4SQ_USER_BADGES_URL = 'https://api.foursquare.com/v2/users/%s/badges?oauth_token=%s'
_4SQ_USER_FRIENDS_URL = 'https://api.foursquare.com/v2/users/%s/friends?oauth_token=%s&offset=%s&limit=500'
_4SQ_USER_FOLLOWERS_URL = 'https://api.foursquare.com/v2/users/%s/followers?oauth_token=%s&offset=%s&limit=500'
_4SQ_USER_LIST_DONES_URL = 'https://api.foursquare.com/v2/lists/%s/dones?oauth_token=%s&offset=%s&limit=500'
_4SQ_USER_MAYORSHIPS_URL = 'https://api.foursquare.com/v2/users/%s/mayorships?oauth_token=%s&offset=%s'
_4SQ_TIP_URL = 'https://api.foursquare.com/v2/tips/%s?client_id=%s&client_secret=%s'

TIME_INTERVAL = 0.8
TIME_INTERVAL_LINKS = 7.2
TIME_INTERVAL_USERS = 7.2

def request_data(url):
    requester_obj = requester()
    status, data_str, info = requester_obj.get_response(url)
    return (status, data_str, info)

def set_proc_name(newname):
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname)+1)
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)

def get_user_info(user_id, token, logfilename):
    logger_obj = Logger(log_name=' USER INFO THREAD', log_filename=logfilename)
    status, user_info_str, info = request_data(_4SQ_USER_URL % (user_id, token))

    if (status == 500) or (status == 404):
        logger_obj.put_message('error', str(status) + ' - %s' % user_id)
        return status, None, 0

    elif status == 200:
        logger_obj.put_message('debug', '200 - %s' % user_id)
        user_info = dict()
        try:
            user_info = json.loads(user_info_str)['response']['user']
            user_info['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))
            return status, user_info, 1
        except:
            return status, user_info, 1
    else:
        logger_obj.put_message('critical', 'Other error - %s' % user_id)
        logger_obj.put_message('critical', status)
        return status, None, 1 

def get_user_dones_list(user_id, token, logfilename):
    requester_obj = requester()
    dones_list = []
    offset = 0
    dones_count = 0
    page_count = 0

    logger_obj = Logger(log_name=' LIST DONES THREAD', log_filename=logfilename)
    status, dones_str, info = requester_obj.get_response(_4SQ_USER_LIST_DONES_URL % (user_id, token, str(offset)))

    if (status == 500) or (status == 404):
        logger_obj.put_message('error', str(status) + ' - %s' % user_id)
        return status, None, page_count

    elif status == 200:
        page_count += 1
        dones_obj = json.loads(dones_str)
        dones_count = int(dones_obj['response']['list']['listItems']['count'])
        if dones_obj['response']['list']['listItems']['items']:
            dones_list += dones_obj['response']['list']['listItems']['items']
        else:
            for done in dones_list:
                done['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))

            logger_obj.put_message('debug', '200 - %s' % user_id)
            return status, dones_list, page_count

        offset += len(dones_obj['response']['list']['listItems']['items'])
        while offset < dones_count:
            status, dones_str, info = requester_obj.get_response(_4SQ_USER_LIST_DONES_URL % (user_id, token, str(offset)))
            page_count += 1
            if (status == 500) or (status == 404):
                logger_obj.put_message('error', str(status) + ' - %s' % user_id)
                return status, None, page_count
            
            elif status == 200:
                dones_obj = json.loads(dones_str)
                try:
                    if dones_obj['response']['list']['listItems']['items']:
                        dones_list += dones_obj['response']['list']['listItems']['items']
                    else:
                        for done in dones_list:
                            done['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))
                        logger_obj.put_message('debug', '200 - %s' % user_id)
                        return status, dones_list, page_count
                except:
                    for done in dones_list:
                        done['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))
                    logger_obj.put_message('debug', '200 - %s' % user_id)
                    return status, dones_list, page_count

            else:
                logger_obj.put_message('critical', 'Other error - %s' % user_id)
                logger_obj.put_message('critical', status)
                return status, None, page_count

            offset += len(dones_obj['response']['list']['listItems']['items'])

        for done in dones_list:
            done['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))
        logger_obj.put_message('debug', '200 - %s' % user_id)
        return status, dones_list, page_count
    else:
        logger_obj.put_message('critical', 'Other error - %s' % user_id)
        logger_obj.put_message('critical', status)
        return status, None, page_count

def get_user_friends(user_id, token, logfilename):
    friend_list = []
    offset = 0
    friends_count = 0
    page_count = 0

    logger_obj = Logger(log_name=' LIST FRIENDS THREAD', log_filename=logfilename)
    status, friends_str, info = request_data(_4SQ_USER_FRIENDS_URL % (user_id, token, str(offset)))

    if (status == 500) or (status == 404):
        logger_obj.put_message('error', str(status) + ' - %s' % user_id)
        return status, None, page_count

    elif status == 200:
        page_count += 1
        friends_obj = json.loads(friends_str)
        friends_count = int(friends_obj['response']['friends']['count'])
        if friends_obj['response']['friends']['items']:
            friend_list += friends_obj['response']['friends']['items']
        else:
            for friend in friend_list:
                friend['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))
            logger_obj.put_message('debug', '200 - %s' % user_id)
            return status, friend_list, page_count

        offset += len(friends_obj['response']['friends']['items'])
        while offset < friends_count:
            status, friends_str, info = request_data(_4SQ_USER_FRIENDS_URL % (user_id, token, str(offset)))
            page_count += 1
            if (status == 500) or (status == 404):
                logger_obj.put_message('error', str(status) + ' - %s' % user_id)
                return status, None, page_count
            
            elif status == 200:
                friends_obj = json.loads(friends_str)
                try:
                    if friends_obj['response']['friends']['items']:
                        friend_list += friends_obj['response']['friends']['items']
                    else:
                        for friend in friend_list:
                            friend['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))
                        logger_obj.put_message('debug', '200 - %s' % user_id)
                        return status, friend_list, page_count
                except:
                    for friend in friend_list:
                        friend['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))
                    logger_obj.put_message('debug', '200 - %s' % user_id)
                    return status, friend_list, page_count

                offset += len(friends_obj['response']['friends']['items'])

            else:
                logger_obj.put_message('critical', 'Other error - %s' % user_id)
                logger_obj.put_message('critical', status)
                return status, None, page_count

        for friend in friend_list:
            friend['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))
        logger_obj.put_message('debug', '200 - %s' % user_id)
        return status, friend_list, page_count

    else:
        logger_obj.put_message('critical', 'Other error - %s' % user_id)
        logger_obj.put_message('critical', status)
        return status, None, page_count

def get_user_followers(user_id, token, logfilename):
    follower_list = []
    offset = 0
    followers_count = 0
    page_count = 0
    logger_obj = Logger(log_name=' LIST FOLLOWERS THREAD', log_filename=logfilename)
    status, followers_str, info = request_data(_4SQ_USER_FOLLOWERS_URL % (user_id, token, str(offset)))
    
    if (status == 500) or (status == 404):
        logger_obj.put_message('error', str(status) + ' - %s' % user_id)
        return status, None, page_count

    elif status == 200:
        page_count += 1
        followers_obj = json.loads(followers_str)
        followers_count = int(followers_obj['response']['followers']['count'])
        if followers_obj['response']['followers']['items']:
            follower_list += followers_obj['response']['followers']['items']
        else:
            for follower in follower_list:
                follower['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))
            logger_obj.put_message('debug', '200 - %s' % user_id)
            return status, follower_list, page_count

        offset += len(followers_obj['response']['followers']['items'])
        while offset < followers_count:
            status, followers_str, info = request_data(_4SQ_USER_FOLLOWERS_URL % (user_id, token, str(offset)))
            page_count += 1
            
            if (status == 500) or (status == 404):
                logger_obj.put_message('error', str(status) + ' - %s' % user_id)
                return status, None, page_count
            
            elif status == 200:
                followers_obj = json.loads(followers_str)
                try:
                    if followers_obj['response']['followers']['items']:
                        follower_list += followers_obj['response']['followers']['items']
                    else:
                        for follower in follower_list:
                            follower['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))
                        logger_obj.put_message('debug', '200 - %s' % user_id)
                        return status, follower_list, page_count
                except:
                    for follower in follower_list:
                        follower['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))
                    logger_obj.put_message('debug', '200 - %s' % user_id)
                    return status, follower_list, page_count
                
                offset += len(followers_obj['response']['followers']['items'])

            else:
                logger_obj.put_message('critical', 'Other error - %s' % user_id)
                logger_obj.put_message('critical', status)
                return status, None, page_count

        for follower in follower_list:
            follower['current_time'] = str(int(time.mktime(datetime.datetime.now().timetuple())))
        logger_obj.put_message('debug', '200 - %s' % user_id)
        return status, follower_list, page_count

    else:
        logger_obj.put_message('critical', 'Other error - %s' % user_id)
        logger_obj.put_message('critical', status)
        return status, None, page_count

def actual_id(user_id):
    requester_obj = requester()
    status, actual_url = requester_obj.get_url(_4SQ_USER_HTML_URL % user_id)
    return (status, actual_url)

def write_data(output_filename, venue_id, data):
    output_file = open(output_filename, 'ab')
    output_file.write(venue_id + ' ' + data + '\n')
    output_file.close()

def load_ids(id_filename):
    id_file = open(id_filename, 'r')
    id_list = []
    for line in id_file:
        id_list.append(line.strip())
    id_file.close()
    return id_list

def update_ids_file(id_filename, list_ids):
    id_file = open(id_filename, 'w')
    for id in list_ids:
        id_file.write(id + '\n')
    id_file.close()

def main():
    ids_filename = sys.argv[2]

    now_time = datetime.datetime.now()
    month = str(now_time.month)
    day = str(now_time.day)
    year = str(now_time.year)
    hour = str(now_time.hour)
    minute = str(now_time.minute)
    second = str(now_time.second)

    output_filename_photos = sys.argv[3] + 'photos' + month + '_' + day + '_' + year + '_' + hour + '_' + minute + '_' + second + '.txt.gz'
    output_filename_tips = sys.argv[3] + 'tips' + month + '_' + day + '_' + year + '_' + hour + '_' + minute + '_' + second + '.txt.gz'
    output_filename_venue_info = sys.argv[3] + 'venue_info' + month + '_' + day + '_' + year + '_' + hour + '_' + minute + '_' + second + '.txt.gz'
    client_id = sys.argv[4]
    client_secret = sys.argv[5]

    ids = True
    while ids:
        ids = load_ids(ids_filename)
        id = get_actual_id(ids.pop(int(len(ids)*random.random())))
        if id:
            try:
                print 'Go to get the %s photos list on %s' % (id.strip(), datetime.datetime.now())
                photos_list = get_photos_list(id.strip(), client_id, client_secret)
                print 'Go to get the %s tips list on %s' % (id.strip(), datetime.datetime.now())
                tips_list = get_tips_list(id.strip(), client_id, client_secret)
                print 'Go to get the %s venue info on %s' % (id.strip(), datetime.datetime.now())
                venue_info = get_venue_info(id.strip(), client_id, client_secret)

                write_data(output_filename_photos, id.strip(), json.dumps(photos_list))
                print 'Has just written the %s photos list on %s' % (id.strip(), str(datetime.datetime.now()))
                write_data(output_filename_tips, id.strip(), json.dumps(tips_list))
                print 'Has just written the %s tips list on %s' % (id.strip(), str(datetime.datetime.now()))
                write_data(output_filename_venue_info, id.strip(), json.dumps(venue_info))
                print 'Has just written the %s venue info on %s' % (id.strip(), str(datetime.datetime.now()))
                
                update_ids_file(ids_filename, ids)
                print 'Has just updated the venue_ids file on %s' % str(datetime.datetime.now())

            except:
                pass

def test():
    user_info, number_pages = get_user_dones_list('19455', 'QAF2HMYWSVINQCW4JLJLNWQ5XQQGP0CASAD5CXMPNC3DOQFI')
    print user_info, number_pages

if __name__  == '__main__':
    test()
