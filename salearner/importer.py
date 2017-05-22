#!/usr/bin/env python3
"""Import SA info from Mailbox and create a pickle file."""

import re
import pickle
import mailbox
import numpy as np

class MessageInfoExtractor(object):
    """Extract SA data from emails"""
    # TODO refacto: extract class needed: multi purpose class doing coffee
    def __init__(self, maildir_path, spam_folders):
        self.maildir_path = maildir_path
        self.spam_folders = spam_folders
        self.data_filename = []
        self.data_messageid = []
        self.data_rule_matched = []
        self.data_hot_ones = []
        self.data_labels = []
        self.data_numpy = {}
        self.rule_directory = RulesDirectory()

    def parse_mails(self):
        """Too big function extracting SA data from mails"""
        maildir = mailbox.Maildir(self.maildir_path)
        for folder_name in maildir.list_folders():
            folder = maildir.get_folder(folder_name)
            # TODO need to "map/reduce" that part
            for filename, message in folder.items():
                info = self._extract_info(filename, message, folder_name)
                if info is not None:
                    self.data_filename.append(info[0])
                    self.data_messageid.append(info[1])
                    self.data_rule_matched.append(info[2])
                    self.data_labels.append(info[3])
        self._convert_to_hot_ones()
        self._convert_to_numpy()

    def save_pickle(self, filepath):
        """Write the numpy dict to a pickle"""
        with open(filepath, mode='wb') as picklefile:
            pickle.dump(self.data_numpy, picklefile, protocol=-1)

    def _extract_info(self, filename, message, folder_name):
        # TODO refacto needed, the folder_name shouldn't be here
        rules_matched = MailParser(message).sa_matched_rules
        if rules_matched is None:
            return None
        rule_numbers = self._convert_rules_to_numbers(rules_matched)
        return (filename, message['Message-Id'], rule_numbers,
                folder_name in self.spam_folders)

    def _convert_rules_to_numbers(self, rule_list):
        res = []
        for rule in rule_list:
            res.append(self.rule_directory.get_rule_number(rule))
        return res

    def _convert_to_hot_ones(self):
        nb_rules = len(self.rule_directory.reverse)
        self.data_hot_ones = \
            list(map(lambda matched_rules:
                     [1 if rule in matched_rules else 0 for rule in range(nb_rules)],
                     self.data_rule_matched))

    def _convert_to_numpy(self):
        self.data_numpy = {
            'filename': np.array(self.data_filename),
            'messageid': np.array(self.data_messageid),
            'hot-ones': np.array(self.data_hot_ones, dtype=np.bool),
            'labels' : np.array(self.data_labels, dtype=np.bool),
            'rules' : self.rule_directory.reverse
        }

class MailParser(object):
    """ Parse a single mail for SA information """
    def __init__(self, message):
        self.message = message

    @property
    def sa_matched_rules(self):
        """ returns SA matched rules.

        Returns:
            list: list of rules matched
            None: if the message should be discarded
        """
        return None if not self._is_message_good_candidate() \
                else self._extract_rules_from_message()

    def _is_message_good_candidate(self):
        """ Return true is the message is read and have been scanned by SA """
        if 'X-Spam-Status' not in self.message or \
            'S' not in self.message.get_flags():
            return False
        return True

    def _extract_rules_from_message(self):
        spam_status = self.message['X-Spam-Status']
        spam_status = spam_status.replace('\n\t', '')
        re_match = re.search('tests=(.*)autolearn=', spam_status)
        if re_match is None:
            return None
        test_string = re_match.group(1)
        # two sub needed. the RE should be modified to avoid that
        test_string = re.sub(r'([\s\[\]]|[=:]-?\d+(?:\.\d+)?)', '', test_string)
        test_string = re.sub(r'([\s\[\]]|[=:]-?\d+(?:\.\d+)?)', '', test_string)
        matched_rules = test_string.split(',')
        matched_rules = [x for x in matched_rules if x != '' and x != 'none']
        return matched_rules

class RulesDirectory(object):
    """Keep accounting of SA rules"""
    def __init__(self):
        # rules to numbers
        self.forward = {}
        # numbers to rules
        self.reverse = []

    def get_rule_number(self, rule):
        """Get a rule number from its name"""
        if rule in self.forward:
            return self.forward[rule]
        return self._add_new_rule(rule)

    def get_rule(self, number):
        """Get a rule name from its number"""
        return self.reverse[number]

    def _add_new_rule(self, rule):
        number = len(self.reverse)
        self.forward[rule] = number
        self.reverse.append(rule)
        return number

# TODO: if __name__ == '__main__':
