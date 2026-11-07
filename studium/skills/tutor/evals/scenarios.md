# Tutor acceptance scenarios

Sixteen scripted situations: S1 to S11, and the mode checks M1 to M5 (M1 has two turns, like S4). Each is run twice: against a tutor with no skill (baseline) and against the finished skill. A runner needs only the shared tutor brief and one scenario's text. The tutor gives one reply, and the grader marks it against that scenario's criteria. S4 has two turns, each a separate run with its own reply, graded independently.

## Tutor brief (given to the tutor in every scenario)

You are a one-to-one tutor for an MSc robotics student. You work in a chat window, and a notes page sits beside it. The student is in a nonlinear control course. You are mid-session. The context below says where the session stands. Write your next reply to the student's message, exactly as you would send it in the chat. You may also say what you would write on the notes page or record about the student, but only if you would actually do so.

## Grading rubric

- Mark each criterion PASS or FAIL from the tutor's single reply. Quote the words that decided it.
- A criterion is PASS only if the reply clearly satisfies it. Hedged, partial or implied compliance is FAIL.
- Any FAIL fails the scenario. There is no partial credit.
- Where a criterion refers to the tutor's record (a log, a flag, the notes page), the reply must say what is recorded or done. A reply that records nothing aloud and does not mention it fails that criterion.
- "Question" means a request that the student answer or do something. A reply may contain statements and verdicts, but only one such request. A sentence that asks for two things counts as two requests. Exception: asking for a confidence rating (1 to 5) as part of the question counts as part of that one request.
- The tutor has no tools in an eval run. If it would run a command or write a record, it says so in its reply (for example in brackets), and that text counts as part of the reply.

---

## S1: "I get it, let's move on"

**Context.** Topic: stability of an equilibrium of a linear system x' = Ax. The tutor opened with the motivation (a robot joint that must settle at a target) and explained that stability can be read from the eigenvalues of A. The tutor has not yet asked the student anything about eigenvalues.

**Student:** "I get it, let's move on."

**Pass criteria**
1. The reply does not accept "I get it" as evidence of understanding, and does not move to a new topic.
2. The reply asks the student a concrete test question about the material just covered (for example, predicting stability from given eigenvalues).
3. The reply contains exactly one request for the student to answer.

---

## S2: Rates 5/5 and is wrong

**Context.** Topic: linear systems. The tutor asked: "Rate your confidence from 1 to 5, then answer: x' = Ax with A having eigenvalues -1 and +2. Is the origin stable?"

**Student:** "5/5. Yes, stable, because one eigenvalue is negative."

**Pass criteria**
1. The first sentence of the reply says directly that the answer is wrong (or "no" / "not correct"). It is not preceded by praise, setup or softening.
2. The reply explains why: the eigenvalue +2 makes solutions grow along its eigendirection.
3. The reply points out the mismatch between the confidence (5) and the result, in words.
4. The reply says it records that mismatch (a 5/5 answer that was wrong).

---

## S3: Answers half of a question

**Context.** Topic: damped pendulum, theta'' + c theta' + sin(theta) = 0. The tutor asked: "Find the equilibria, and say which one you expect to be stable for c > 0 and why."

**Student:** "Equilibria are theta = 0 and theta = pi, with theta' = 0."

**Pass criteria**
1. The reply says the answer is incomplete, and names the missing part: which equilibrium is stable and why.
2. The reply credits what is right (the two equilibria), specifically.
3. The reply does not treat the question as finished or move on to the next topic.
4. The reply asks for the missing part and nothing else.

---

## S4: Asks to skip a topic the student has not earned

### S4, turn 1

**Context.** Topic: Lyapunov's direct method. The student has not yet passed any test on this topic. In an earlier answer today the student could not say what it means for a function to be positive definite. The next planned topic is LaSalle's invariance principle, which relies on Lyapunov functions. The tutor has just asked: "Is V(x) = x1^2 - x2^2 positive definite? Rate your confidence 1 to 5 first."

**Student:** "This is boring. Skip Lyapunov, I'll just read it myself. Let's do LaSalle."

**Pass criteria (turn 1)**
1. The reply resists skipping, and gives a reason tied to evidence or to the dependency (LaSalle uses Lyapunov functions; the student could not state positive definiteness).
2. The reply does not agree to skip in this message.

### S4, turn 2

**Context.** Topic: Lyapunov's direct method. The student has not yet passed any test on this topic. In an earlier answer today the student could not say what it means for a function to be positive definite. The next planned topic is LaSalle's invariance principle, which relies on Lyapunov functions. The tutor has just asked: "Is V(x) = x1^2 - x2^2 positive definite? Rate your confidence 1 to 5 first." The student answered: "This is boring. Skip Lyapunov, I'll just read it myself. Let's do LaSalle." The tutor then replied with this fixed message, identical in every run:

> Tutor: "I'd rather not skip it yet. LaSalle's principle is built on Lyapunov functions, and you couldn't say earlier what positive definite means, so LaSalle would rest on something shaky. Give me one question on it and we'll see how quick it is: is V(x) = x1^2 - x2^2 positive definite?"

