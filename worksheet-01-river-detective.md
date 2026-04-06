# Lesson 2 — Reading the Data, Taking Action

**Subject**: Science / English / PSHE  
**Year group**: Years 3–6 (ages 7–11)  
**Duration**: 60–75 minutes  
**Prior knowledge needed**: Lesson 1 (or familiarity with pH, nitrates, phosphates)

---

## Learning objectives

By the end of this lesson, pupils will be able to:

- Interpret a set of river water-quality readings and form a conclusion
- Use an AI assistant to generate and then critically evaluate explanations
- Choose one action to take in response to what the data shows
- Produce a piece of writing (poster text, letter, or assembly speech) addressed to a real audience

---

## Resources needed

| Resource | Notes |
|---|---|
| `worksheet-02-write-to-a-decision-maker.md` (printed) | One per pupil |
| `data/sample-readings.csv` | Displayed on screen |
| `prompts/prompt-templates.md` | For teacher reference |
| Access to an AI assistant | Local Ollama or similar |
| Writing materials or devices | For the action output |

---

## Lesson outline

### Starter — Recap and reveal (10 min)

Return to the question each pair wrote at the end of Lesson 1.

Read three or four questions aloud. Then say:

> "Today we are going to do what real river scientists do. We are going to look at the data, decide what it means, and then do something about it."

Reveal this session's scenario — present it as a real briefing:

---

**📋 River Ranger Briefing**

*Your local river has been monitored at three sites over the past year. The data is in. Some of it is worrying. The people who manage the river need to hear from the community — especially from young people who will live with the consequences longest.*

*Your job today: understand the data, use your AI assistant to help explain it, and produce one piece of communication that could make a difference.*

---

### Main activity 1 — Interpreting the data (15 min)

Show the full year of sample data from `sample-readings.csv` on the whiteboard.

In pairs, pupils answer three questions on **Worksheet 2**:

1. Which site is most at risk? Highlight the readings that concern you most.
2. What trend do you notice between March and September?
3. What do you think is causing the problem at Site C?

After 10 minutes, take responses. Note on the board: **causes** (farming, sewage, urban run-off) and **effects** (loss of invertebrates, algae, reduced oxygen).

---

### Main activity 2 — Ask the AI assistant (20 min)

Introduce the prompt-building process. Explain that the quality of our question shapes the quality of the answer — just like in science.

**Model a weak prompt and a strong prompt:**

| Weak | Strong |
|---|---|
| "What is wrong with the river?" | "We found nitrates of 24 mg/L and phosphates of 0.68 mg/L at a river site downstream from farmland. What are the likely causes and what might this mean for fish and invertebrates? Please explain for a 9-year-old." |

Pupils use **Prompt Template 2** from `prompts/prompt-templates.md` to craft their own question and submit it to the AI assistant (as a class, in groups, or individually depending on device access).

They record:
- The question they asked
- The AI's answer (summarised in their own words)
- One thing the AI said that surprised them
- One thing they are not sure is correct (and how they might check it)

The final point is critical — treat it as a class discussion moment. What sources could verify the AI's claims? (River monitoring organisations, school science textbooks, the Environment Agency website.)

---

### Main activity 3 — Take action (20 min)

Pupils choose one output from three options and begin drafting on **Worksheet 2**:

**Option A — Poster for the school entrance**  
Audience: other pupils and their families  
Message: what's happening to your local river and why it matters  
Format: headline + three key facts + one call to action  

**Option B — Letter to a decision-maker**  
Audience: local councillor, MP, water company, or farm owner  
Message: the data, what it means, and one specific ask  
Format: formal letter structure (greeting, evidence, request, sign-off)  

**Option C — Two-minute assembly speech**  
Audience: the whole school  
Message: river health as a community responsibility  
Format: hook, three points, memorable ending

Encourage pupils to use the AI assistant to:
- Help them find the right words for a difficult concept
- Check their letter sounds polite but firm
- Suggest one more fact they could include

But the ideas, the argument, and the action must be theirs.

---

### Plenary — Share and commit (5–10 min)

Pairs share one sentence from their draft with the class.

Ask: "If we actually sent these — who would read them? What might happen?"

If there is a real local river group partner, discuss: could any of these pieces of work genuinely be shared with them, or with a local paper or councillor?

Close with:

> "You are River AI Rangers. You used real data, you used an AI tool responsibly, and you made something that could make a real difference. That is exactly what scientists and citizens do."

---

## Differentiation

**Support**: Pre-fill the data summary on Worksheet 2 (site names and worst readings already highlighted). Provide sentence starters for the action output.

**Extension**: Pupils research the actual water quality standards set by the EU Water Framework Directive or Defra and compare them to the sample data. Do our readings breach legal limits?

**EAL**: Provide a bilingual glossary. Allow the AI assistant to translate the pupil's drafted text into a second language as an extension.

---

## Assessment opportunities

- Worksheet 2 data interpretation: can the pupil draw an evidence-based conclusion?
- AI interaction record: does the pupil evaluate the AI's response critically?
- Action output: is it addressed to a real audience, with evidence, and a clear ask?

---

## Cross-curricular links

| Subject | Link |
|---|---|
| English | Persuasive writing, audience and purpose, formal letter structure |
| Science | Working scientifically, data interpretation, habitats |
| PSHE | Environmental responsibility, community action, citizenship |
| Geography | River systems, land use, water cycle |
| Computing | Understanding AI tools, data literacy |

---

## Extending the project

This two-lesson sequence is designed as a foundation. Schools that want to go further can:

- Set up a termly river monitoring visit with a local group
- Publish pupil letters to the school website or local paper
- Enter data into a shared open dataset (contact us to join the River AI Rangers network)
- Use the AI assistant to track changes in the data over time and write a year-end report

---

## Teacher notes

### If pupils ask "Is the AI alive?"

This comes up. A useful framing for primary age:

> "The AI has read millions of pages about rivers, science, and nature. It uses all of that to predict what a helpful answer looks like. It is not alive, it does not understand the river the way you do — but it can be a very fast and useful research assistant, as long as we keep checking its work."

### On data privacy

Because this toolkit uses a locally-run model (Ollama), nothing pupils type is sent to any company. This is worth explaining to pupils — and to parents — as an early lesson in understanding how AI systems handle data.
