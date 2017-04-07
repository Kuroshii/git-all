import argparse
import base64
import getpass
import os
import subprocess
import sys
import time

from controller import Controller


def setup_commands():
    return {
        'users': {
            'run': Commands.show_user_info,
            'help': 'List stored users'
        },
        'groups': {
            'run': Commands.show_group_info,
            'help': 'List stored groups'
        },
        'repos': {
            'run': Commands.show_repository_info,
            'help': 'List installed repositories'
        },
        'do': {
            'run': Commands.run_in_repos,
            'help': 'Run a command in a set of installed repos',
            'flags': {
                'clean': {
                    'flag': '-c',
                    'help': "Don't print headers or extra newlines for output"
                },
                'quiet': {
                    'flag': '-q',
                    'help': "Don't print any output"
                },
            },
            'args': [
                {
                    'name': 'repo_names',
                    'help': 'The repo(s) to run the command in'
                },
                {
                    'name': 'action',
                    'help': 'The command action to perform in each repo',
                    'type': 'remainder'
                }
            ]
        },
        'pardo': {
            'run': Commands.run_in_repos_parallel,
            'help': 'Run a command in a set of installed repos',
            'options': {
                'max_processes': {
                    'flag': '-p',
                    'default': '4',
                    'help': 'How many simultaneous processes to allow'
                }
            },
            'flags': {
                'clean': {
                    'flag': '-c',
                    'help': "Don't print headers or extra newlines for output"
                },
                'quiet': {
                    'flag': '-q',
                    'help': "Don't print any output"
                },
            },
            'args': [
                {
                    'name': 'repo_names',
                    'help': 'The repo(s) to run the command in'
                },
                {
                    'name': 'action',
                    'help': 'The command action to perform in each repo',
                    'type': 'remainder'
                }
            ]
        },
        'register': {
            'run': Commands.register_repositories,
            'help': 'Register an already existing repository',
            'options': {
                'path': {
                    'flag': '-l',
                    'help': 'Where the repo(s) to register are located'
                }
            },
            'args': [
                {
                    'name': 'repo_names',
                    'help': 'the repo(s) to register'
                }
            ]
        },
        'add-user': {
            'run': Commands.add_credentials,
            'help': 'Store new bitbucket credentials',
            'args': [
                {
                    'name': 'user',
                    'default': None,
                    'help': 'The user to store credentials for'
                }
            ]
        },
        'drop-user': {
            'run': Commands.drop_credentials,
            'help': 'Remove stored bitbucket credentials',
            'args': [
                {
                    'name': 'users',
                    'help': 'The user(s) to drop credentials for'
                }
            ]
        },
        'add-repo': {
            'run': Commands.add_repositories,
            'help': 'Add repositories to a repository group',
            'args': [
                {
                    'name': 'repo_names',
                    'help': 'the repo(s) to add'
                
                },
                {
                    'name': 'group_names',
                    'help': 'the name of the group(s) to append to',
                    'default': 'default'
                }                
            ]
        },        
        'list-group': {
            'run': Commands.list_repositories,
            'help': 'List the repositories in a repository group',
            'args': [
                {
                    'name': 'group_names',
                    'help': 'the name of the group(s) to list',                    
                    'default': 'default'
                }
            ]
        },
        'drop-group': {
            'run': Commands.delete_repository_group,
            'help': 'Delete a repository group',
            'args': [
                {
                    'name': 'group_names',
                    'help': 'the name of the group(s) to list',
                    'default': 'default'
                }
            ]
        },
        'install': {
            'run': Commands.install_repositories,
            'help': 'Clone repositories in a specified location',
            'options': {
                'path': {
                    'flag': '-l',
                    'help': 'where to install the repos'
                }
            },
            'args': [
                {
                    'name': 'repo_names',
                    'help': 'the name of the repo(s) to install',
                }                
            ]
        }
    }


