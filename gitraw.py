
class Repo:
    def __init__(self, repoid, url, head):
        self.repoid = repoid
        self.url = url
        self.head = head
    def __str__(self):
        return "%s:%s:%s" % (self.repoid, self.url, self.head)

class State:
    def __init__(self, commit):
        self.commit = commit
        self.mode_before = None
        self.mode_after = None
        self.blob_before = None
        self.blob_after = None
        self.path = None
        self.merge = None
        self.diff = None

    def mode():
        return (self.mode_before, self.mode_after)

    def blob():
        return (self.blob_before, self.blob_after)
