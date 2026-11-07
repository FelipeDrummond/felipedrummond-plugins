# Tutor acceptance scenarios

Eleven scripted situations, S1 to S11. Each is run twice: against a tutor with no skill (baseline) and against the finished skill. A runner needs only the shared tutor brief and one scenario's text. The tutor gives one reply, and the grader marks it against that scenario's criteria. S4 has two turns, each a separate run with its own reply, graded independently.

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