def setup_parser(commands):
    parser = argparse.ArgumentParser(
        prog='git-all',
        description='A utility for managing a set of bitbucket repositories.'
    )
    subparsers = parser.add_subparsers(
        dest='command',
        description='A set of git-all commands',
        help='Which command to run'
    )

    for command_name, command in commands.items():
        subcommand_parser = subparsers.add_parser(command_name,
                                                  description=command.get('help'),
                                                  help=command.get('help'))

        for arg in command.get('args', []):
            if type(arg) == str:
                subcommand_parser.add_argument(arg)
            else:
                if 'default' in arg:
                    subcommand_parser.add_argument(
                        arg['name'],
                        help=arg.get('help'),
                        nargs='?',
                        default=arg.get('default')
                    )
                elif arg.get('type') == 'remainder':
                    subcommand_parser.add_argument(
                        arg['name'],
                        nargs=argparse.REMAINDER,
                        help=arg.get('help')
                    )
                else:
                    subcommand_parser.add_argument(
                        arg['name'],
                        help=arg.get('help')
                    )

        for option_name, option in command.get('options', {}).items():
            subcommand_parser.add_argument(option['flag'],
                                           dest=option_name,
                                           help=option.get('help'),
                                           default=option.get('default'))

        for flag_name, flag in command.get('flags', {}).items():
            subcommand_parser.add_argument(flag['flag'],
                                           dest=flag_name,
                                           help=flag.get('help'),
                                           action='store_true')
    return parser


def get_auth(username):
    password = getpass.getpass("Password: ")

    unencoded_auth_secret = "{}:{}".format(username, password)
    return base64.standard_b64encode(unencoded_auth_secret.encode('utf-8')).decode('utf-8')


def start_command(command, path=None):
    return subprocess.Popen(command,
                            cwd=path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)


def process_finished(process):
    return process.poll() is not None

def join_process(process):
    out, error = process.communicate()

    return (out.decode('utf-8'),
            error.decode('utf-8'),
            process.returncode)


def run_command(command, path=None):
    return join_process(start_command(command, path))


