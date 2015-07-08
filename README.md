
[WORK IN PROGRESS]

== Manage your branches in git ==

This is especially useful if you use arcanist or some such tool which squashes your commit.

The model:

we track one "trunk" or "master" branch. By default this is "origin/master".

Every feature branch either starts from this branch or from another
feature branch.

Create a feature branch using the "feature" command:

        bark feature foo-bar

Every feature branch can have multiple dependencies on other feature
branches.

        bark feature foo-bar2
        bark add_dep foo-bar2 foo-bar

at this point you can continue working on both foo-bar and foo-bar2
branches. When you want to sync everything call:

        bark rebaseall

In particular this will rebase foo-bar2 onto the update foo-bar.

It will also rebase foo-bar onto the latest version of origin/master
(as retrieved from last fetch)

Now, if you have multiple features and you call add_dep, we'll enforce
that *all managed features start from the same commit on
origin/master*. This is a simplication to make it easy to think about
what's going on behind the scenes. If we see that you don't meet this
constraint we'll suggest you run "rebaseall" which will bring
everything to speed.

Once we have this database of dependencies, it's easy to write
programmatic things to handle dependencies. For example using arcanist
a common pattern is to diff against the parent diff, which can be
automated as:

        arc diff `bark get-root-diff` (TODO: implement get-root-diff)

You might also want to automatically list all the dependencies in your
arcanist message. As a first step you can get the list of all
dependencies using `bark get-deps` (TODO: implement), and then parse
the branches to find out what the phabricator diff is.
