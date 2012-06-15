import os
import argparse
import jenkins
import sys


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


def create_job(client, args):
    # before creating a job we want to validate the repo
    # structure
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


def main():
    parser = argparse.ArgumentParser(description='Drive Jenkins from your couch.')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_list = subparsers.add_parser('list', help='List all jobs.')
    parser_list.set_defaults(func=list_jobs)

    parser_build = subparsers.add_parser('build', help='Build a job.')
    parser_build.add_argument('job', help='Job to build.')
    parser_build.set_defaults(func=build_job)

    parser_create = subparsers.add_parser('create', help='Create a new Job')
    parser_create.add_argument('--name', help='Name of the job', default=None)
    parser_create.add_argument('repository', help='Repository')
    parser_create.set_defaults(func=create_job)

    parser.add_argument('--url', dest='url',
                        default='http://hudson.build.mtv1.svc.mozilla.com/',
                        help="Jenkins Root URL")
    args = parser.parse_args()

    client = jenkins.Jenkins(args.url)
    args.func(client, args)


if __name__ == '__main__':
    main()
