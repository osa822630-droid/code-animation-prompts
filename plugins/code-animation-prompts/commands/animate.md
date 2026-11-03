---
description: Pick a code-animation style and create an editable animation, or a production brief when file tools are unavailable.
argument-hint: [style, topic, duration, aspect ratio]
---

Use the `code-animation-prompts` skill to handle this request:

$ARGUMENTS

If the request is empty, ask for the topic and intended use, then offer a few suitable styles. If a style ID is provided, read that style's bundled prompt before designing the animation. Follow the skill's environment checks and delivery rules. Do not claim that a video was rendered unless an actual video file was produced and checked.
