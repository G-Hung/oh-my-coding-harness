# I Just Want My Coding Agent to Leave Me Alone

> English text-only snapshot from the author's coding-agent article, source revision
> `f725a01da74b0a37a0d14d70ef983f3b1f088c00`, captured 2026-10-18.
> Images and their captions are omitted; the sweep skill name is updated.
> This is background reading. The current [adoption guide](../adoption.md)
> governs installation, including separate explicit approval for AGENTS.md edits.

A year ago, AI was already pretty good at writing code. I was still the one sitting in front of an IDE, reading what it wrote, fixing things, and nudging it along. Then, toward the end of the year, coding agents got a lot better, very quickly. I started catching myself thinking, *Why am I still doing this part?* Before long, I barely wanted to open my IDE at all.

Naturally, I went down the rabbit hole of how everyone else was using them. Skills, workflows, spec-driven development, context engineering, multi-agent orchestration, Ralph loops… Some genuinely useful ideas in there, but also an impressive number of shiny new things to learn, install, and manage.

I kept coming back to one question: **Does any of this actually get me out of the implementation loop, without requiring a second job supervising agents?**

There's an old management analogy about the monkey on your back. Someone brings you a problem, you say, “I'll take a look,” and suddenly *their* problem is *your* problem. Coding agents are surprisingly good at this. “All done! Here are a few dozen files and a few thousand lines of diff for you to review.”

Hold on. When did I become my agent's human subagent? And how did the monkey end up on my head?

What I want is simple. We make the important decisions together in Plan Mode. Then I get out of the way. When the agent is done, I want something that's already been tested, reviewed, and fixed, ready for me to merge or open up and try. Not a cheerful “Done!” followed by an afternoon of cleanup.

So I started putting more effort into the environment my agents work in: make the repo easier to understand, give the agent useful feedback when something breaks, and leave it enough clues to fix things without coming back to me. Ideally, the monkey never makes it onto my back in the first place.

## TL;DR

