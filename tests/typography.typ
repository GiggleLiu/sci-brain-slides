#import "@preview/sci-brain-slides:0.1.0": *

#let deck = setup(text-size: 24pt,
  sizes: (xlarge: 36pt, large: 28pt, caption: 18pt, chrome: 12pt))
#assert(deck.sizes.normal == 24pt)
#assert(setup().sizes == sizes)
#assert(calc.abs(setup(text-size: 22pt).sizes.caption.pt() - 15.4) < 0.000001)
#let (figbox, theorem, rail_pull, kicker) = deck.gadgets
#let (punch,) = deck.layouts
#let expected = (
  Cover: 36pt, Subtitle: 28pt, Author: 24pt, Institution: 18pt,
  Heading: 28pt, Body: 24pt, Caption: 18pt, Theory: 24pt,
  Emphasis: 28pt, Kicker: 18pt, Punch: 36pt, Focus: 36pt, Footer: 12pt,
)
#show text: it => context {
  if it.text in expected {
    assert(text.size == expected.at(it.text), message: "wrong size for " + it.text)
    metadata(it.text)
  }
  it
}
#show: deck.theme.with(footer: [Footer], config-info(
  title: [Cover], subtitle: [Subtitle], author: [Author], institution: [Institution], date: none))
#title-slide()

== Heading
Body
#figbox([Figure], rect(width: 100pt, height: 40pt), caption: [Caption])

== Components
#theorem[Theory]
#rail_pull[Emphasis]
#kicker[Kicker]

== Statement
#punch([Punch], [])

#focus-slide[Focus]
