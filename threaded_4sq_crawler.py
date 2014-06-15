# Description: Implements a threaded crawler id
# Colaborators: Saulo Ricci and Marisa Vasconcelos
# Date: 01/03/2012

import math
from logger.logger import Logger
from threading import Thread
from request_foursquare_data import *
import socket

MAX_AMOUNT_SPLITS = 10

class threaded_4sq_crawler(Thread):

    def __init__(self, user_id, aspect, credentials, log_filename):
        Thread.__init__(self)
        self.user_id = user_id
        self.aspect = aspect
        self.credentials = credentials
        self.log_filename = log_filename
        self.result = None
        self.amount_pages = 0
        self.status = None

    def run(self):
        self.get_aspect()

    def get_aspect(self):
        if self.aspect == 'user_info':
            self.status, self.result, self.amount_pages = get_user_info(self.user_id, self.credentials['token'], self.log_filename)
        elif self.aspect == 'user_friends':
            self.status, self.result, self.amount_pages = get_user_friends(self.user_id, self.credentials['token'], self.log_filename)
        elif self.aspect == 'user_followers':
            self.status, self.result, self.amount_pages = get_user_followers(self.user_id, self.credentials['token'], self.log_filename)
        elif self.aspect == 'list_dones':
            self.status, self.result, self.amount_pages = get_user_dones_list(self.user_id, self.credentials['token'], self.log_filename)

def read_credentials_file(credentials_filename):
    credentials_dict = dict()
    file = open(credentials_filename)
    credentials_dict['token_user_info'] = file.readline().strip()
    credentials_dict['token_user_tips'] = file.readline().strip()
    credentials_dict['token_user_friends'] = file.readline().strip()
    credentials_dict['token_user_followers'] = file.readline().strip()
    credentials_dict['client_id_tip_detail_1'] = file.readline().strip()
    credentials_dict['client_secret_tip_detail_1'] = file.readline().strip()
    credentials_dict['client_id_tip_detail_2'] = file.readline().strip()
    credentials_dict['client_secret_tip_detail_2'] = file.readline().strip()
    credentials_dict['client_id_tip_detail_3'] = file.readline().strip()
    credentials_dict['client_secret_tip_detail_3'] = file.readline().strip()
    credentials_dict['client_id_tip_detail_4'] = file.readline().strip()
    credentials_dict['client_secret_tip_detail_4'] = file.readline().strip()
    credentials_dict['client_id_tip_detail_5'] = file.readline().strip()
    credentials_dict['client_secret_tip_detail_5'] = file.readline().strip()
    credentials_dict['client_id_tip_detail_6'] = file.readline().strip()
    credentials_dict['client_secret_tip_detail_6'] = file.readline().strip()
    credentials_dict['client_id_tip_detail_7'] = file.readline().strip()
    credentials_dict['client_secret_tip_detail_7'] = file.readline().strip()
    credentials_dict['client_id_tip_detail_8'] = file.readline().strip()
    credentials_dict['client_secret_tip_detail_8'] = file.readline().strip()
    credentials_dict['client_id_tip_detail_9'] = file.readline().strip()
    credentials_dict['client_secret_tip_detail_9'] = file.readline().strip()
    credentials_dict['client_id_tip_detail_10'] = file.readline().strip()
    credentials_dict['client_secret_tip_detail_10'] = file.readline().strip()
    file.close()
    return credentials_dict

def main(process_name):
    ids_filename = sys.argv[2]

    output_filename_user_info = sys.argv[3] + process_name + '_user_info' + '.txt'
    output_filename_list_dones = sys.argv[3] + process_name + '_list_dones' + '.txt'
    output_filename_user_friends = sys.argv[3] + process_name + '_user_friends' + '.txt'
    output_filename_user_followers = sys.argv[3] + process_name + '_user_followers' + '.txt'

    credentials_file = sys.argv[4]

    logfilename = ''
    if socket.gethostname() in ['mummra', 'gargamel', 'esqueleto', 'cavernoso']:
        logfilename = '/data/users/saulomrr/_4sq_crawler/log/' + process_name + '.log'
    else:
        logfilename = '/var/tmp/_4sq_crawler/log/' + process_name + '.log'

    credentials_dict = read_credentials_file(credentials_file)
    ids = True
    logger_obj = Logger(log_name=' MAIN THREAD', log_filename=logfilename)
    while ids:
        sum_time = 0
        ids = load_ids(ids_filename)
        if not ids:
            break
        pos_id = int(len(ids) * random.random())
        id = ids[pos_id]
