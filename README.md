# Graph That Git

Super lame name :)


## Usage

Originally written to take in a directory of files and organize the data.  It expects
a directory of files in sets of three.  In the Stash git repository product, git repos
are stored by IDs and not by their URL.  So each file is of the form ``repoid.Extension``.
The extension is ``HEAD``, ``repo``, or ``log``.  The ``HEAD`` file is what HEAD references.
The ``repo`` file is the url.  The ``log`` file is the ``git log --raw --reverse -p`` output.
This assumes we're looking at one file across all repos.  Work in Progress.

Example of what the files look like
```console
$ ls
100.HEAD 100.repo 100.log
$ cat 100.HEAD
ref: refs/heads/master
$ cat 100.repo
git@stash.example.com:fooproject/awesome.git
$ head -10 100.log
commit 21ab4cde00076e554dc208d7423e8d63aed98b8b
Author: Some Guy <foo@example.com>
Date:   Tue Apr 1 16:13:23 2014 -0700

    fix all the bugs in my projects

:000000 100644 0000000... ba51b06... A  gradle/deps.gradle

diff --git a/gradle/deps.gradle b/gradle/deps.gradle
new file mode 100644
index 0000000..ba51b06
--- /dev/null
+++ b/gradle/deps.gradle
@@ -0,0 +1,47 @@
+buildscript {
```
