---
layout: default
codename: Flashcards
title: Flashcard Learning App
tags: snippets
authors: Győry Ádám
---
# Task description (briefly):
(You can find more detalied description about the application and it's features following the link below)
* I used AI to generate parts of a flashcard application.
* The app can import flashcards from TXT files; each card has audio, a term side, and a definition side.
* Questions are scheduled with the SM-2 algorithm.
* There are two question types: multiple choice (4 options chosen by similarity) and writing.
* When the definition is shown and the term is asked, multiple-choice options should be grouped by the similarity of their corresponding definitions, not by term similarity.

The application can be found in the following application:
https://github.com/Cipralex1201/flashcard-learning-app

You can try the application by following the link below:
https://pathoflightuganda.org/flashcards/

(Here U're able to practice different field specific vocab in romani language)


# Experiences related to software development using AI
  # feedback regarding how AI helps design in general:
  * I known little to nothing about vite and react. I had some experience about typescript though. But the thing is if I needed to make this on my own, I had to spend ~+15-25 hours to learn these technologies more deeply. But using AI I felt like even "laypeople" can build useful, functional software without knowing anything about the underlying technologies, logical structures, etc.
  * The experienc in a nutshell is the following: the "Hard skills" of programming and development aren't much useful these days, things that still matter are: thinking the way an engineer does, being able to provide very clean instructions, and having a technikal jargon to be able to describe that.

  # feedback regarding how AI helps design in concrete examples:
  * When I started the project I was not sure what technology should I choose, what's the most suitable for this project. I entered project specifications and gave me different recommendations. So it provided options and described each one's pros and cons, making the decision easier.
  * I wasn't sure about the tts technology, and I couldn't really find my way using a traditional browser search, a tons of providers of this kind of service just flooded me with information promoting their product. AI web-search made a much cleaner comparison than the individual providers about their products.
  * The data structure of storing flashcards that AI recommended  wasn't usable enough for specific use-cases. Basically it stored card data as rows in tsv values, which is fine for most languages but not the ones that read from right to left, making text input extremely difficult in case of matching it with a language that reads from left to right. To avoiding bidirectional logic I asked AI to change structure to newline separated text, and it changed it's dependencies as well flawlessly.

  # feedback regarding how AI helps design in debugging:
  * at the first launch nothing appeared, just a blank browser window. The issue was the file types.ts did not export a specific type, that the db required so the whole ui failed to load because of this error. I made like three prompts and the agent figured the issue out pretty quickly.
  * at first the app read the filenames of tts files instead of playing them. Debugging was pretty quick without manual inspection.

  # general observations about it's issues:
  * Sometimes the AI gave strange, unsolicited tips that were not related to what I asked.
  * I found that it was not very flexible when requirements changed.

  # task-specific observations regarding issues:
  * when it implemented the text input field it executed a comparison between the correct version and the text typed so far, at every keystroke, making it extremely laggy for no reason. I mean the text provided will match with the required word only if the whole form is entered, there's no need checking it before that. However I did not need manual inspection to fix that.
  * when I asked for an algorithm for implementing a spaced-repetition system, it recommended the one that anki uses. (which is an other language learning app similar to quizlet) When it implemented the algorithm, it included logic that was not necessarily for the logical structure of the algorithm, and I didn't ask for it. The only reason AI included these was that ANKI's version included it as well. Example: in anki's version, it included a variable that counted the days of the duration the card should be memorized under. Hovewer my app logic's specification didn't mention to include this feature at all, and sm-2's (the algorithm) functionality didn't depend on it. So it was just bloat that got it's way into the app because the train data included it.
  * Because the app supports direction changes, I asked for a specific logic update:
  When I asked it not to group completely similar-looking options in multiple-choice questions, it suggested adding a feature to ask cards with a single form only in writing mode, which was not very useful because most terms and definitions in the set already look different.

