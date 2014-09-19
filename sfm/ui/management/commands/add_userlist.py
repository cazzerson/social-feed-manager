import time
from optparse import make_option

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from ui.models import TwitterUser, TwitterUserSet


class Command(BaseCommand):
    help = 'Add list of TwitterUsers from a text file, with one' \
           'TwitterUser name per line'

    option_list = BaseCommand.option_list + (
        make_option('--setname', action='store', default=False, dest='setname',
                    help='Add TwitterUsers to a TwitterUserSet'),
        )

    #help message will display [input-filepath] as a required arg
    @classmethod
    def usage(self, *args):
        usage = 'Usage: ./manage.py add_userlist [input-filepath] ' + \
                '[options]' + '\n' + self.help
        return usage

    def handle(self, *args, **options):
        set_name_fnd = set_name_nt_fnd = False
        if len(args) != 1:
            raise CommandError('Please specify one input file')
        #check if setname is present, if not create it
        if options['setname']:
            set_name = TwitterUserSet.objects.filter(name=options['setname'])\
                .values('id', 'name')
            if len(set_name) == 0:
                print 'SET:', options['setname'], 'doesnot exists.' \
                      'Create it??[Y/N]'
                if raw_input('>>') is 'Y':
                    try:
                        usrname_id = User.objects.get(
                            username=settings.TWITTER_DEFAULT_USERNAME)
                        TwitterUserSet.objects.create(
                            name=options['setname'], user_id=usrname_id.id)
                        set_name = TwitterUserSet.objects.filter(
                            name=options['setname']).values('id', 'name')
                        set_name_nt_fnd = True
                    except Exception as e:
                        print 'ERROR: creating set ', e
                else:
                    print 'Please try adding userlist without setname option'
                    return
            else:
                set_name_fnd = True
                print 'SET FOUND:', options['setname'], 'in sfm'
        #read the input file, add userlist and respective setname
        for line in open(args[0]):
            new_twi_usr = line.lstrip().lstrip("@").rstrip()
            twitter_user = TwitterUser.objects.filter(name=new_twi_usr)
            #if username does not exists, add username, setname(per option)
            if len(twitter_user) == 0:
                try:
                    twitter_user = TwitterUser(name=new_twi_usr)
                    twitter_user.clean()
                    twitter_user.save()
                    if options['setname']:
                        if set_name_nt_fnd or set_name_fnd is True:
                            try:
                                for ids in set_name:
                                    twitter_user.sets.add(ids['id'])
                                print 'ADDED:', new_twi_usr, ' with ' \
                                      'Set:', options['setname']
                            except Exception as e:
                                print 'ERROR:', e
                                time.sleep(1)
                    else:
                        print 'ADDED:', new_twi_usr, 'to SFM'
                        time.sleep(1)
                except Exception as e:
                    if 'not found' in e.message:
                        print 'ERROR: twitter screen name:%s was' \
                              ' not found' % new_twi_usr
                    elif 'already present' in e.message:
                        print 'ERROR: twitteruser %s not unique in SFM,' \
                              'already present' % new_twi_usr
                    else:
                        print 'ERROR: %s \n' % new_twi_usr, e.message
                    continue
            else:
                #if user exists, if setname exists for username, skip.
                print 'FOUND:', new_twi_usr, 'in sfm'
                twitter_user = TwitterUser.objects.get(name=new_twi_usr)
                try:
                    if options['setname']:
                        set_exists = twitter_user.sets.filter(
                            name=options['setname']).values(
                            'id', 'twitteruser')
                        if len(set_exists) == 0:
                            for ids in set_name:
                                try:
                                    twitter_user.sets.add(ids['id'])
                                    print 'UPDATED:', new_twi_usr, 'with ' \
                                          'new Set:', options['setname']
                                except Exception as e:
                                    print 'ERROR:', e
                        else:
                            print 'SET EXISTS:', options['setname'], \
                                  ' for', new_twi_usr
                except Exception as e:
                    print 'ERROR:', e
                    continue
