# Strategic Intelligence Project — Git Delivery Workflow

## Purpose

This is the sole documentation authority for Git delivery procedure. Git itself
remains authoritative for branch, SHA, upstream, remote equality, staging,
worktree, containment, and integration truth. Execution, safety, Card closure,
and evidence rules belong in `AGENTS.md`.

## Card Branch Workflow

```text
verified main
→ create one authorized Card branch
→ implement and validate the one Card
→ Final Closure
→ approved commit and Card-branch push
→ approved fast-forward integration into main
→ verify Git delivery
→ STOP
```

Before creating a Card branch, verify dynamically that local `main` equals
`github/main`, `main` is the default branch, and the tracked worktree is clean.
Create the branch from that verified `main`; never base a new Card on an older
completed Card branch.

## Staging and Commit

Before an authorized commit:

1. inspect `git status` and the complete diff;
2. stage only approved Card files;
3. run `git diff --cached --check` and inspect the staged diff;
4. confirm no secrets, `.env`, credentials, caches, generated artifacts, or
   unrelated files are staged; and
5. commit one coherent, validated change using an accurate message.

For a Card with an identified cross-Card composition surface, the staged
evidence must include its required composed Critical Path or regression proof.

Commit only with explicit user authorization. Do not claim validation that did
not run.

## Push and Integration

Push only the approved branch normally and verify its upstream and remote SHA.
An approved Card may be integrated only with explicit user authorization.

For integration:

1. verify the approved Card commit is a clean descendant of current `main`;
2. update local `main` with fast-forward-only behavior if required;
3. fast-forward `main` to the approved Card commit; and
4. push `main` normally and verify local/remote equality and commit containment.

Preserve completed Card branches unless explicit policy or user approval allows
deletion. Do not create a merge commit, rebase, squash, force-push, or rewrite
history unless separately and explicitly authorized.

## Post-Delivery Verification

After delivery, Git must show the expected branch/remote equality, approved
commit containment in `main`, preserved Card branch, and clean tracked
worktree. The next Card remains stopped until separately authorized. No
control-only reconciliation commit is required unless a durable documentation
statement itself needs correction.

## Guiding Rule

**Git proves delivery facts. Evidence records their historical meaning.**
