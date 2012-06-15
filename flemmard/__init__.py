import re
import shutil
import os
import argparse
import sys
import tempfile
from datetime import datetime

from jenkinsapi import api as jenkinsapi
import jenkins

from flemmard.util import run


MANDATORY_TARGETS = ('build', 'test', 'build_rpms')


def _color2status(color):
    if color == 'red':
        return 'FAIL'
    if color == 'blue':
        return 'SUCCESS'
    if color.endswith('anime'):
        return 'IN PROGRESS'
    return color.upper()


actions = ['list', 'build', 'create']


def list_jobs(client, args):
    jobs = client.get_jobs()
    maxl = max([len(job['name']) for job in jobs])
    for job in jobs:
        status = '[%s]' % _color2status(job['color'])
        name = job['name']
        pad = maxl - len(name) + 1
        print '%s%s%s' % (job['name'], ' ' * pad, status)


def build_job(client, args):
    client.build_job(args.job)
    print 'Build sent in the build queue'


def list_artifacts(client, args):
    artifacts = jenkinsapi.get_artifacts(args.url, args.job)
    for name, art in artifacts.items():
        print('%s - %s' % (name, art.url))


def job_status(client, args):
    print('Getting some info about %r' % args.job)
    #info = client.get_job_info(args.job)
    latest = jenkinsapi.get_latest_build(args.url, args.job)
    when = float(latest.get_timestamp()) / 1000.
    when = datetime.fromtimestamp(when).strftime('%Y-%m-%d %H:%M:%S')

    print('Latest build started at %s' % when)
    print('Build #%d' % latest.id())
    running = latest.is_running()
    if not running:
        status = latest.is_good()
        if status:
            print('Build went ok. \o/')
        else:
            print('Build failed /o\\')
    else:
        print('Still running *now*...')

def create_job(client, args):
    # before creating a job we want to validate the repo
    # structure
    print('Checking the project')
    repo = args.repository
    valid, msg = _control_project(repo)
    if not valid:
        print(msg)
        print('YOU FAIL')
        sys.exit(0)

    #
    template = os.path.join(os.path.dirname(__file__), 'job_tmpl.xml')
    with open(template) as f:
        template = f.read()

    if args.name is None:
        name = args.repository.split('/')[-1]
        if name.endswith('.git'):
            name = name[:-4]
    else:
        name = args.name

    name = name.title().replace(' ', '-')
    data = {'name': name, 'repository': args.repository,
            'description': "Job created by Flemmard"}
    client.create_job(name, template % data)
    print('Job %r created.' % name)



def _control_project(repository):

    temp_dir = tempfile.mkdtemp()
    old_wdir = os.getcwd()
    try:
        checkout = os.path.join(temp_dir, 'repo')
        print('Checking out in %r' % checkout)

        code, stdout, stderr = run('git clone %s %s' % (repository, checkout))
        os.chdir(checkout)

        # check the structure
        sys.stdout.write('Do we have a Makefile...')
        files = os.listdir('.')
        if 'Makefile' not in files:
            sys.stdout.write(' no\n')
            return False, 'No Makefile'
        sys.stdout.write(' yes\n')

        # check the Makefile targets
        with open('Makefile') as f:
            makefile = f.read()

        # we want 'build', 'test', 'build_rpms'
        sys.stdout.write('Checking the Makefile structure...')
        targets = re.findall('^(\w+)\:', makefile, re.M)
        for mandatory in MANDATORY_TARGETS:
            if mandatory not in targets:
                sys.stdout.write(' ouch\n')
                return False, 'The Makefile misses a %r target' % mandatory
        sys.stdout.write(' good, good\n')

    finally:
        os.chdir(old_wdir)
        shutil.rmtree(temp_dir)

    return True, None


def main():
    parser = argparse.ArgumentParser(description='Drive Jenkins from your couch.')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_list = subparsers.add_parser('list', help='List all jobs.')
    parser_list.set_defaults(func=list_jobs)

    parser_status = subparsers.add_parser('status', help='Gives a job status')
    parser_status.add_argument('job', help='Job to build.')
    parser_status.set_defaults(func=job_status)

    parser_build = subparsers.add_parser('build', help='Build a job.')
    parser_build.add_argument('job', help='Job to build.')
    parser_build.set_defaults(func=build_job)

    parser_create = subparsers.add_parser('create', help='Create a new Job')
    parser_create.add_argument('--name', help='Name of the job', default=None)
    parser_create.add_argument('repository', help='Repository')
    parser_create.set_defaults(func=create_job)

    parser_artifacts = subparsers.add_parser('artifacts', help='Lists the artifacts.')
    parser_artifacts.add_argument('job', help='Job.')
    parser_artifacts.set_defaults(func=list_artifacts)

    parser.add_argument('--url', dest='url',
                        default='http://hudson.build.mtv1.svc.mozilla.com/',
                        help="Jenkins Root URL")
    args = parser.parse_args()

    client = jenkins.Jenkins(args.url)
    args.func(client, args)


if __name__ == '__main__':
    main()
