Title: Loop Engineering: A Balance of Human and Agent
Date: 2026-06-25
Modified: 2026-06-25
Category: Tools
Tags: ai-agents, loop-engineering, kanban, workflow, code-review

Like many engineers these days, I spend a lot of time on so-called "loop engineering". The core question isn't really which model or tool is fastest—it's about the balance between human and agent. How do you get the agents to do the heavy lifting, while making sure you intervene at exactly the times where you, the human, add the most value?

I have been working on a skill based on the [kanban-md](https://github.com/antopolskiy/kanban-md) tool. It already ships with a skill, but I wanted to tailor it to my workflow—run more controlled bites and know when it needed to involve me. And then I have some other skills I use once in a while or experiment with, most notably the superpowers skill, which just came up with some enhancements.

I ran the same fleshed-out plan two different ways.

## First run

I did a test with a plan broken down into tasks, using the superpowers skill and the subagent-driven workflow.
This is a lot of agent control and it decides exactly where to spawn sub-agents (which it does a lot).

It took a long time, almost 1h30 (it actually took a lot longer because I had to keep granting permissions, but that was my setup). TBH I'm not sure I would not have been faster coding it by hand.  The permission friction is really my problem there (part of loop engineering).

For the record, the cost:

```text
  Total cost:            $37.26
  Total duration (API):  1h 18m 28s
  Total duration (wall): 15h 42m 18s
  Total code changes:    1661 lines added, 170 lines removed
  Usage by model:
       claude-opus-4-8:  35.0k input, 116.0k output, 15.9m cache read, 3.3m cache write ($31.79)
     claude-sonnet-4-6:  197 input, 56.8k output, 10.0m cache read, 364.7k cache write ($5.22)
      claude-haiku-4-5:  425 input, 9.7k output, 1.4m cache read, 49.9k cache write ($0.2511)
```

## Second run

Next I tried the same plan with the kanban-loop skill I devised, using [kanban-md](https://github.com/antopolskiy/kanban-md) (it's in my [skills](https://github.com/f1code/skills) repo). I first asked it to split the plan into sequential tasks (it created 3), then set it to work.

This took 1h4. It is really nice to be able to check the progress on the kanban board—that's a much healthier place for the human to sit in the loop: glancing at status rather than approving every step. Though I still need to get the agent to be a bit more communicative on its progress when updating the tasks. It was cheaper at $13.92 (I used [pi-crust](https://github.com/f1code/pi-crust) to calculate that, which is based on estimates—it might not be as accurate).  To take with a huge grain of salt - this was absolutely not a formal benchmark.  But I am not convinced Claude's strategy of aggressively spawning sub-agents always pays off.

## Where the human actually added value

I asked an agent to run a comparison between the two branches. The first implementation let a significant bug through! But it had a more thorough implementation for one of the tasks. Apparently they were both solid (mind you, I hadn't looked at the code yet at this point).

Once I looked at the code myself I figured out very fast that both implementations were actually not great—because the plan sucked and I didn't review it carefully. So it goes to show: crap in, crap out.

But here's the loop-engineering lesson. Seeing the code made the problem obvious in a way that staring at the plan never did. The most valuable human intervention wasn't babysitting permissions or even reviewing the plan up front—it was reading the output once the agent had taken a first pass. For $13, that wasn't too bad. Sometimes there is a lot of value in letting the agent run ahead so you can find the rough edges in your own thinking more quickly than you would by reviewing a plan.  There is another version of the skill that takes a hard break after each sub-task for the human to review, and I think, even though we would like for this to be fully automated and hands-off, that's a better proposition.  Then it really comes down to where you want to place the seams, to have something that is reasonably to review, but large enough that you still have a good gain of time from it.
