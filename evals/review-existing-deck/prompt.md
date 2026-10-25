---
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Skill, Bash, Read, Write, Edit, Glob, Grep]
tags: [review]
---

First run this to create my current deck: `python3 -c "from pptx import Presentation; from pptx.util import Pt; p=Presentation(); s=p.slides.add_slide(p.slide_layouts[1]); s.shapes.title.text='RESULTS'; b=s.placeholders[1].text_frame; b.text='Revenue went up a lot this year compared with last year which is great news for everybody involved'; [b.add_paragraph().__setattr__('text', t) for t in ['Costs: 1.2M','Margin: 18%','Clients: 42','Churn: 3%','NPS: 51','Headcount: 37']]; p.save('my-deck.pptx')"`

Then review my-deck.pptx and make it look professional.
