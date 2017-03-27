# git-all

A simple client for managing operations over a set of repostitories, with special integration with bitbucket teams and projects.

## Setup

First, you'll need to install the source locally. To do that, run `install.sh $BIN_DIR $LIB_DIR`.

This will place an executable named `git-all` at `$BIN_DIR`, which points to the source, which will be placed at `$LIB_DIR/git-all` (along with the internal configuraiton).

### Adding Credentials

To add a user to access some bitbucket repositories, run `git-all add-user`. This will save the username and base64-encoded password to the internal configuration, so `git-all` can talk to bitbucket on your behalf.

### Adding Repos to a Group

There are three ways to refer to a set of repos:
- Referring to a single repo by name e.g. `auth-server`
- Referring to a known group, prefixed by a '/' e.g. `/frontends`
- Referring to a user, team, project combination, e.g. `@my-user/my-organization/my-project`
    - If user is omitted, then the default user (as shown by `git-all list-user`) is used
    - If the project is omitted, then all projects for that team will be considered.
    - For example, a common case is `git-all add-repo @/my-org my-group`, which will add all of the repos from all of the projects in the team `my-org` as accessed by the default user to the group `my-group`

### Installing Repos

Running `git-all install REPOS`, where `REPOS` refers to a repo specification like above, will clone each of the specified repos into the current folder.

### Registering Repos

Running `git-all register REPOS` will register `REPOS` as installed in the the proper name of each repo under the current directory.

### Running commands

To run a command simultaneously across several repos, run `git-all do REPOS COMMAND`.