My setup is on GitHub: [oh-my-coding-harness](https://github.com/G-Hung/oh-my-coding-harness).
The harness tools are free, and you can pick only the pieces your project needs; your coding-agent subscription and tokens are still yours to pay for.
The copy-and-paste adoption prompt is at the bottom, if you want your agent to work out which pieces are worth stealing.

## I only want to be involved at two points

Suppose an agent spends an hour building a substantial feature. It writes a few thousand lines of code, tests them, gets a review, and fixes what the reviewer finds without needing me. Great. I can spend that hour thinking about the product, planning the next feature, or doing something else that actually benefits from having a human involved.

Now suppose another agent finishes in twenty minutes but pulls me back in every five. Technically, it's faster. In practice, I can't get anything else done. Every time I switch my attention to something useful, I get dragged straight back into implementation.

And it's usually for the same reasons. The feature works, but it isn't what I wanted. The new flow works, but an old one broke. All the tests are green, yet the app is obviously wrong as soon as I open it. Then there are the slower problems: files that keep growing, logic implemented three different ways, architectural decisions quietly forgotten a few PRs later.

After running into enough of these, I started asking a different question whenever I had to step in: **How could the agent have caught this without me?** That question is where the following layers came from.

## Layer 1: Spend the human attention in Plan Mode

This is the one place I'm happy to spend more time. It takes judgment to decide which patterns to reuse, which ones to introduce, and what architectural tradeoffs to make. Product taste and lessons learned the hard way matter here too. The agent can research options, explain tradeoffs, and push back on my ideas. I want it to. But we still need to agree on what we're building before anyone starts writing code.

Take something as ordinary as adding a filter to a dashboard. Should the filter state live in the URL? What should survive a refresh? Where does the permission check belong? Should we stick with an existing component or introduce a better pattern? None of these questions is especially difficult on its own, but the answers shape the implementation. I also want to settle what we're *not* doing, which existing behavior must stay intact, and what would count as a successful result.

Usually I ask the agent to propose an approach, then apply my own judgment to it. If it can make a convincing case for something better, this is the time to change my mind. **I'd rather spend ten extra minutes here than discover, a few thousand lines later, that we agreed to build the wrong thing.** Once the direction is clear, I leave the implementation details to the agent. It only needs to come back when it hits a real contradiction or a decision that changes the agreed design.

## Layer 2: Don't make me run a command just to discover a failure

I used to find myself asking the same questions over and over: “Did you run typecheck? What about regression tests? Have you actually opened the app?” After the third reminder, it finally occurred to me that I was doing a job a script could do better.

My repo now has checks at different stages: fast feedback while the agent works, required checks before committing, and a broader set before handing the change back. With the harness's TypeScript kit, for example, these are the commands available from the project root after adoption:

```sh
npm run lint
npm run typecheck
npm run check:readme -- --staged
npm run check
```

The first three run during pre-commit; pre-push runs `npm run check`. Builds, browser checks, integration tests, and E2E tests plug into the project's own commands. The exact script names aren't the point. The point is that the agent gets the failure, can read the actual error, and is expected to fix it before declaring victory. Local hooks give it immediate feedback, while CI provides another gate. There's no reason to spend model tokens having an AI rediscover what TypeScript already knows.

Of course, passing typecheck doesn't mean the product works. I also want the agent to start the app, open a browser, walk through the important flows, and check the screen, console, and API responses. Integration and E2E tests are especially useful when a change crosses modules or touches permissions and state. Unit tests can happily pass while the real user flow is broken.

I can buy more compute. I can buy more tokens. What I can't buy is another uninterrupted hour of my own attention. **If I still have to remind the agent to run a test, I haven't really delegated the work.**

## Layer 3: Skip the fancy memory system. Write better READMEs.

Agents can read code. What they can't always infer is why the code looks the way it does. Why was this module split in two? Why did we avoid that dependency? Which public interface was deliberately kept stable?

I keep that context close to the code. A submodule gets its own README when it needs one, with a short description of what it owns, what it shouldn't touch, how to verify changes, and a bit of decision history.

I stole a useful tip from [Karpathy](https://x.com/karpathy/status/2105819303471976479): ask an LLM to explain things in ASD-STE100, the simplified English developed for aerospace maintenance documentation. Short sentences, consistent terminology, less room for creative interpretation. He also suggests going about 80% of the way if the full standard feels too stiff. I've borrowed that spirit for my READMEs. We're helping the next agent find its way around, not servicing an aircraft.

The catch, obviously, is keeping those READMEs current. I have a small script that checks which files changed and finds the nearest README. If the code changed but the README didn't, pre-commit asks the agent whether the module's behavior or interface has changed too. If the docs need an update, update them; if not, explain why. The reviewer also checks that the implementation hasn't wandered outside the documented boundaries.

It's a small nudge, not a rule that every code change requires a documentation edit. But it means the next agent working in that module can pick up the reasoning behind earlier decisions without dragging me back in to explain it all again.

## Layer 4: Fight magic with magic

Even a clean build and green tests can leave real bugs behind. So once the implementation passes its checks, I hand it to a separate reviewer agent.

The implementer writes the code; the reviewer tries to break it. Any findings go back to the implementer, and the fixes go back to **the same reviewer**. That last part matters. I want the reviewer to follow its own issues to resolution, not forget them as soon as another model enters the conversation.

Otherwise you get a strange little committee of amnesiacs: one reviewer flags A, the next gets interested in B, and a third decides the architecture should be rewritten. Very busy. Still no clear answer on whether A was ever fixed.

A useful review finding should say what's wrong, where it happens, and how to verify the fix. A vague “looks good to me” doesn't count. The main agent can spin up subagents for investigation, implementation, or testing whenever it makes sense; I'm not interested in micromanaging its staffing. I just want it to own the result and keep the review/fix loop going until the issues are resolved and the required checks pass, unless there's a good reason to stop.

That exception is interesting. Occasionally a task spends far too long bouncing between review and fixes. One change breaks another; a supposedly straightforward feature turns into five rounds of corrections. Bad news: maybe the abstraction is wrong, the architecture doesn't fit, or the requirements contradict each other. Good news: **at least the problem has made itself obvious.**

Instead of burning tokens on an endless “try again,” the agent should stop and tell me what it tried, what's still failing, what it suspects, and what decision it needs from me. That's exactly the kind of interruption I *do* want.

Most of the time, the handoff should be boring: what changed, which checks passed, which review findings were fixed, and anything the agent thinks deserves my attention. Ideally, everything required is already green when I get back.

## So do I still review every line of code?

At first, my answer was a very firm yes. Of course I should. I'm responsible for the code, so I need to understand every line and every function before it goes in. Having an AI write it doesn't magically transfer the responsibility to a chat window.

Then the agents got faster. They could produce code much faster than I could read it. A few thousand lines would arrive, I'd sit down to review them, and another task would finish while I was still reading the first. The whole operation had acquired a very expensive single-threaded bottleneck. Hello, it's me.

The more uncomfortable realization was that, even in the areas I know best, the AI often writes better code than I would. So what exactly am I checking as I scroll through all this? Sometimes I have a useful observation. Sometimes I'm just reassuring myself that I have personally witnessed each function exist.

The failures that really hurt were usually further upstream. We'd built the wrong behavior. We'd chosen a design that made the next change painful. Or everything passed, but the product clearly wasn't doing what we had agreed. Reading every line wasn't where I was adding the most value.

So for most noncritical changes, I no longer do it. I spend more of my attention on the plan and design, then check the actual result. For an easy-to-roll-back change, I'll usually let it merge into the development branch, open the app in the dev environment, and try it. Does it do what we agreed? Does it feel right? Enforceable style rules and conventions belong in scripts, lint, and checks; I don't need to earn my keep by pointing out the same formatting issue for the twelfth time.

This still takes judgment. Data models, payments, security-sensitive code, and data migrations can have a much bigger blast radius and may be hard to undo. For those, I slow down, break the work into explicit steps, inspect the important design choices and code, and verify each step before moving on.

And if I do catch a bug at the end, I want one extra thing answered: why didn't the earlier checks catch it? What would let them catch it next time? A test, a rule, or a change to the design itself? Since you've already dragged me back in, we might as well patch the hole while I'm here. Please don't page me for the same thing twice.

## The monkeys in one task

Here's what those layers are meant to take off my plate:

| The monkey | What it used to make me do | What handles it now |
| --- | --- | --- |
| A feature goes in the wrong direction | Revisit the requirements after the code is written | **Plan Mode:** agree on behavior, design, and acceptance criteria first |
| Typecheck or tests fail | Run commands, read logs, tell the agent to fix them | **Scripts and test gates:** send failures straight back to the agent |
| The UI or an integration breaks | Become the manual QA team | **Browser checks and integration/E2E tests** |
| Design decisions get forgotten | Explain the architecture all over again | **Module READMEs, pre-commit reminders, and reviewer checks** |
| The implementation has bugs | Investigate and track every fix myself | **A consistent reviewer:** follow findings through to resolution |

None of this makes agents infallible. It just means more of their mistakes are discovered and dealt with before they become my problem.

## Once one works, why not start another?

Once I could trust one agent to take a task from an agreed plan to something ready for a final look, I started wondering why I was only running one.

Welcome to worktrees. Each task gets its own working directory, so independent tasks can run side by side. I plan the first one and send it off, then start planning the next while the first is busy. The catch is that this only works if the agents can mostly look after themselves. If one agent needs rescuing every ten minutes, five worktrees don't give you five times the productivity. They give you five places to put out fires.

Right now, five main agents is about my limit. If I counted every subagent and reviewer they spin up, I could probably claim I'm managing fifty agents. 🤷‍♂️ But five is about how many separate plans and outcomes I can comfortably keep track of.

Separate directories don't prevent two tasks from changing the same files. Overlap warnings can flag files changed by both branches, giving an early hint of likely shared-file edits; merge-readiness checks can then catch concrete conflicts against the chosen base and peer branches. Useful tools when the monkeys start collaborating. Neither tells you that two cleanly merging features make sense together.

I tend to give each agent a reasonably substantial feature, with a PR taking somewhere around 30–60 minutes. While the first task runs, I work through the plan for the second; once that's started, I move to the third. By the time I've kicked off the fifth, the first is often about ready for me to look at. On a good day, that's five substantial changes moving forward in a couple of hours, without five implementation loops competing for my attention.

## Every PR can be reasonable, and the codebase can still become a mess

The first feature needs API retries, so the agent adds retry logic. The second needs retries too, so it adds another version. Then a third feature comes along. Each PR makes sense on its own, and each passes tests and review. A few weeks later, we have three almost-identical retry implementations with just enough differences to be annoying.

Congratulations. Now even fixing the retry logic comes with three choices.

A reviewer can flag duplication too, but keeping separate implementations may have made sense at the time. Once several features are in place, it may be worth pulling that logic into something shared. That's why I like doing a regular sweep across recent changes: look for drifting module boundaries, duplicate DIY solutions, inconsistent patterns, and security issues that only become visible when you consider how different pieces now fit together.

I like this part because it's not just cleanup. It's a chance for me to catch up with where the codebase has gone. Does the architecture still make sense after all these features? Is it time to extract something we previously kept local? Which shortcuts were sensible a month ago but have now outlived their usefulness?

I go over the findings with the agent and choose the refactors worth doing, then send the agreed work through the same implementation, checks, review, and fix loop. Sometimes I'll kick it off at the end of the day so I can come back the next morning to a tidier starting point. A sweep is not permission to refactor everything it finds.

## Put the whole thing together

The four layers handle a single task. Worktrees let independent tasks run alongside each other. The sweep steps back and asks what all those individually reasonable changes have done to the codebase. I still choose the direction and judge the result; I just don't want to be the courier carrying every failed check from one agent to another.

The nicest part is how little there is to manage once it's in place. I work as usual; checks run at the right points, and failures go straight back to the agent. Much of the time, I don't even notice the harness doing anything. The things it catches simply stop turning into tasks for me.

Which has left me with a problem I didn't expect: **where am I supposed to find enough good ideas to keep them all busy?**

I used to worry that my backlog was growing faster than my product. Now I'm starting to worry it won't grow fast enough. That's a problem I can live with.

I'm curious where you draw the line: which changes do you still read yourself, and which have you handed over to agents and checks? Any monkeys still refusing to get off your back?

## Want to give your agent the setup?

I've mostly built and tested this in **OpenAI Codex**, but the workflow doesn't depend on one product. If you use Claude Code, Cursor, or another coding agent, I'd love to hear what needs adapting. The prompt below asks your agent to inspect your setup before proposing what to bring over.

Open **Plan Mode**, or your agent's equivalent planning workflow, and paste this in. It should compare the reference repo with your project and propose what to adopt, adapt, keep, or skip. You don't have to install everything.

Also check which models it plans to hire. Please don't copy my entire staffing budget by accident. The plan should show who implements, who reviews, and which models and reasoning settings they use, so you can confirm or change the lineup.

```text
Read https://github.com/G-Hung/oh-my-coding-harness.
Use its README's adoption instructions and asset list as
your starting point.

Inspect my project's instructions, code, architecture,
languages, and existing checks. Assess the listed assets
item by item, including ship-cycle, code-sweep, guidelines,
and test gates. Recommend what to add, adapt, keep, or skip,
with reasons specific to my project.

Inspect the coding-agent product and execution environment,
including available models and the model and reasoning
settings supported for each role. Propose a main agent,
helpers, and an independent reviewer, with supported
reasoning settings. Briefly explain the quality, speed,
and total-cost tradeoffs. Separate confirmed availability
from access or settings that still need my input. Do not
copy model defaults blindly. If a proposed role cannot use
a model or setting here, propose a supported alternative.
Include any model-policy changes in the same adoption plan
and approval before applying them.

Follow the README's approval process. Present one adoption
plan for my explicit approval; I can approve it all or select
items in one reply. Then carry out the approved scope.
Never overwrite my existing AGENTS.md; propose targeted
additions instead. Leave changes uncommitted for review.
```

For Codex, once you've approved the plan and adopted `ship-cycle`, explicitly invoke the skill to run the agreed implementation, checks, review, and fix loop. Switch out of Plan Mode into execution mode when needed, then send:

```text
$ship-cycle execute
```

That's my recommended handoff into the full workflow. The **Implement** button's behavior depends on the environment and applicable instructions; explicitly naming the skill makes the workflow you want clear.
