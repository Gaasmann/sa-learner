#!/usr/bin/env python3

import sys
import mailbox

#spam_folders = ['reclass', 'Junk', 'spam']
## This is the general mb, containing no mail, only folders
#mb = mailbox.Maildir('./mail-data/', create=False)

class MessageInfoExtractor(object):
    # TODO refacto: extract class probably needed: one class for the whole
    # extract, one class taking care of operations on a single message
    def __init__(self, maildir_path, spam_folders):
        self.maildir_path = maildir_path
        self.spam_folders = spam_folders
    def reset_data(self):
        self.data = []
        self.data_hot_ones = []
        self.rule_directory = RulesDirectory()
    def parse_mails(self):
        self.reset_data()
        maildir = mailbox.Maildir(self.maildir_path)
        for folder_name in maildir.list_folders():
            folder = maildir.get_folder(folder_name)
        # TODO need to "map/reduce" that part
            for filename, message in folder.items():
                if not self._is_message_good_candidate(message):
                    continue
                info = self._extract_info(filename, message, folder_name)
                if info is not None:
                    self.data.append(info)
    def _extract_info(self, filename, message, folder_name):
        # TODO refacto needed, the folder_name shouldn't be here
        # TODO Bug: parsing not 100% accurate: 'LOTS_OF_MONEYautolearn'
        #      '[BAYES_50', 'none'
        rules_matched = self._extract_rules_from_message(message)
        if rules_matched is None:
            return None
        rule_numbers = self._convert_rules_to_numbers(rules_matched)
        return (filename, message['Message-Id'], rule_numbers,
                folder_name in self.spam_folders)
    def _extract_rules_from_message(self, message):
        spam_status = message['X-Spam-Status']
        splitted_status = spam_status.replace('\n\t', '').split(' ')
        try:
            tests = next(x for x in splitted_status if x.startswith('tests='))
        except StopIteration:
            return None
        matched_rules = tests.split('=')[1].split(',')
        return matched_rules
    def _convert_rules_to_numbers(self, rule_list):
        res = []
        for rule in rule_list:
            res.append(self.rule_directory.get_rule_number(rule))
        return res
    def _is_message_good_candidate(self, message):
        """ Return true is the message is read and have been scanned by SA """
        if 'X-Spam-Status' not in message or \
            'S' not in message.get_flags():
                return False
        return True

class RulesDirectory(object):
    def __init__(self):
        # rules to numbers
        self.forward = {}
        # numbers to rules
        self.reverse = []
    def get_rule_number(self, rule):
        if rule in self.forward:
            return self.forward[rule]
        else:
            return self._add_new_rule(rule)
    def get_rule(self, number):
        return self.reverse[number]
    def _add_new_rule(self, rule):
        number = len(self.reverse)
        self.forward[rule] = number
        self.reverse.append(rule)
        return number
