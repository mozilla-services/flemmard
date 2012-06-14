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


actions = ['list', 'build']


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


def main():
    parser = argparse.ArgumentParser(description='Drive Jenkins from your couch.')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_list = subparsers.add_parser('list', help='list help')
    parser_list.set_defaults(func=list_jobs)

    parser_build = subparsers.add_parser('build', help='a help')
    parser_build.add_argument('job', help='Job to build.')
    parser_build.set_defaults(func=build_job)

    parser.add_argument('--url', dest='url',
                        default='http://hudson.build.mtv1.svc.mozilla.com/',
                        help="Jenkins Root URL")
    args = parser.parse_args()

    client = jenkins.Jenkins(args.url)
    args.func(client, args)


if __name__ == '__main__':
    main()
