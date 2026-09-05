#!/usr/bin/env python3
"""Compile the installed template, gallery, and regression cases. No test dependencies."""
import argparse
import json
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
THEMES = ("academic", "dark", "minimal", "vibrant", "brand")


def pdf_pages(path):
    """Count page objects in a PDF emitted by Typst."""
    return len(re.findall(rb"/Type\s*/Page\b", path.read_bytes()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--typst", default="typst", help="Typst compiler executable")
    parser.add_argument("--output", type=Path, default=ROOT / "previews")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = tomllib.loads((ROOT / "typst.toml").read_text())
    package = manifest["package"]
    spec = f'@preview/{package["name"]}:{package["version"]}'

    with tempfile.TemporaryDirectory(prefix="sci-brain-slides-") as tmp:
        tmp = Path(tmp)
        packages = tmp / "packages"
        install = packages / "preview" / package["name"] / package["version"]
        # Copy only what users receive; exclude development files and previews.
        shutil.copytree(ROOT / "src", install / "src")
        shutil.copytree(ROOT / "template", install / "template")
        for name in ("lib.typ", "typst.toml", "README.md", "LICENSE"):
            shutil.copy2(ROOT / name, install / name)

        def run(*command, error=None):
            result = subprocess.run(
                [args.typst, *map(str, command), "--package-path", str(packages)],
                capture_output=True, text=True,
            )
            if error is not None:
                assert result.returncode != 0 and error in result.stderr, result.stderr
            else:
                assert result.returncode == 0, result.stderr
                if command[0] != "query":  # query is deprecated after our minimum compiler.
                    assert "warning:" not in result.stderr, result.stderr
            return result.stdout

        deck = tmp / "fresh-deck"
        run("init", spec, deck)
        entry = deck / manifest["template"]["entrypoint"]
        # Compile the README's complete example with the same installed package.
        example = re.search(r"```typst\n(.*?)\n```", (ROOT / "README.md").read_text(), re.S)
        assert example is not None, "README must include a complete Typst example"
        readme = deck / "readme.typ"
        readme.write_text(example.group(1))
        run("compile", readme, output / "readme.pdf")
        gallery = deck / "gallery.typ"
        gallery.write_text((ROOT / "gallery.typ").read_text())
        for theme in THEMES:
            starter_pdf = output / f"starter-{theme}.pdf"
            gallery_pdf = output / f"gallery-{theme}.pdf"
            run("compile", "--input", f"theme={theme}", entry, starter_pdf)
            run("compile", "--input", f"theme={theme}", gallery, gallery_pdf)
            for source, pdf, expected in ((entry, starter_pdf, 6), (gallery, gallery_pdf, 44)):
                count = pdf_pages(pdf)
                assert count == expected, f"{theme} {source.name}: expected {expected} pages, got {count}"
            print(f"PASS {theme}: initialized starter + full gallery")

        # The shorter starter must retain six pages at each supported example size.
        for size in (22, 24):
            for theme in THEMES:
                starter_pdf = output / f"starter-{theme}-{size}pt.pdf"
                run("compile", "--input", f"text-size={size}", "--input", f"theme={theme}",
                    entry, starter_pdf)
                count = pdf_pages(starter_pdf)
                assert count == 6, f"{size}pt {theme} starter spilled onto {count} pages"
        typography = deck / "typography.typ"
        shutil.copy2(ROOT / "tests/typography.typ", typography)
        run("compile", typography, output / "typography.pdf")
        observed = json.loads(run("query", typography, "metadata", "--field", "value"))
        assert set(value for value in observed if isinstance(value, str)) == {
            "Cover", "Subtitle", "Author", "Institution", "Heading", "Body", "Caption",
            "Theory", "Emphasis", "Kicker", "Punch", "Focus", "Footer",
        }
        print("PASS configurable typography; six-page starter fits at 20, 22, and 24pt")

        (deck / "user-figure.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="160" height="100">'
            '<rect width="160" height="100" fill="#7c5fdc"/>'
            '<circle cx="80" cy="50" r="24" fill="white"/></svg>'
        )
        regression = deck / "regression.typ"
        regression.write_text((ROOT / "tests/regression.typ").read_text())
        regression_pdf = output / "regression.pdf"
        run("compile", regression, regression_pdf)
        count = pdf_pages(regression_pdf)
        assert count == 10, f"regression: expected 10 pages, got {count}"
        observed = json.loads(run("query", regression, "metadata", "--field", "value"))
        values = [value for value in observed if isinstance(value, str)]
        assert values == ["Override date", "2 min", "2 min", "5 min", "2030-01-02"], values
        test = deck / "errors.typ"
        preamble = f'#import "{spec}": *\n'
        for code, message in (
            ('#let d = setup(theme: "missing")', "theme must be"),
            ('#let (conclusion_grid,) = gadgets(palettes.academic)\n#conclusion_grid(highlight: 0)', "conclusion_grid highlight must be"),
            ('#let d = setup(text-size: 0pt)', "text-size must be"),
            ('#let d = setup(text-size: 1em)', "text-size must be"),
            ('#let d = setup(sizes: (caption: -1pt))', "sizes.caption must be"),
            ('#let d = setup(sizes: (body: 24pt))', "unknown size token"),
            ('#let d = setup(primary: red)', "primary requires"),
            ('#let (portrait,) = gadgets(palettes.academic)\n#portrait("user-figure.svg", [Name])', "portrait expects content"),
            ('#let (clip_image,) = gadgets(palettes.academic)\n#clip_image("user-figure.svg")', "clip_image expects content"),
            ('#let (toc,) = gadgets(palettes.academic)\n#toc(columns: 0)', "toc columns must be"),
            ('#let (data_table,) = gadgets(palettes.academic)\n#data_table()', "data_table requires"),
            ('#let (data_table,) = gadgets(palettes.academic)\n#data_table(("A", "B"), ("one",))', "same number of cells"),
            ('#let (pacing,) = gadgets(palettes.academic)\n#pacing(-1)', "pacing minutes must be"),
        ):
            test.write_text(preamble + code)
            run("compile", test, tmp / "error.pdf", error=message)
        test.write_text(preamble + '#let (toc,) = gadgets(palettes.academic)\n#toc(columns: 4)')
        run("compile", test, tmp / "empty-outline.pdf")
        run("compile", "--format", "png", "--pages", "1", "--ppi", "160", entry, output / "cover.png")
        print("PASS custom brand, image boundary, long titles, narrow hero, sparse/empty outlines, invalid inputs")


if __name__ == "__main__":
    main()
