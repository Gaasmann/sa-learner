#!/usr/bin/env python3

import sys
import mailbox

spam_folders = ['reclass', 'Junk', 'spam']
# This is the general mb, containing no mail, only folders
mb = mailbox.Maildir('./mail-data/', create=False)
list_folders = mb.list_folders()
data = []

for folder_name in list_folders:
    folder = mb.get_folder(folder_name)
    for message in folder:
        # no Spamassassin header or message not read => pass
        if 'X-Spam-Status' not in message or \
            'S' not in message.get_flags():
            continue
        spam_status = message['X-Spam-Status']
        splitted_status = spam_status.replace('\n\t', '').split(' ')
        try:
            tests = next(x for x in splitted_status if x.startswith('tests='))
        except StopIteration:
            print(splitted_status, file=sys.stderr)
            continue
        matched_rules = tests.split('=')[1].split(',')
        data.append( (message['Message-Id'],
                      matched_rules,
                      folder_name in spam_folders) )

print(data)
