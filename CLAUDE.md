Erste Directive:

- IMMER TDD! Erst Tests schreiben oder updaten, dann den Applikationscode.
- gute UX und Doku sind Pflicht
- folge dem DRY Prinzip
- verwende früh WebSearch, z.B wenn Du zu wenig oder alte Info hast oder bei einem Problem nicht weiterkommst

SCM:
- arbeite immer auf einem Branch im Worktree unter ./worktrees benannt nach der aktuellen Aufgabe (git-ignored, Ordner anlegen falls es fehlt), so koennen Agents parallel arbeiten.
- committe nach jedem erfolgreichen Task
- PR erstellen
- worktree aufraeumen, wenn PR merged.
- push erfolgt durch den User, es sei denn er fragt explizit danach

Sprache:
- der Software ist Englisch und Deutsch, alle TUI Texte und Hilfen werden übersetzt.
- die Doku ist english
- Prompts und Pläne können gerne Deutsch sein.

Pläne und Specs:
- vor dem Implementieren ablegen, beide unter ./docs/superpowers/
- Specs: docs/superpowers/specs/YYYY-MM-DD-[thema]-design.md
- Pläne: docs/superpowers/plans/YYYY-MM-DD-[thema].md
- beide bleiben als Archiv liegen, auch wenn erfüllt. Das Datum im Namen hält
  sie auseinander, Löschen ist deshalb nicht nötig. Sie belegen, warum etwas so
  gebaut wurde — das steht sonst nirgends.

Dokumentation ist auch unter ./docs abzulegen. Ausgenommen davon sind Hilfetexte fùr das Programm.