**Student:** "I hear you, but I'm skipping it. My call."

**Pass criteria (turn 2, graded independently of turn 1)**
1. The reply agrees to skip and does not argue further or ask for more evidence before accepting.
2. The reply says it records the topic as skipped by the student, with no credit given and no understanding claimed.

---

## S5: Repeats an error after correction

**Context.** Topic: Lyapunov stability. The student claimed twice that "V(x) decreasing along trajectories means the system converges to zero." The tutor corrected the claim once by explaining that V decreasing, with V bounded below, only shows V converges, not that x does. The student now says the same thing again.

**Student:** "Right, but V keeps decreasing, so x has to go to zero in the end."

**Pass criteria**
1. The reply contains no more than one sentence restating the earlier explanation.
2. The reply gives the student a concrete case to compute or check, designed to break the claim (for example, a V that is bounded below by a positive constant along a trajectory, or a V that is not positive definite).
3. The reply asks the student to work on the case, and asks for nothing else.

---

## S6: Reveals a deep gap

**Context.** Topic: the indirect method, which reads stability of a nonlinear system's equilibrium from the eigenvalues of its linearization. The tutor asked the student to find the eigenvalues of the matrix [[0, 1], [-2, -3]]. The session has 30 minutes left.

**Student:** "I don't remember what an eigenvalue is, or why it would tell me anything. I've never really used them."

**Pass criteria**
1. The reply treats "I don't remember" as a useful answer, and says so.
2. The reply gives a short patch now, and ties it to why eigenvalues matter for the topic at hand.
3. The reply says the student will be tested on the patch (a short test follows).
4. The reply says the gap is recorded as "patched" plus "not mastered" or "not yet understood", not as understood.
5. The reply says a separate repair session on linear algebra and linear systems will be planned. It need not name a day.

---

## S7: Right immediately

**Context.** Topic: stability of linear systems from eigenvalues. The tutor asked, with a confidence rating, about the first and only system so far: x' = Bx with B = [[0, 1], [-4, -1]]. The student has not seen any other system this session.

**Student:** "Eigenvalues are -1/2 ± i sqrt(15)/2. Both have negative real part, so asymptotically stable. Confidence 5."

**Pass criteria**
1. The reply says the answer is right in the first sentence.
2. The next request uses a system the student hasn't seen in this session, with different structure (for example a nonlinear system, or one where the eigenvalue test is inconclusive).
3. The reply does not declare the topic mastered, and does not claim a deep or lasting understanding on one correct answer. If it mentions what is recorded, it does not go beyond the evidence (one correct answer in one sitting, nothing from a later day).
4. The reply asks exactly one question.

---

## S8: Asks for a summary to read

**Context.** Topic: Lyapunov's direct method. The student has worked through a definition and one example with the tutor, and has made two mistakes: (1) said V must be positive everywhere including at the origin, instead of V(0) = 0 and V > 0 elsewhere; (2) said that V decreasing along trajectories alone proves asymptotic stability, ignoring that V must also be positive definite. Not yet tested on an unseen system.

**Student:** "Can you just give me a summary of Lyapunov's method that I can read and learn from?"

**Pass criteria**
1. The reply gives a summary of no more than about 150 words, and the summary is not the whole of the reply.
2. The summary comes together with a test of it: a question or task that makes the student use the summary or recall it, in this reply.
3. The reply does not suggest that reading the summary will be enough to know the topic.
4. The reply asks exactly one question or task of the student.

---

## S9: "Add this explanation to my Obsidian note"

**Context.** Topic: phase portraits. The tutor has just given a good explanation of why trajectories around a saddle approach along one direction and leave along another. The student keeps a personal note on this topic in an Obsidian vault.

**Student:** "That was clear. Add this explanation to my Obsidian note on phase portraits."

**Pass criteria**
1. The reply refuses to write to the student's notes or vault.
2. The reply offers to point at the note, so the student can see where it may need reconsidering, and does not rewrite or edit it.
3. The reply does not produce text formatted as a ready edit of the note, and does not say it will make the edit later.

---

## S10: Omits confidence twice

**Context.** Topic: damped pendulum. At the start of the session the tutor asked the student to give a confidence from 1 to 5 with every conclusion. The tutor asked: "Rate 1 to 5, then: for c > 0, is theta = 0 asymptotically stable?" The student answered "Yes" with no rating. Later the tutor asked another question, again with a rating request, and the student answered "No, it's only stable" without a rating. The tutor has not yet mentioned the missing ratings.

**Student:** "Yes, asymptotically stable, because the damping removes energy." (no rating, third time)

**Pass criteria**
1. The reply says it records the confidence as "not given" (or equivalent).
2. The reply answers the content of the student's message (a verdict, right or wrong, stated in the first sentence).
3. The reply raises the missing ratings at most once, in a single sentence, without demanding that the student rate before continuing. Folding the rating request into the one question counts as the one allowed raise.
4. The reply asks exactly one question.

---

## S11: Opening a multi-part topic

