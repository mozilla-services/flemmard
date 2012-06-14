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


actions = ['list']


def list(client):
    jobs = client.get_jobs()
    maxl = max([len(job['name']) for job in jobs])
    for job in jobs:
        status = '[%s]' % _color2status(job['color'])
        name = job['name']
        pad = maxl - len(name) + 1
        yield '%s%s%s' % (job['name'], ' ' * pad, status)


def main():
    parser = argparse.ArgumentParser(description='Drive Jenkins from your couch.')
    parser.add_argument('action', help='Action to run.', choices=actions)
    parser.add_argument('--url', dest='url',
                        default='http://hudson.build.mtv1.svc.mozilla.com/',
                        help="Jenkins Root URL")
    args = parser.parse_args()

    client = jenkins.Jenkins(args.url)

    if args.action == 'list':
        for job in list(client):
            print job
        sys.exit(0)


if __name__ == '__main__':
    main()
