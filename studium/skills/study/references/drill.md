# Problem drill

Exercise sheets, tutorial problems and old exams. This is where grades are made in an
engineering degree, and where an assistant does the most damage by being helpful: a solution
that is read feels like a solution that was found, and it is not.

## Steps

1. **Read the problem and the student.** Identify the course hub and read its `## Error log`,
   plus the tutor notes: you want to know what kind of mistake this student tends to make
   before you look at their work. Check the profile for the concepts the problem needs. For a
   full sheet or exam PDF, have a subagent extract the problem statements. If an official
   solution exists (a Musterlösung in the same folder), it is ground truth for you and stays
   hidden from them.
2. **Get an independent solution.** Send a subagent the problem statement only, not their
   attempt, and ask for: the governing principle, the full solution, the final answers, the
   key intermediate results, and likely wrong turns. It should check the result with sympy or
   numpy (symbolic identity, a numeric spot check, units, a limiting case) and reconcile with
   the official solution if there is one. If it is unsure, or disagrees with the official
   solution, tell the user so instead of bluffing.
3. **Attempt first.** If they have not tried yet:
   - ask them to name the principle or method and say why it applies, before any algebra.
     Recognising which tool a problem calls for is the skill the exam tests and the sheet hides,
     since sheet 5 is always about chapter 5;
   - then they work on it for ten to fifteen minutes.
4. **Stuck? Use the hint ladder.** Give the lowest rung that unblocks them, one rung per turn,
   and hand the problem back each time.

   | Rung | What you give |
   |---|---|
   | 1 Locate | Ask where exactly they are stuck and what they have tried. |
   | 2 Orient | What is asked, what is given, which quantity connects them. |
   | 3 Principle | Name the governing principle, or point at their own note (`[[Jacobian]]`) or an analogous problem. |
   | 4 Setup | The first equation, the free-body diagram, the choice of frame. |
   | 5 One step | Carry out the next step only. |
   | 6 Full solution | Only when they ask for it outright. Then add the problem to the hub's `## Redo queue` with a date three days out, to be solved again from a blank page. |

   If the sheet counts toward the grade (bonus points, graded homework), stop at rung 4; it has
   to be their work. Ask whether it is graded only when you are about to go past rung 4.

   When you give them a check to run, make it something they can actually run or see: a few
   lines of numpy, a figure of the configuration (`visuals.md`), or a pose they can picture ("arm straight up: which way can the tip
   move when only the elbow turns?"). An invariant they can reuse on every problem of this kind
   ("det J cannot depend on q1, since q1 only rotates the whole arm") is worth more than the
   fix itself.
5. **Checking an attempt.** Find the **first** wrong step; everything after it is noise. Point
   at the line and ask what is off there. One retry, then explain. Also check what they did not:
   units, sign, a limiting case. A right answer reached by wrong reasoning counts as wrong, and
   say so. If the mistake matches one already in the error log, say that it is a repeat and
   which: a pattern they can name is a pattern they can watch for, and a check they can run
   every time ("differentiate, then substitute a number") is worth more than this one fix.
6. **Classify and log the error.** Decide the type yourself and log it straight away, so the
   record exists even if the session stops here. Tell them the type you chose in a clause; if
   they see it differently, change the entry.

   | Type | Meaning |
   |---|---|
   | `concept` | Did not know or misunderstood the principle. |
   | `setup` | Right principle, wrong model: frame, sign convention, boundary condition, free-body diagram. |
   | `execution` | Algebra or arithmetic slip. |
   | `units` | Dimensions or unit conversion. |
   | `reading` | Misread what was asked or given. |
   | `time` | Knew how, ran out of time. |

   Append to the hub's `## Error log`:
   `- 2026-10-20 · Sheet 3 P2 · setup · [[Jacobian]] — used the body frame where the space frame was asked`

   Write the second half as a rule for next time, in their words where they offered them. For a
   `concept` error, also `record` a `miss` on that concept note so it comes back tomorrow; if
   there is no such note, propose a stub. When the same pattern has now shown up three times,
   add it to `meta/Tutor notes.md` under recurring patterns.
7. **After it is solved**, two quick things, because solving one instance is not yet knowing the
   method: the key idea in one sentence, and one variation answered qualitatively ("what
   changes with friction at the joint?", "what if the base is moving?").

## Exam preparation sets

When they are working a batch of problems for an exam:

- Mix problems across sheets and topics instead of going in sheet order.
- Run it timed and without hints; go through errors only at the end.
- Read the `## Error log` first and report the pattern: "four of your last six errors are
  `setup`, mostly sign conventions". That tells them what to practise, which is more useful than
  another problem.
- Clear the `## Redo queue` before starting anything new.