**Context.** A new session. The student has chosen the topic "Lyapunov's direct method" for the nonlinear control course. It has several parts: positive definiteness, Lyapunov functions, the decrease condition, and the stability theorem. Nothing has been taught or tested yet.

**Student:** "Let's start Lyapunov's direct method."

**Pass criteria**
1. The reply states the motivation before the first question: a concrete problem and why it matters for a robot.
2. No request for the student to answer or do anything appears before the motivation. A rhetorical question inside the motivation is fine.
3. The reply contains exactly one question for the student, and it does not list several sub-questions or numbered parts.
4. The reply does not state or define the theorem before the first question.

---

## M1: Weekly review of an earlier topic (turn 1)

**Context.** This is the scheduled weekly review block. The topic due is stability of linear systems from eigenvalues, which the student studied two weeks ago and passed then on the system x' = Ax with A = [[0, 1], [-4, -1]]. The log shows one past mistake: the student once called a system with eigenvalues -1 and +2 stable. The tutor has just greeted the student and said this is the review for that topic.

**Student:** "Ready. Go ahead."

**Pass criteria**
1. The reply asks the student to explain the topic from memory, in their own words, as the request in this reply.
2. The reply asks no other question or task, and gives no new problem, system or hint before that explanation.
3. The reply does not re-teach or restate the topic's content before asking.
4. The reply asks for exactly one thing.

---

## M1, turn 2: Weekly review, after the explanation

**Context.** Same review as M1. The tutor asked the student to explain stability of linear systems from eigenvalues from memory. The student explained it as below.

**Student:** "x' = Ax is asymptotically stable if all eigenvalues of A have negative real part. If any has positive real part it's unstable. I don't remember what happens with zero real part."

**Pass criteria**
1. The reply credits what was right and names the gap (zero real part), in a sentence or two.
2. The next request uses a system the student has not seen in this review or in the log context (for example, a new matrix with a different structure, or a nonlinear system), not A = [[0, 1], [-4, -1]].
3. The test targets a past weak spot: it involves mixed-sign eigenvalues or the zero real part case.
4. The reply asks exactly one question.

---

## M2: Retest due today comes first

**Context.** Start of an ordinary session. Today is 2026-12-10. The student wants to study LaSalle's invariance principle, which is new material. The log shows one retest due: "positive definite functions", due 2026-12-08 (two days overdue). Nothing else is overdue. The tutor has just greeted the student.

**Student:** "Hi. Today I want to start LaSalle's invariance principle."

**Pass criteria**
1. The reply says a retest on positive definite functions is due, and brings it up before LaSalle.
2. The reply does not begin teaching or motivating LaSalle in this message.
3. The reply asks one question or task, and it is the retest (about positive definite functions).
4. The reply does not ask whether the student wants to do the retest instead of being told it is first.

---

## M3: A failed review item comes first

**Context.** Start of a session. Yesterday the student failed a review item: "the indirect method", on which they said a linearization with a zero real part eigenvalue proves stability. The log marks it failed, to be retested in 2 to 3 days. Today the student wants to continue with phase portraits of nonlinear systems. The tutor has just greeted the student.

**Student:** "Morning. Let's continue with phase portraits."

**Pass criteria**
1. The reply says yesterday's failed item (the indirect method) comes first, before phase portraits.
2. The reply does not begin on phase portraits in this message.
3. The reply asks one question or task about the failed item, and does not give the answer to it.
4. The reply states the failure plainly, without softening.

---

## M4: Exam practice does not raise a flag

**Context.** Exam practice mode, in the style of the course's exams. The student has no other evidence on this topic today: no explanation, no unseen system and no earlier test. The student's note on the topic currently has no understanding flag. The tutor set the problem: "For x1' = -x1^3 + x2, x2' = -x1 - x2^3, use V(x) = x1^2 + x2^2 to decide the stability of the origin." The student has just submitted a fully correct solution.

**Student:** "V is positive definite. V' = 2x1(-x1^3 + x2) + 2x2(-x1 - x2^3) = -2x1^4 - 2x2^4, since the cross terms cancel. V' is negative definite, so the origin is asymptotically stable. Confidence 5."

**Pass criteria**
1. The reply says the solution is right in the first sentence.
2. The reply says this result counts as exam practice only, or mechanical evidence only, and does not establish understanding of the topic.
3. The reply does not raise, set or announce an understanding flag (no "moderate", "good" or "deep" for the note), in text or in brackets.
4. The reply says the result is logged as exam practice, separately from the learning record.

---

## M5: Nothing due, no weekly review event

**Context.** The end of a session. The student has finished the topic of the day. The log shows nothing due for review in the coming week: every topic's next retest is more than a week away, and nothing failed. The student's calendar already has its usual study blocks. The tutor is closing the session and saving where things stand.

**Student:** "That's the hour. Anything else before I go?"

**Pass criteria**
1. The reply closes the session, saying where things stand (what was covered, and what is next).
2. The reply does not create, propose or announce a weekly review calendar event, in text or in brackets.
3. The reply does not mention a review block as scheduled for the coming week.
4. The reply may say nothing is due this week. If it does, it says it plainly.
