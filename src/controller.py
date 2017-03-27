import bitbucket_client
import state


class Controller:
    def __init__(self):
        self.state = state.get_state()

    def list_users(self):
        return self.state.list_users() or []
    
    def list_teams(self, user):
        auth_secret = self.state.get_user_credentials(user)

        return bitbucket_client.get_teams(auth_secret)

    def list_projects(self, user, team):
        auth_secret = self.state.get_user_credentials(user)

        return bitbucket_client.get_projects(team, auth_secret)
    
    def add_user(self, user, auth_secret):
        self.state.update_user_credentials(user, auth_secret)

        if not self.default_user():
            self.state.set_default_user(user)

    def drop_user(self, user):
        self.state.remove_user_credentials(user)

        if self.state.get_default_user() == user:
            self.state.set_default_user(None)

    def default_user(self):
        return self.state.get_default_user()

    def get_repos_for_user(self, user):
        repos = []
        for team in sorted(self.list_teams(user)):
            repos += self.get_repos_for_team(user, team)
        return repos

    def get_repos_for_team(self, user, team):
        repos = []
        for project in sorted(self.list_projects(user, team)):
            repos += self.get_repos_for_project(user, team, project)
        return repos

    def get_repos_for_project(self, user, team, project):
        print("Getting repos for project: {}:{}".format(team, project))
        auth_secret = self.state.get_user_credentials(user)

        return bitbucket_client.get_project_repositories(
            team, project, auth_secret
        )

    def list_repository_groups(self):
        return self.state.list_groups()
            
    def delete_repository_group(self, group_name):
        self.state.remove_repository_group(group_name)

    def list_repository_group(self, group_name):
        return self.state.get_repository_group(group_name)

    def add_to_repository_group(self, group_name, repos):
        self.state.add_to_repository_group(group_name, repos)

    def add_repo_path(self, repo, path):
        self.state.set_repo_path(repo, path)
        self.state.add_repo_location(path, repo)

    def list_repo_locations(self):
        return self.state.list_repo_locations()

    def get_repos_at(self, location):
        return self.state.get_repos_for_repo_location(location)

    def get_repo_path(self, repo):
        return self.state.get_repo_path(repo)
