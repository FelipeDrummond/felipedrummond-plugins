# Review mode and the weekly block

Everything due is grouped into one weekly block of one hour, at the day and time in `HOME/data/config.json` (`review_weekday`, `review_time`). The block is tracked three ways: the log, one calendar event, and one one-time scheduled task that opens the review. `T` below means `python3 S/scripts/tutorlog.py`.

## Live test

Not yet run. To be filled in after the scheduled review has fired once with the student present: whether the task found `HOME` and read the due list, whether he could reply and it continued, and whether a second run did nothing.

If a scheduled session turns out unable to find `HOME` or to wait for his replies, the fallback is: the event's description tells him to start `/tutor` in `HOME` and say "weekly review", and the task only prepares the due list (`T due --for block`) and stops.

## The state file

`HOME/data/review_state.json`, JSON indented by 2:

```json
{
  "block_date": "YYYY-MM-DD",
  "event_id": "id from create_event",
  "task_id": "id from create_scheduled_task",
  "completed": false,
  "overflow_history": [0, 2]
}
```

Setup creates it with every id and `block_date` null: `block_date` null means no block yet, and `block-action` treats it like a missing file. `overflow_history` holds one number per finished block: how many due topics didn't fit it. Read the file before changing it and write every field back.

## After any session that changes due dates

Run this at the close of every session, repair, exam practice and review (the step in `references/session.md`, Closing). It keeps exactly one event and one task for the next block, or none.

1. **The block date** is the next `review_weekday` on or after today. If that is today and `review_state.json` has today's block with `completed: true`, it is the same weekday next week.
2. `T block-action --block-date D`. It prints `create`, `update`, `delete` or `none`, and a warning line when the last two blocks both overflowed.
3. **A stale block first.** If the stored block has a different `block_date` and `completed: false`, and it has an `event_id` or `task_id`, delete those first, whatever the action: `delete_event` (calendar `tutor_calendar` from config) and `delete_scheduled_task`. Set both ids to null. This is a block from an earlier week that never ran, or one from before the review day changed; its topics are still due, so they are in the new block.
4. Act on the answer:

| Answer | Do |
|---|---|
| `create` | Create the event and the task (below). Write `block_date: D`, both new ids, `completed: false`; keep `overflow_history`. |
| `update` | If both ids are stored: `update_event` with the new title (the count changes), plus a new start time and `update_scheduled_task` with a new `fireAt` only if `review_time` changed. If the ids are null, create instead, as for `create`. |
| `delete` | Nothing is due by `D` any more: `delete_event` and `delete_scheduled_task` by the stored ids, then set both ids to null. |
| `none` | Nothing to do: either nothing is due (a week with nothing due gets no block) or this block is already finished. |

5. **The warning line**, if printed: tell him in the closing message that more is due than one block holds for the second week running, and that it is his decision whether to add a block. If he wants one, he starts a review himself in one of his own study blocks.
6. Say in the closing message what changed, in one line: "[Weekly review: Sunday 16:00, 4 topics, event and reminder created.]"

If a delete reports that the event or task no longer exists, carry on: he may have removed it. Any other error from the calendar or the scheduler: tell him, and change nothing else in the state file.

You only ever touch the event and the task whose ids are stored. Never edit or delete any other event.

### Creating the event

