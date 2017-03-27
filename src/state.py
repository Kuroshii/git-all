import json
import os

class State:
    def __init__(self, file_location):
        self.file_location = file_location
        self.state = self._retrieve_state()

    def remove_user_credentials(self, user):
        self.ensure('user').pop(user, None)

    def update_user_credentials(self, user, auth_secret):
        self.ensure('user')[user] = auth_secret

    def get_user_credentials(self, user):
        return self.ensure('user').get(user)

    def list_users(self):
        return self.ensure('user').keys()

    def get_default_user(self):
        return self.ensure('default').get('user')

    def set_default_user(self, user):
        if user:
            self.ensure('default')['user'] = user
        else:
            self.ensure('default').pop('user', None)

    def list_groups(self):
        return self.ensure('group').keys()
            
    def remove_repository_group(self, group_name):
        self.ensure('group').pop(group_name, None)

    def add_to_repository_group(self, group_name, new_repos):
        existing_repos = self.get_repository_group(group_name)
        self.ensure('group')[group_name] = list(set(new_repos) | set(existing_repos))
        
    def get_repository_group(self, group_name):
        return self.ensure('group').get(group_name, [])

    def set_repo_path(self, repo, path):
        self.ensure('repo', repo)['path'] = path

    def add_repo_location(self, path, repo):
        path_repos = self.ensure('repo_locations', path).get('repos', [])
        path_repos.append(repo)
        self.ensure('repo_locations', path)['repos'] = path_repos

    def get_repo_path(self, repo):
        return self.ensure('repo', repo).get('path');
        
    def list_repo_locations(self):
        return self.ensure('repo_locations').keys()

    def get_repos_for_repo_location(self, path):
        return self.ensure('repo_locations', path).get('repos', [])
        
    def ensure(self, *path):
        cur_dict = self.state
        for path_component in path:
            if path_component not in cur_dict:
                cur_dict[path_component] = {}
            cur_dict = cur_dict[path_component]                
        return cur_dict

    def _retrieve_state(self):
        try:
            state = json.load(open(self.file_location))
        except IOError:
            state = {}
        return state

    def _save(self):
        json.dump(self.state, open(self.file_location, 'w'))

    def __del__(self):
        self._save()


def get_state():
    file_path = os.path.abspath(__file__)
    project_path = os.path.dirname(os.path.dirname(file_path))
    return State('{}/conf/credentials.conf'.format(project_path))
