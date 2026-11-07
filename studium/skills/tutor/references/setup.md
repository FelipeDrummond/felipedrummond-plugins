# Setup mode

The first run, when `HOME/data/roadmap.md` doesn't exist, or when he asks to set up again. Setup collects what the tutor can't know, then proposes an end goal and a roadmap for him to accept or change. Everything it writes goes in `HOME`, never in `S`.

## 1. Files, silently

Create what is missing, and change nothing that exists:

- `HOME/data/topics/` (empty folder).
- `HOME/data/open.json`: `{"on_hold": [], "repairs": [], "skipped": []}`, indented by 2 (shape in `references/session.md`, Recording).
- Sync the page assets: `rsync -a S/assets/ HOME/pages/assets/`.

`HOME/data/config.json` holds the settings. Read it before asking anything; ask only for what is null or missing.

| Key | Holds |
|---|---|
| `vault`, `target_date`, `timezone`, `session_minutes` | Known before setup |
| `tutor_calendar` | Calendar for the tutor's own events (`primary` is his main one) |
| `class_calendar` | Id of his class calendar, read-only |
| `review_weekday` | Lower-case English weekday, such as `sunday` |
| `review_time` | Local start time, `HH:MM`, 24-hour |

## 2. Questions, one per message

Each message asks exactly one thing, as everywhere in this skill. In this order, skipping any already answered:

1. **Class calendar**, only if `class_calendar` is null: `list_calendars`, and if exactly one calendar is plainly his classes, use its id; if several could be, ask which.
2. **Review block day and time.** Read his calendar first (`list_events`): if he already has a weekly review block of his own, suggest the hour next to it. Store `review_weekday` and `review_time`.
3. **End goal.** Propose one capstone, in one or two sentences, with the reason it fits who he wants to become and his courses (for example, a learned robot policy with a real stability argument; that is only an example). Ask whether he accepts it or wants to change it.
4. **Exam dates**, if any exist yet. "Not yet" is a fine answer; ask again in a later setup or when he mentions one. If an exam falls before `target_date`, propose moving `target_date` to the first exam and change it only if he agrees.
5. **Course material**, only if you can't find it: the path of the first course's own material (script, slides), since scope and notation come from it.

## 3. The roadmap

**The classes set the sequence, the roadmap sets the depth.**

- Start with one course: the one he names, or the first one his class calendar shows if he names none. Others are added later, one at a time, each with its own material.
- Read the course's class dates with `list_events` on `class_calendar`, from today to `target_date`. Use them to pace the course's topics in the order of its material. **Don't copy class dates into any file**: the calendar can change, so read it again when needed.
- Topics the classes won't reach, and topics the end goal needs that no course covers, are ordered back from `target_date`: the end goal's last step nearest the target, each prerequisite before what needs it, and every `own_it` topic early enough to be retested in the last two weeks before the target.
- **Every topic gets a tier and a reason**, stated as your judgment about what matters in a world before general AI, never as fact:

| Tier | Value | Meaning |
|---|---|---|
| Own it | `own_it` | Understood deeply, with no help |
| Do by hand, then delegate | `by_hand_then_delegate` | Done by hand until understood, then handed to tools |
| Know it exists | `know_exists` | Knows what it is and when to reach for it |

  Course requirements stay separate from value: a `know_exists` topic may still be on the exam.

Write `HOME/data/roadmap.md` in this shape:

```markdown
# Roadmap

End goal: one or two sentences.
Why: the reason, in one or two sentences.
Target date: YYYY-MM-DD
Exams: course-slug YYYY-MM-DD, or "none yet"

## Course name (`course-slug`)

Material: absolute path of the course's own material

| # | Topic | Slug | Tier | Reason | Status |
|---|---|---|---|---|---|
| 1 | Stability of linear systems | linear-stability | own_it | Every linearization argument rests on it | in progress |
| 2 | Lyapunov's direct method | lyapunov-direct | own_it | The only general stability proof without a closed-form solution | not started |
| 3 | A topic he chose to skip | some-slug | know_exists | Why it matters, and the risk of skipping it | skipped (YYYY-MM-DD) |

## Beyond the courses

Same table: topics the end goal needs that no course covers, ordered back from the target date.
```

- `Status` is one of `not started`, `in progress`, `skipped (YYYY-MM-DD)`. Never write a level or "mastered" here: the level is whatever `tutorlog.py level SLUG` says.
- Slugs match the topic files in `HOME/data/topics/`. Topic files are created when a topic is first tested, not at setup.

Then, in chat: the end goal, the first few topics with tier and reason, the full roadmap's path, and one question: does he accept it, or what should change? Change what he asks, then ask again. Setup is done when he accepts.

## 4. After setup

`HOME/data/review_state.json` is not created here; `references/review.md` writes it with the first block. Run "After any session that changes due dates" in `references/review.md`: with nothing due, `block-action` prints `none` and nothing is created. Then go on in the mode he asks for, by the table in `SKILL.md`.