- Calendar: `tutor_calendar` from config. Class dates come from `class_calendar`, which is read-only.
- Count: `N` is the number of topics `T due --for block --block-date D` prints (at most 6).
- Check for clashes first: `list_events` on both calendars for the hour starting `review_time` on `D`. A clash is not an error and doesn't stop scheduling: create the event and the task at `review_time` anyway, and tell him in the closing message the clashing event's time and title. He decides whether to move the block; if he does, use `update_event` and `update_scheduled_task` with the new time.
- `create_event`: `summary` "Tutor weekly review: N topics", start at `review_time` with `timeZone` from config, length `session_minutes`, `description` "Weekly retest block from the tutor. A review session should open by itself. If it doesn't, start /tutor in HOME_ABS and say: weekly review." (with `HOME`'s absolute path).
- **No topic names and no questions in the event or the task.** He knows a review is coming, not what it asks.

### Creating the task

- `create_scheduled_task` with `taskId` `tutor-review-D`, `title` "Tutor weekly review", a one-line `description`, and `fireAt` at the event's start as ISO 8601 with the offset for that date: `python3 -c "from datetime import datetime; from zoneinfo import ZoneInfo; print(datetime(2026, 11, 15, 16, 0, tzinfo=ZoneInfo('Europe/Berlin')).isoformat())"` (date, time and zone from the block and config).
- The task starts a fresh session in an unknown folder, runs only while the app is open, and otherwise runs at next launch. So its prompt must be self-contained. Fill in this template:

```text
Use the tutor skill (/studium:tutor, or /tutor) in review mode for the weekly review block dated BLOCK_DATE.

The tutor's home folder is HOME_ABS. Run its scripts with TUTOR_HOME=HOME_ABS, or pass --data HOME_ABS/data to tutorlog.py.

First read HOME_ABS/data/review_state.json. If it is missing, if its block_date is not BLOCK_DATE, or if completed is true, reply with one line saying this review has nothing to do, and stop.

Otherwise read SKILL_DIR/SKILL.md and SKILL_DIR/references/review.md, and run the review block as review.md says, waiting for the student's replies.
```

`HOME_ABS` is `HOME` as an absolute path, read from where you resolved it now. `SKILL_DIR` is `S` as an absolute path now: the installed plugin's copy, or the repo checkout while the plugin isn't installed.

## Running the review block

Load `references/session.md` too: the reply shape, clock, recording, confidence, flags, correctness and page rules all apply. This file replaces its "Before teaching" and "Opening a topic": a review asks about topics he has already studied, so there is no course-position question, no prerequisite quiz and no motivation-first opening.

1. **Which block.** Started by the scheduled task, the block is the one in `review_state.json`, and the prompt has already checked it is still owed; a block run late (the app was closed) still runs. Started by him ("weekly review", or an extra block after an overflow warning), run it now.
2. `T clock start`. The review is its own block.
3. **The agenda**, in this order, with no topic twice:
   1. Topics from `T due --for session` (failed retests come first there).
   2. Topics from `T due --for block` (today's date), in its order: tier, then longest overdue. Keep the `overflow: N` number it prints.
   3. Topics with `"retest_without_notice": true` not already listed, if time remains.

   The clock, not the count, decides how far you get. Topics not reached stay due and come up in the next session or block.
4. **Each topic**, in turn:
   1. **Read, silently:** the topic file (`mistakes`, `evidence`) and its vault note (`flag.py find`). Show him nothing from them.
   2. **Explain from memory:** one question asking him to state or explain the topic's core result without looking (kind `state` or `conceptual`).
   3. **New questions:** an unseen system (different structure, not new numbers), aimed at his recorded mistakes. Check each with code before setting it.
   4. **Record every answer** with `"surprise": true` (he knew a review was coming, not the questions), plus `"unseen_system": true` where it applies. All of a topic's items on one date are one retest: any answer that isn't correct fails it, and `record` sets the next date from that (a failure brings it back in 2 days, and `due --for session` then lists it first in any session, so it doesn't wait for the next block). Set `retest_without_notice` to `false` after it, and `patched` to `false` only if the retest passed.
   5. **Update the flag** (Flags, in `references/session.md`), and say in the record line whether the retest passed or failed.
5. **Page:** the review's notes page is `HOME/pages/reviews/review-YYYY-MM-DD.html`, built as in `references/notes-page.md`.
6. **Closing** at 5 minutes left or when the agenda is done. First, in `review_state.json`: if the stored block is not completed and its `block_date` is today or earlier, append the `overflow` number to `overflow_history` and set `completed: true`. Otherwise leave the file alone: a review he started before the block's day leaves that block in place (it shrinks, or goes when nothing is due), and a block replaced meanwhile by a later session's plan is not this one. Only then follow `references/session.md`, Closing; its step 3 runs "After any session that changes due dates" above, which now plans next week's block instead of touching this one.

## Red flags

| About to | Instead |
|---|---|
| Show the note or his old answer before he explains | Ask him to explain from memory first |
| Ask the same exercise again with new numbers | An unseen system aimed at his mistakes |
| Record a review answer without `surprise` | `"surprise": true` on every review item |
| Put topic names or questions in the event or task | "Tutor weekly review: N topics", nothing more |
| Create a second event for the same week | Act on `block-action`; delete a stale block first |
| Edit or delete an event you didn't create | Only the stored `event_id` |
