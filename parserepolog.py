
import gitraw
import glob
import os
import re

ZERO = "0000000"

class RepoLogParseStash:
    def __init__(self, directory):
        self.directory = directory

    def parse_repo(self):
        globs = glob.glob(os.path.join(self.directory,'*.repo'))

        # First parse the repo/HEAD files and store the log file
        repos = {}
        for currentrepo in globs:
            m = re.search('.*' + os.path.sep + '([0-9]+)\.repo', currentrepo)
            if m is None:
                continue
            repo_id = m.group(1)
            with open(os.path.join(self.directory,"%s.repo" % repo_id)) as f:
                repo_url = "".join(f.readlines()).strip()
            with open(os.path.join(self.directory,"%s.HEAD" % repo_id)) as f:
                repo_HEAD = "".join(f.readlines()).strip()
            with open(os.path.join(self.directory,"%s.log" % repo_id)) as f:
                repo_info = f.readlines()
            if repo_HEAD.startswith("ref: "):
                repo_HEAD = repo_HEAD[len("ref: "):]
            if len(repo_info) > 0:
                repos[repo_id] = gitraw.Repo(repo_id, repo_url, repo_HEAD)
                repos[repo_id].fulllog = repo_info

        # Parse the actual log contents, delete the pure contents
        for repo_id in repos:
            repo = repos[repo_id]
            commits = []
            commit = None
            for line in repo.fulllog:
                if line.startswith("commit"):
                    if commit is not None:
                        commits.append(commit)
                    commit = gitraw.State(line[len("commit "):].strip())
                    commit.repo = repo
                elif line.startswith("Author: "):
                    commit.author = line[len("Author: "):].strip()
                elif line.startswith("Date:"):
                    commit.date = line[len("Date:"):].strip()
                elif line.startswith("Merge:"):
                    commit.merge = line[len("Merge:"):].strip()
                elif line.startswith("diff"):
                    commit.diff = []
                    commit.diff.append(line)
                elif commit.diff is not None:
                    commit.diff.append(line)
                elif line.startswith(":"):
                    m = re.search(":(\d+)\s+(\d+)\s+([a-f0-9]+)(\.{3})?\s+([a-f0-9]+)(\.{3})?\s+[A-Z]\s+(.*)", line)
                    if m is not None:
                        if commit.blob_before is not None and commit.blob_after is not None:
                            # Try to deal with rename case
                            if commit.blob_before == ZERO:
                                commit.mode_before = m.group(1).strip()
                                commit.blob_before = m.group(3).strip()
                                commit.path = m.group(7).strip()
                            if commit.blob_after == ZERO:
                                commit.mode_after = m.group(2).strip()
                                commit.blob_after = m.group(5).strip()
                        else:
                            commit.mode_before = m.group(1).strip()
                            commit.mode_after = m.group(2).strip()
                            commit.blob_before = m.group(3).strip()
                            commit.blob_after = m.group(5).strip()
                            commit.path = m.group(7).strip()
                    else:
                        print "m is None for %s" % line
            if commit is not None:
                commits.append(commit)
            repo.commits = commits
            repo.fulllog = None

        return repos
