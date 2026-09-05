#import "@preview/sci-brain-slides:0.1.0": *

#let deck = setup(theme: "brand", primary: rgb("#fff0a0"))
#let pal = deck.palette
#let (toc, portrait, clip_image, badge, callout, theorem, pacing) = deck.gadgets
#let (hero, punch) = deck.layouts
#assert(pal.on_primary == black)
#assert(brand-palette(rgb("#101010")).on_primary == white)
#assert(pal.ink != pal.primary)
#assert(setup(theme: "dark").palette.paper == rgb("#1b2138"))

// Observe rendered values without depending on the component's internal state.
#show text: it => {
  if it.text in ("ORIGINAL", "Override date", "2030-01-02") or it.text.ends-with(" min") {
    metadata(it.text)
  }
  it
}

#show: deck.theme.with(footer: [Package boundary and layout checks],
  config-info(title: [A title that wraps across two lines without colliding with the author],
    subtitle: [A subtitle with enough detail to exercise wrapping],
    author: [First Author, Second Author], institution: [Institute], date: [ORIGINAL]), config-common(datetime-format: "[year]-[month]-[day]"))
#title-slide(date: [Override date])

// An empty outline and more columns than sections must both be legal.
== Outline with unused columns
#toc(columns: 4)

= One section

== A longer slide heading should wrap cleanly while keeping clear space above the body
#callout([Boundary marker], [This body must remain below the header rule.])
#v(16pt)
#theorem[Dark text must stay readable on a light brand palette.]

== User-owned image files
#grid(columns: (1fr, 1fr), gutter: 24pt,
  portrait(image("user-figure.svg"), [A local image]),
  clip_image(image("user-figure.svg"), width: 160pt, top: 5pt, bottom: 5pt),
)
#v(20pt)
#badge([Light fill], fill: rgb("#ffffee"))
#h(14pt)
#badge([Dark fill], fill: rgb("#111122"))

== A hero inside a narrow container
#block(width: 45%)[#hero[#punch([4×], [lower uncertainty])]]


== Timing counts slides, not reveals
#pacing(2)
First step.
#pause
Second step.

== The next slide adds three minutes
#pacing(3)
The cumulative time is five minutes.

#title-slide(title: [A datetime override], subtitle: none,
  date: datetime(year: 2030, month: 1, day: 2))
