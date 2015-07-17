
import gitraw
import sys
import os
import json
import glob
import re
import nodes
import graphviz

ZERO = "0000000"
DESTRUCTION = "%s-DESTRUCTION" % ZERO
CREATION = "%s-CREATION" % ZERO

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

#print "%d repos with data." % len(repos)

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

node_store = {}
node_store[CREATION] = nodes.Node(CREATION)
node_store[DESTRUCTION] = nodes.Node(DESTRUCTION)
for repo_id in repos:
    repo = repos[repo_id]
    #previous_node = node_store[CREATION]
    previous_node = None
    for commit in repo.commits:
        if commit.merge is not None:
            continue
        if commit.blob_before == ZERO:
            previous_node = node_store[CREATION]
        if commit.blob_after == ZERO:
            current_node = node_store[DESTRUCTION]
        else:
            if commit.blob_after not in node_store:
                node_store[commit.blob_after] = nodes.Node(commit.blob_after)
            current_node = node_store[commit.blob_after]
        current_node.commits.append(commit)
        if previous_node.blob not in current_node.inward:
            current_node.inward[previous_node.blob] = previous_node
        previous_node = current_node

for n in node_store:
    for i in node_store[n].inward:
        if n not in node_store[i].outward:
            node_store[i].outward[n] = node_store[n]

node_store[CREATION].inward = {}
node_store[DESTRUCTION].outward = {}
#TODO: Doesn't deal with multiple files in one repo correctly.  Maybe just Blob Sha transitions

dot = graphviz.Digraph(comment='par.gradle in stash', graph_attr={"size":"17,11"})
for n in node_store:
    if len(node_store[n].outward) == 0:
        shape = 'doublecircle'
    else:
        shape = 'circle'
    if n == CREATION:
        title = "CREATION\n(%dout)" % len(node_store[n].outward)
    elif n == DESTRUCTION:
        title = "DESTRUCTION\n(%dcom, %din)" % (len(node_store[n].commits), len(node_store[n].inward))
    else:
        title = "%s\n(%dc, %di, %do)" % (n, len(node_store[n].commits), len(node_store[n].inward), len(node_store[n].outward))
    dot.node(n, title, shape = shape)
    for o in node_store[n].outward:
        dot.edge(n,o)

dot.render('pargradle', cleanup=True)


myjson = {}
myjson["repos"] = []
for repo_id in repos:
    repo = repos[repo_id]
    repo_json = {"url":repo.url, "HEAD":repo.head, "commits":[]}
    for commit in repo.commits:
        repo_json["commits"].append({"sha":commit.commit, "mode_before":commit.mode_before,
                                     "mode_after":commit.mode_after, "blob_before":commit.blob_before,
                                     "blob_after":commit.blob_after, "path":commit.path,
                                     "merge":commit.merge, "author":commit.author, "date":commit.date})
    myjson["repos"].append(repo_json)

myjson["blobs"] = []
for n in node_store:
    node = node_store[n]
    myjson["blobs"].append({"blob":node.blob, "commits":[x.commit for x in node.commits],
                            "inblobs":node.inward.keys(), "outblobs":node.outward.keys()})
with open("pargradle.json","w") as f:
    f.write(json.dumps(myjson,indent=4))