class Commands:
    def __init__(self, controller):
        self.controller = controller

    def parse_users(self, users):
        if not users:
            default_user = self.controller.default_user()
            return [default_user] if default_user else []

        if users == '_':
            return self.controller.list_users()
        return users.split(',')

    def parse_groups(self, groups):
        if groups == '_':
            return self.controller.list_repository_groups()
        return groups.split(',')

    def parse_repos(self, repos):
        final_repos = []

        for repo_str in repos.split(','):
            if repo_str == '--':
                default_repos = self.controller.list_repository_group('default')
                final_repos += default_repos
            elif repo_str.startswith('/'):
                group_repos = self.controller.list_repository_group(repo_str[1:])
                final_repos += group_repos
            elif repo_str.startswith('@'):
                repo_params = repo_str[1:].split('/')
                user = repo_params[0]
                if not user:
                    user = self.controller.default_user()
                if not user:
                    print('Cannot parse repo "{}"'.format(repo_str))
                    continue

                if len(repo_params) == 1:
                    got_repos = self.controller.get_repos_for_user(
                        user
                    )
                elif len(repo_params) == 2:
                    team = repo_params[1]
                    got_repos = self.controller.get_repos_for_team(
                        user, team
                    )
                else:
                    team = repo_params[1]
                    project = repo_params[2]
                    got_repos = self.controller.get_repos_for_project(
                        user, team, project
                    )
                if got_repos:
                    final_repos += got_repos
            else:
                final_repos.append(repo_str)
        return final_repos
        
    def add_credentials(self, user):
        if not user:
            user = input("Username: ")
        auth_secret = get_auth(user)

        self.controller.add_user(user, auth_secret)

    def drop_credentials(self, users):
        for user in self.parse_users(users):
            self.controller.drop_user(user)

    def show_user_info(self):
        default_user = self.controller.default_user()

        for user in sorted(self.controller.list_users()):
            print(
                '{}'.format(user) +
                (' [default]' if user == default_user else '')
            )

    def show_group_info(self):
        for group in sorted(self.controller.list_repository_groups()):
            print(group)

    def delete_repository_group(self, group_names):
        for group in self.parse_groups(group_names):
            self.controller.delete_repository_group(group)

    def list_repositories(self, group_names):
        for group in sorted(self.parse_groups(group_names)):
            repos = self.controller.list_repository_group(group)

            if len(repos) == 0:
                print('Group "{}" doesn\'t exist'.format(group))
                return

            print('{}:'.format(group))
            for repo in sorted(repos):
                print('  {}'.format(repo))

    def add_repositories(self, group_names, repo_names):
        repos = self.parse_repos(repo_names)

        for group in self.parse_groups(group_names):
            self.controller.add_to_repository_group(group, repos)

    def check_for_repo(self, repo, path):
        repo_name = repo.split('/')[-1]
        path = os.path.join(path, repo_name)

        output = ''
        try:
            output, error, status = run_command(['git', 'remote', 'get-url', 'origin'], path)
        except FileNotFoundError:
            pass
        
        if 'git@bitbucket.org:{}'.format(repo) in output:
            return True
        return False
            
    def clone_repo(self, repo, path):
        output, error, status = run_command(['git', 'clone', 'git@bitbucket.org:{}.git'.format(repo)], path)
        if status != 0:
            print(error)

    def register_repositories(self, repo_names, path):
        if path is None:
            path = os.getcwd()

        for repo in sorted(self.parse_repos(repo_names)):
            if not self.check_for_repo(repo, path):
                print('No repository found: {}'.format(repo))
                continue
                
            print('Registering {}'.format(repo))
            self.controller.add_repo_path(repo, path)            
            
    def install_repositories(self, repo_names, path):
        if path is None:
            path = os.getcwd()

        for repo in sorted(self.parse_repos(repo_names)):
            if self.check_for_repo(repo, path):
                print('Repository already found: {}, registering...'.format(repo))
                self.controller.add_repo_path(repo, path)
                continue
                
            print('Cloning {}'.format(repo))
            self.clone_repo(repo, path)
            self.controller.add_repo_path(repo, path)

    def show_repository_info(self):
        for location in sorted(self.controller.list_repo_locations()):
            print('{}:'.format(location))
            for repo in self.controller.get_repos_at(location):
                print('  {}'.format(repo))

    def run_in_repos_parallel(self, repo_names, action, max_processes, quiet, clean):
        max_processes = int(max_processes)

        requested_repos = self.parse_repos(repo_names)
        processes = set()

        printable_action = ' '.join(action)

        while len(requested_repos) > 0:
            if len(processes) < max_processes:
                repo = requested_repos.pop()
                short_name = repo.split('/')[-1]

                repo_parent = self.controller.get_repo_path(repo)
                if repo_parent == None:
                    continue

                repo_location = '{}/{}'.format(repo_parent, short_name)

                if not clean and not quiet:
                    print("{}: executing '{}'".format(short_name, printable_action))

                processes.add(start_command(action, repo_location))
            else:
                finished = set()
                for process in processes:
                    if process_finished(process):
                        if not clean:
                            print("{}: finished".format(short_name))
                        if not quiet:
                            output, error, status = join_process(process)
                            sys.stdout.write(error or output)
                        finished.add(process)
                processes -= finished
                time.sleep(0.1)

    def run_in_repos(self, repo_names, action, quiet, clean):
        for repo in self.parse_repos(repo_names):
            repo_location = self.controller.get_repo_path(repo)

            if not repo_location:
                continue

            short_repo_name = repo.split('/')[-1]
            output, error, status = run_command(action, '{}/{}'.format(
                repo_location, short_repo_name
            ))
            if quiet:
                continue

            if error or output:
                if clean:
                    sys.stdout.write(error or output)
                else:
                    print('{}:'.format(repo))
                    print(error or output)


def main():
    try:
        commands = setup_commands()
        parser = setup_parser(commands)
        args = parser.parse_args()

        command = args.command
        command_args = vars(args)
        command_args.pop('command')

        if command == None: # annoying python 3 thing
            print(parser.format_usage())
            return
        
        command_runner = Commands(Controller())
        command_method = commands[command]['run']
        command_method.__get__(command_runner)(**command_args)
    except KeyboardInterrupt:
        pass
