# About this file

This file, branches.md, describes the recommended way for Leo's devs to create and use git branches.<br>
It also describes Leo's most important branches. 

Many thanks to Marcel Franke for suggesting the organization described here.

Devs, please add/delete a branch description here when creating/deleting a branch. <br>
*Commit the change to the devel branch*.

# Overview of branches

Devs may create a branch at any time.  The most important branches:

- **master**: a permanent, stable branch,  suitable for even the most timid users.
- **devel**: a permanent, quasi-stable branch. Everthing new comes from devel and goes to devel.
- **Feature branches**:  Unstable. Devs are expected to run all unit tests before pushing to devel.
- **Release branches**: These contain all work on a single, specific release.  Example, 5.7.1.
  These branches should contain *only*:
  - All distribution-related work.
  - Urgent last-minute bug fixes.<br>

<img width="75%" height="75%" src="leo/Icons/Gitflow-Workflow-3.png">

# Branch descriptions

Devs, please add your descriptions here.

## master

- A permanent, stable branch, suitable for pulling by the most timid users.
- Updated only as the result of merging a release branch into master.

## devel

- A permanent, quasi stable branch, the target of all development work.
- Devs are expected to run all unit tests before pushing to devel.

## proto

- A long-lived branch a long-lived branch containing prototype code related to client/server/javascript/vue.js code.
- There are no plans to merge or delete this branch at this time.