#        pre_result = actual_id(id)
#        if pre_result[0] == 200:
#            try:
                # Thread array to crawl basic information
        threaded_array = []
        threaded_array.append(threaded_4sq_crawler(id, 'user_info', {'token':credentials_dict['token_user_info']}, logfilename))
        threaded_array.append(threaded_4sq_crawler(id, 'list_dones', {'token':credentials_dict['token_user_tips']}, logfilename))
        threaded_array.append(threaded_4sq_crawler(id, 'user_friends', {'token':credentials_dict['token_user_friends']}, logfilename))
        threaded_array.append(threaded_4sq_crawler(id, 'user_followers', {'token':credentials_dict['token_user_followers']}, logfilename))
                
        for thread in threaded_array:
            thread.start()
        for thread in threaded_array:
            thread.join()

        if (threaded_array[0].status == 200) and (threaded_array[1].status == 200) and (threaded_array[2].status == 200) and (threaded_array[3].status == 200):
            if threaded_array[0].result:
                time1 = datetime.datetime.now()
                write_data(output_filename_user_info, id.strip(), json.dumps(threaded_array[0].result))
                time2 = datetime.datetime.now()
                sum_time += (time2 - time1).seconds + (time2-time1).microseconds/float(1000000)

            if threaded_array[1].result is not None:
                time1 = datetime.datetime.now()
                write_data(output_filename_list_dones, id.strip(), json.dumps(threaded_array[1].result))
                time2 = datetime.datetime.now()
                sum_time += (time2 - time1).seconds + (time2 - time1).microseconds/float(1000000)

            if threaded_array[2].result is not None:
                time1 = datetime.datetime.now()
                write_data(output_filename_user_friends, id.strip(), json.dumps(threaded_array[2].result))
                time2 = datetime.datetime.now()
                sum_time += (time2 - time1).seconds + (time2 - time1).microseconds/float(1000000)

            if threaded_array[3].result is not None:
                time1 = datetime.datetime.now()
                write_data(output_filename_user_followers, id.strip(), json.dumps(threaded_array[3].result))
                time2 = datetime.datetime.now()
                sum_time += (time2 - time1).seconds + (time2 - time1).microseconds/float(1000000)
                    
                logger_obj.put_message('debug', 'CRAWLED - %s' % id)
                id = ids.pop(pos_id)
                update_ids_file(ids_filename, ids)
                list_pages = map(lambda x: x.amount_pages, threaded_array)
                maximum_amount_pages = max(list_pages)

                sleep_time_overall = TIME_INTERVAL_USERS*maximum_amount_pages + 2*random.random() - sum_time
                if sleep_time_overall > 0:
                    time.sleep(sleep_time_overall)

        elif threaded_array[0].status == 404 or threaded_array[0].status == 400:
            logger_obj.put_message('debug', 'NOT EXISTS - %s' % id)
            id = ids.pop(pos_id)
            update_ids_file(ids_filename, ids)

            list_pages = map(lambda x: x.amount_pages, threaded_array)
            maximum_amount_pages = max(list_pages)

            sleep_time_overall = TIME_INTERVAL_USERS*maximum_amount_pages + 2*random.random() - sum_time
            if sleep_time_overall > 0:
                time.sleep(sleep_time_overall)

        else:
            logger_obj.put_message('critical', 'ERROR - GONNA RETRY %s' % id)
            list_pages = map(lambda x: x.amount_pages, threaded_array)
            maximum_amount_pages = max(list_pages)

            sleep_time_overall = TIME_INTERVAL_USERS*maximum_amount_pages + 2*random.random() - sum_time
            if sleep_time_overall > 0:
                time.sleep(sleep_time_overall)
            break
#            except ValueError:
#                pass

#        elif pre_result[0] == 404:
#            logger_obj.put_message('debug', 'NOT EXISTS - %s' % id)
#            id = ids.pop(pos_id)
#            update_ids_file(ids_filename, ids)

#        else:
#            logger_obj.put_message('critical', 'ERROR - GONNA RETRY %s' % id)
#            logger_obj.put_message('critical', pre_result[0])
#            break

if __name__ == '__main__':
    process_name = sys.argv[1]
    set_proc_name(process_name)
    main(process_name)
