"""
Python script used to create a GitLab release
Freely inspired from https://pypi.org/project/gitlab-auto-release/

Author: Matteo Lupi

In order for the process to work, an token should be created for a user
with permission to create the release. The token can be created (logging-in
as the bot executing the release) at https://gitlab.cern.ch/-/profile/personal_access_tokens.
The token should be added as a masked variable (not protected) in
https://gitlab.cern.ch/cmshgcalasic/econd_rtl/-/settings/ci_cd.
"""

import os
import re
import sys

import argparse
import gitlab


class Release:
    """Class handling the release on GitLab
    The parameters needed are passed as part of the __init__ method"""
    project = None
    gitlab_url = None
    project_url = None
    private_token = None
    project_id = None
    assets = None
    tag_name = None
    def __init__(self, private_token, project_id, gitlab_url, project_url):
        """Class to handle the release and sanitise the input parameters

        input:
        private_token (str):  Private GITLAB token, used to authenticate when
                               usign the API
        project_id (int):     Unique indentifier of the gitlab project
        gitlab_url (str):     URL to to the gitlab server
        project_url (str):    URL to to the gitlab project
        """
        if project_url is None:
            try:
                project_url = os.environ["CI_PROJECT_URL"]
            except KeyError:
                print("project_url not provided and CI_PROJECT_URL env not defined")
                sys.exit(1)
        self.project_url = project_url
        self.gitlab_url = gitlab_url
        self.private_token = private_token
        self.project_id = project_id
        self.get_project()

    def create(self, tag_name, asset, artifacts, changelog, dry_run=False):
        """Creates the release
        input:
        tag_name (str):   The tag name i.e. release_v0.1.0, must contain
                           semantic versioning somewhere in the tag (0.1.0).
        asset (list):     A list of tuples in the format "name,link".
                           These will be included in the release.
        artifacts (list): A list Of jobs from current pipeline to link
                           artifacts from.
        changelog (str):  Path to changelog file.
        changelog (str):  If True, does not create the release
        """
        self.tag_name = tag_name
        assert self.tag_name is not None, "tag_name not set"
        self.check_if_release_exists()
        self.add_assets(asset)
        self.add_artifacts(artifacts)
        description = self.get_changelog(changelog)
        self._create(description, dry_run)

    def get_project(self):
        """Assigns the project variable"""
        gtlb = gitlab.Gitlab(self.gitlab_url, private_token=self.private_token)
        try:
            self.project = gtlb.projects.get(self.project_id)
        except gitlab.exceptions.GitlabGetError as err:
            print(f"Unable to get project {self.project_id}. Error: {err}.")
            sys.exit(1)

    def check_if_release_exists(self):
        """Checks if the release already exsists for that project."""
        exists = False
        try:
            gitlab_release = self.project.releases.get(self.tag_name)
            if gitlab_release:
                exists = True
        except gitlab.exceptions.GitlabGetError:
            pass
        if exists:
            print(f"Release already exists for tag {self.tag_name}.")
            sys.exit(0)

    def add_assets(self, asset=None):
        """Gets the asset in the correct format for the API request to create
        the release and include these extra assets with the release.
        generates:
            list: (of dicts), which includes a name and url for the asset
                              we will include in the release.
        Raises
            IndexError: When format is incorrect
        """
        assets = []
        if asset:
            try:
                for item in asset:
                    asset_hash = {"name": item.split(",")[0], "url": item.split(",")[1]}
                    assets.append(asset_hash)
            except IndexError:
                print(f"Invalid input format asset {asset}.")
                print("Format should be \"name,link_to_asset\"")
                sys.exit(1)
        self.assets = assets

    def add_artifacts(self, artifacts):
        """Gets the artifacts from the job name specified. Gets the current
        pipeline id, then matches the jobs we are looking finds the job id.
        generates (updated) version of the assets
            list: (of dicts), which includes a name and url for the asset we
                    will include in the release.
        Raises
            IndexError: When the job doesn't exist in the pipeline jobs list
                        or when the CI_PIPELINE_ID env is not defined.
        """
        assets = []
        if artifacts:
            assert isinstance(artifacts,(list,tuple)),"Artifact parameter should be list or tuple"
            try:
                pipeline_id = os.environ["CI_PIPELINE_ID"]
            except KeyError:
                print("Could not find pipeline_id: env CI_PIPELINE_ID must be defined")
                sys.exit(1)
            pipeline = self.project.pipelines.get(pipeline_id)
            jobs = pipeline.jobs.list()
            for artifact in artifacts:
                try:
                    matched = [job for job in jobs if job.name == artifact][0]
                    job_id = matched.id
                    artifact_link = {"name":
                                     f"Artifact: {artifact}",
                                     "url":
                                     f"{self.project_url}/-/jobs/{job_id}/artifacts/download"}
                except IndexError:
                    print(f"One of the jobs specified not found: cannot link artifact {artifact}")
                    sys.exit(1)
                assets.append(artifact_link)
        self.assets += assets

    def _get_changelog(self, changelog):
        """Gets details from the changelog to include in the description of the release.
        The changelog must adhere to the keepachangelog format.
        Returns
            str: The description to use for the release
        """
        with open(changelog, "r") as change:
            content = change.read()
            semver = r"((([\d]+)\.([\d]+)\.([\d]+)(?:-([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)" # pylint: disable=C0301
            semver_tag = re.search(semver, self.tag_name).group(0)
            if semver_tag:
                semver_changelog = f"## [{semver_tag}]"
                description = "\n\n\n"

                position_start = content.find(semver_changelog)
                if position_start:
                    position_end = content[position_start + 2 :].find("## [")
                    position_end = (position_end + position_start + 2) if position_end != -1 else -1
                    description = content[position_start:position_end]
        return description

    def get_changelog(self, changelog):
        """Tries to retrieve changelog and raises if not found.
        Returns
            str: The description to use for the release
        Raises:
            AttributeError: If the tag_name doesn't contain semantic versioning somewhere within
                             the name.
            FileNotFoundError: If the file couldn't be found.
            OSError: If couldn't open file for some reason.
        """
        if not os.path.isfile(changelog):
            print(f"Unable to find changelog file at {changelog}.")
            sys.exit(1)
        try:
            return self._get_changelog(changelog)
        except (IndexError, AttributeError):
            print(f"Invalid tag name doesn't contain a valid semantic version {self.tag_name}.")
            sys.exit(1)
        except OSError:
            print(f"Unable to open changelog file at {changelog}.")
            sys.exit(1)

    def _create(self, description, dry_run=False):
        release_info = {"name": self.tag_name,
                        "tag_name": self.tag_name,
                        "description": description,
                        "assets": {"links": self.assets}}
        if dry_run:
            print(f"Dry run done. Release info: {release_info} ")
        else:
            self.project.releases.create(release_info)
            print(f"Created a release for tag {self.tag_name}.")


