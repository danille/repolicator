import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from github import Github, GithubException
from git import Repo

from repolicator.settings import BASE_DIR

logger = logging.getLogger()

from core.forms import ReplicationForm


def index(request):
    return render(request, 'core/index.html')


def try_create_repo(user, repo_name):
    try:
        repo = user.create_repo(repo_name)
    except GithubException as e:
        logger.error(f'Error occurred during repo creation.')
        logger.error(e)
        repo = None

    return repo


def try_push_local_repo_to_remote(remote_repo):
    local_repo = Repo(BASE_DIR)
    new_remote_name = remote_repo.full_name.replace('/', '_') + '_remote'
    try:
        new_remote = local_repo.create_remote(new_remote_name, remote_repo.clone_url)
        push = new_remote.push()
    except Exception as e:
        logger.error(f'Error occurred during pushing to remote')
        logger.error(e)
        push = None

    return push


@login_required
def replicate(request):
    if request.method == 'POST':
        replication_form = ReplicationForm(request.POST)
        if replication_form.is_valid():
            repo_name = replication_form.cleaned_data['repository_name']
            social = request.user.social_auth.get(provider='github')
            access_token = social.extra_data['access_token']
            github = Github(access_token)
            user = github.get_user()
            created_repo = try_create_repo(user, repo_name)
            if created_repo:
                print('Successfully created repo and replicated it')
                push = try_push_local_repo_to_remote(created_repo)
                if push:
                    return render(request,
                                  'core/index.html',
                                  {'message': 'Code has been successfully replicated into specified repo'})
                else:
                    replication_form.add_error('repository_name',
                                               'Something went wrong while replication. Please, try again later, we are working on it')
            else:
                replication_form.add_error('repository_name', 'Repository with such name already exists. Try another')
    else:
        replication_form = ReplicationForm()

    return render(request, 'core/replicate.html', {'replication_form': replication_form})
