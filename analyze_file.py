
import gitraw
import glob
import graphviz
import json
import nodes
import os
import parserepolog
import re
import sys

DESTRUCTION = "%s-DESTRUCTION" % parserepolog.ZERO
CREATION = "%s-CREATION" % parserepolog.ZERO

source = sys.argv[1]
title_of_graph = sys.argv[3]
outputfile = sys.argv[2]

repos = parserepolog.RepoLogParseStash(source).parse_repo()

node_store = {}
node_store[CREATION] = nodes.Node(CREATION)
node_store[DESTRUCTION] = nodes.Node(DESTRUCTION)
for repo_id in repos:
    repo = repos[repo_id]
    previous_node = None
    for commit in repo.commits:
        if commit.merge is not None:
            continue
        if commit.blob_before == parserepolog.ZERO:
            previous_node = node_store[CREATION]
        if commit.blob_after == parserepolog.ZERO:
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

dot = graphviz.Digraph(graph_attr={"size":"17,11"})
dot.body.append(r'label = "%s"' % title_of_graph)
dot.body.append('fontsize=60')
for n in node_store:
    if len(node_store[n].outward) == 0:
        shape = 'doublecircle'
        style = 'filled'
        fillcolor = 'pink'
    else:
        shape = 'circle'
        style = ''
        fillcolor = ''
    if n == CREATION:
        title = "CREATION\n(%dout)" % len(node_store[n].outward)
    elif n == DESTRUCTION:
        title = "DESTRUCTION\n(%dcom, %din)" % (len(node_store[n].commits), len(node_store[n].inward))
    else:
        title = "%s\n(%dc, %di, %do)" % (n, len(node_store[n].commits), len(node_store[n].inward), len(node_store[n].outward))
    dot.node(n, title, shape = shape, style = style, fillcolor = fillcolor)
    for o in node_store[n].outward:
        dot.edge(n,o)
dot.render(outputfile, cleanup=True)


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
with open("%s.json" % outputfile,"w") as f:
    f.write(json.dumps(myjson,indent=4))