def parse_args():
    """Parses the input from CLI"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-pt", "--private_token", required=True, help="Private GITLAB token, used to authenticate when usign the API")  # pylint: disable=C0301
    parser.add_argument("-i", "--project_id", type=int, required=True, help="Unique indentifier of the gitlab project")  # pylint: disable=C0301
    parser.add_argument("-gu", "--gitlab_url", required=False, help="URL to to the gitlab server", default='https://gitlab.cern.ch')  # pylint: disable=C0301
    parser.add_argument("-pu", "--project_url", required=False, help="URL to to the gitlab project", default=None)  # pylint: disable=C0301
    parser.add_argument("-t", "--tag_name", required=True, help="The tag name i.e. release_v0.1.0, must contain semantic versioning somewhere in the tag (0.1.0)")  # pylint: disable=C0301
    parser.add_argument("-ar", "--artifacts", required=False, help="Job name from current pipeline to link artifacts from, repeatable", action='append', default=[])  # pylint: disable=C0301
    parser.add_argument("-as", "--asset", required=False, help="Tuple in the format \"name,link\" (no branckets, no \"\"). These will be included in the release, repeatable", action='append', default=None)  # pylint: disable=C0301
    parser.add_argument("-c", "--changelog", required=False, help="Path to CANGELOG.md file", default='CHANGELOG.md')  # pylint: disable=C0301
    parser.add_argument("-d", "--dry_run", required=False, help="If called, it runs without the last step of creating the release", action='store_true')  # pylint: disable=C0301
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rls = Release(args.private_token, args.project_id, args.gitlab_url, args.project_url)
    rls.create(args.tag_name, args.asset, args.artifacts, args.changelog, args.dry_run)
