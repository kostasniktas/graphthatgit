
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
