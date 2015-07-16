
class Node:
    def __init__(self, blob):
        self.blob = blob
        self.inward = []
        self.outward = []
        self.commits = []

    def __str__(self):
        return "%s : In[%d] Out[%s] Commits[%s]" % (self.blob, len(self.inward), len(self.outward), [x.commit for x in self.commits])
