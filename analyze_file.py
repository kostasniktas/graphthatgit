
import gitraw
import sys
import os
import glob
import re

source = sys.argv[1]
globs = glob.glob(os.path.join(source,'*.repo'))
# just regex it for id

repos = {}
for currentrepo in globs:
    m = re.search('.*' + os.path.sep + '([0-9]+)\.repo', currentrepo)
    if m is None:
        continue
    repo_id = m.group(1)
    with open(os.path.join(source,"%s.repo" % repo_id)) as f:
        repo_url = "".join(f.readlines()).strip()
    with open(os.path.join(source,"%s.HEAD" % repo_id)) as f:
        repo_HEAD = "".join(f.readlines()).strip()
    with open(os.path.join(source,"%s.log" % repo_id)) as f:
        repo_info = f.readlines()
    if repo_HEAD.startswith("ref: "):
        repo_HEAD = repo_HEAD[len("ref: "):]
    if len(repo_info) > 0:
        repos[repo_id] = gitraw.Repo(repo_id, repo_url, repo_HEAD)
        repos[repo_id].fulllog = repo_info

print "%d repos with data." % len(repos)

for repo_id in repos:
    repo = repos[repo_id]
    commits = []
    commit = None
    for line in repo.fulllog:
        if line.startswith("commit"):
            if commit is not None:
                commits.append(commit)
            commit = gitraw.State(line[len("commit "):].strip())
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
                commit.mode_before = m.group(1).strip()
                commit.mode_after = m.group(2).strip()
                commit.blob_before = m.group(3).strip()
                commit.blob_after = m.group(5).strip()
                commit.path = m.group(7).strip()
    if commit is not None:
        commits.append(commit)
    repo.commits = commits
    repo.fulllog = None

#for i in repos:
#    print repos[i], len(repos[i].commits)
