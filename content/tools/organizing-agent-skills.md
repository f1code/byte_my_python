Title: Organizing Agent Skills
Date: 2026-07-12
Modified: 2026-07-12
Category: Tools
Tags: agent-skills, developer-tools, skills

Most agents (Codex, Pi, OpenCode, and so on) will by default look for global skills under `~/.agents/skills`, but it’s not an established standard. Claude Code and Cursor, for example, only use their own skill folder. The same applies within a project. Regardless of where skills are stored, the structure inside the skills folder is similar: individual folders that each contain at least a `SKILL.md` file, plus some reference documents or scripts. That part is getting standardized—see [agentskills.io](https://agentskills.io/specification).

I started my [skills](https://github.com/f1code/skills) repo a few weeks ago, in an attempt to organize a growing collection of both custom and third-party skills.

## The challenges

My challenges are:

- I periodically want to try out new third-party skills, to test a new workflow or just play with something new.
- When I have a third-party skill, I want to be able to keep it updated...
- ...but I might also want to customize that third-party skill.
- And then, in addition to that, I have my own custom skills to edit and maintain.

## Managing installed skills

A new-ish tool from Vercel makes that possible, aptly named "[skills](https://github.com/vercel-labs/skills)."

It lets you:

- install a new skill to the global or project folder, given a Git repo or a path within a repo;
- track installed third-party skills in a `.skill-lock.json` file;
- update those skills using `npx skills@latest update`;
- list installed third party skills, based on the skill lock file: `npx skills@latest ls -g`
- remove individual installed skills using `remove` (though only individual skills right now)

The `.skill-lock.json` has a `package-lock.json` feel but is more focused on updates. It’s useful because it lets me install and uninstall skills without messing with my custom skills. By keeping everything under Git, I can also make tweaks to third-party skills if I want to try small changes—being careful when updating them, since `npx skills update` will silently overwrite changes.

## My layout

I organize my repo like this:

- `.agents/.skill-lock.json` — the lock file from `skills`
- `.agents/skills/*` — all third-party skills
- `.agents/skills/custom/*` — all my custom skills

Agents will recursively discover skills, so you can use any organization you like within the repo. I haven’t done that yet, but I have seen developers divide skills between engineering-focused and research-focused work. There is not yet a way to activate a specific portion of the skills for a given agent session, though, so the organization is just to keep things tidy, not to increase agent performance.

## Take away

This is a growing area of exploration and one where we as senior developers can really leverage our software engineering experience to boost the whole team.
The need for composable, modular skills is crucial and good organization is paramount - I feel this is going to be a
crucial need and one worth mastering.  
I have been doing quite a bit of experimentation - as always, I mostly learn by doing - and will be sharing that in the
future on this blog as well, so stay tuned!
