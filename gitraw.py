
class Repo:
    def __init__(self, repoid, url, head):
        self.repoid = repoid
        self.url = url
        self.head = head
    def __str__(self):
        return "%s:%s:%s" % (self.repoid, self.url, self.head)

class State:
    def __init__(self, commit, mode_before, mode_after, blob_before, blob_after, path):
        self.commit = commit
        self.mode_before = mode_before
        self.mode_after = mode_after
        self.blob_before = blob_before
        self.blob_after = blob_after
        self.path = path
        # contents = the full contents of file
        # diff = the diff contents of change
        pass

    def mode():
        return (self.mode_before, self.mode_after)

    def blob():
        return (self.blob_before, self.blob_after)
