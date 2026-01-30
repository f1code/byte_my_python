Title: Why Git's Linear Log Can Lie to You
Date: 2026-01-30
Category: Tools
Tags: git, version-control, debugging

When your team uses merge commits instead of rebasing, `git log` can deceive you. That flat, linear list of commits doesn't tell the whole story — and if you're trying to figure out what's actually in a release, you might draw the wrong conclusions.

Here's a scenario I ran into recently.

## The Setup

I opened a PR yesterday for a bug fix on our release branch. The PR was approved but only merged today. Meanwhile, yesterday the CI pipeline built and tagged a release image from the same branch.

Looking at `git log`, you might think my fix made it into that image:

```text
9c2600b (HEAD -> release/2.9.0, origin/release/2.9.0) Merged in fix/user-session-timeout (pull request #1532)
faf20e5 Merged in fix/dashboard-label-update (pull request #1528)
31b3a38 (tag: release/2.9.0-build-1678) Merged in fix/array-null-check (pull request #1529)
a992bf9 DASH-456 update E2E with fixed label update
72da568 (origin/fix/user-session-timeout) SESSION-789: set up connection pooling
7ca61c1 SESSION-789: fix for mock use in unit tests
a598fd9 SESSION-789: work around timeout in tests
346236a SESSION-789: ensure session is not eagerly bound
3d2d424 Merged in fix/picklist-value-type (pull request #1530)
095b0c1 fix PICK-234 incorrect value for picklist
```

See the problem? The commits from my branch (`72da568`, `7ca61c1`, etc.) appear *before* the release tag at `31b3a38`. A quick glance suggests they're included in the build.

But they're not.

## The Reality

Run `git log --graph --oneline --decorate` instead, and the true picture emerges:

```text
*   9c2600b (HEAD -> release/2.9.0, origin/release/2.9.0) Merged in fix/user-session-timeout (pull request #1532)
|\  
| * 72da568 (origin/fix/user-session-timeout) SESSION-789: set up connection pooling
| * 7ca61c1 SESSION-789: fix for mock use in unit tests
| * a598fd9 SESSION-789: work around timeout in tests
| * 346236a SESSION-789: ensure session is not eagerly bound
* |   faf20e5 Merged in fix/dashboard-label-update (pull request #1528)
|\ \  
| * | a992bf9 DASH-456 update E2E with fixed label update
| * | 7b14e0c (origin/fix/dashboard-label-update) DASH-456 fix label update issue
* | |   31b3a38 (tag: release/2.9.0-build-1678) Merged in fix/array-null-check (pull request #1529)
|\ \ \  
| |_|/  
|/| |   
| * | f85fe64 (origin/fix/array-null-check) ARRAY-567: handle undefined array
| |/  
* |   3d2d424 Merged in fix/picklist-value-type (pull request #1530)
```

Now you can see that my fix branch runs *parallel* to the main line. The merge commit that actually incorporates those changes (`9c2600b`) comes *after* the release tag. My fix wasn't in the build.

## Why This Happens

Without rebasing, feature branches keep their original commit timestamps. When merged, Git interleaves these commits chronologically in the flat log view — even though they weren't actually part of the main branch until the merge commit.

The flat `git log` essentially overlays the log from the feature branch onto the trunk. You end up reading multiple parallel histories stacked on top of each other based on date, which can be deeply misleading.

## Reading the Log Correctly

Two approaches to get the truth:

**1. Use `--graph`** to see the actual branch structure:

```bash
git log --graph --oneline --decorate
```

**2. Use `--first-parent`** to see only the merge commits on the main line:

```bash
git log --first-parent --oneline
```

This shows you exactly what was merged and when, ignoring the individual commits within each branch. The order of these merge commits can be trusted.

Most Git hosting platforms (GitHub, GitLab, Bitbucket) also show this graphically in their commit views — branches in flight run parallel until the merge commit actually brings them in.

## A Case for Rebasing

This experience reinforced why rebasing is worth the effort, especially for longer-lived branches (more than a week or so):

**When syncing with the main branch**: Rebase rather than merge. Don't use the "Sync" button in Bitbucket or similar — it creates a merge commit that interleaves histories. Instead:

```bash
git fetch origin
git rebase origin/main
```

**Before merging your PR**: Squash trivial commits (typo fixes, "oops" commits, etc.) into logical units. This keeps the history readable and makes each commit meaningful.

**Why it matters**:

- `git log` reads linearly and accurately represents the state of the repo at each point in time
- `git bisect` works correctly — you can binary search through commits to find regressions without getting lost in parallel histories
- Rolling back to a pre-merge state is straightforward
- Code review is easier when commits tell a coherent story

When you merge without rebasing, the histories become intermingled. Going back to the pre-merge version of a branch or using `git bisect` to analyze regressions becomes challenging because you're navigating through multiple parallel timelines that have been flattened into one.

## Takeaway

If your team uses merge commits, remember that `git log` without flags can mislead you about what's actually in a given commit or tag. When debugging "is this fix in production?", reach for `--graph` or `--first-parent` to get the true story.

And if you want to avoid these headaches altogether, consider rebasing your feature branches before merging — especially the long-lived ones. Your future self (and your teammates) will thank you when bisecting a regression at 2 AM.
