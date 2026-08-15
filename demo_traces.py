#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline demo traces for the Idun Expo showcase.

These are *recorded* (hand-authored, fictional) agent trajectories for the
Contoso demo prompts. They let the playground render a full trace + answer
even when no Foundry token is available (e.g. at a booth, or after the token
expired), instead of showing a bare HTTP 500 / "no answer received".

IMPORTANT: these are clearly labelled DEMO REPLAYS in the UI. They are NOT
live agent output. When a valid FOUNDRY_TOKEN is present the router runs the
real agent; the demo traces are only a fallback / deterministic booth replay.

Shape matches router._step_to_dict() so the same streaming + TraceViz path is
used for both live and demo runs:
    step = {"kind", "text", "tool", "query", "status", "id"}
    trace = {"model": <str>, "steps": [step...], "answer": <str>}
"""

# Keyed by (pack, key) so expo.html can request a deterministic replay.
DEMO_TRACES = {
    ("contoso", "sustainability_summary"): {
        "model": "demo-replay",
        "steps": [
            {
                "kind": "reasoning",
                "text": "Ich strukturiere die Antwort: zuerst das Kreislauf-Prinzip im Geschäftsmodell, dann drei konkrete, nachprüfbare Beispiele aus den öffentlichen Contoso-Materialien.",
                "tool": "", "query": "", "status": "", "id": "r1",
            },
            {
                "kind": "tool", "tool": "web_search",
                "query": "Contoso circular economy business model",
                "status": "completed", "id": "t1", "text": "",
            },
            {
                "kind": "tool", "tool": "web_search",
                "query": "Contoso sustainability report 2026 circularity",
                "status": "completed", "id": "t2", "text": "",
            },
            {
                "kind": "reasoning",
                "text": "Die Quellen zeigen drei wiederkehrende Hebel: Produkt-als-Service, Recyclat-Einsatz und ein Rücknahmesystem. Ich fasse das als Beispiele.",
                "tool": "", "query": "", "status": "", "id": "r2",
            },
        ],
        "answer": (
            "Contoso verankert Kreislaufwirtschaft an drei Stellen im Geschäftsmodell:\n\n"
            "1) Produkt-als-Service: Contosos Drucker- und Batteriesysteme werden "
            "im Pay-per-Use-Modell vermietet, nicht verkauft — Eigentum und Rückbau "
            "bleiben beim Hersteller.\n\n"
            "2) Recyclat-Einsatz: Seit 2026 bestehen Gehäuseteile zu 62 % aus "
            "zertifiziertem Post-Consumer-Recyclat; das Ziel für 2028 liegt bei 80 %.\n\n"
            "3) Rücknahmesystem: Über 4.200 Sammelpunkte nehmen Altgeräte zurück; "
            "ausgelesene Module werden wieder in die Produktion eingespeist.\n\n"
            "Fazit: Kreislauf ist bei Contoso nicht nur PR, sondern Teil des "
            "Umsatzmodells (Service-Verträge) und der Beschaffung (Recyclat-Quote)."
        ),
    },
    ("contoso", "esg_check"): {
        "model": "demo-replay",
        "steps": [
            {
                "kind": "reasoning",
                "text": "Ich prüfe die drei genannten Dimensionen nacheinander und markiere Lücken statt nur Lob.",
                "tool": "", "query": "", "status": "", "id": "r1",
            },
            {
                "kind": "tool", "tool": "web_search",
                "query": "Contoso ESG disclosures emissions scope 1 2 3",
                "status": "completed", "id": "t1", "text": "",
            },
            {
                "kind": "tool", "tool": "web_search",
                "query": "Contoso supply chain audit governance code",
                "status": "completed", "id": "t2", "text": "",
            },
            {
                "kind": "reasoning",
                "text": "Emissions- und Governance-Daten sind vorhanden; die Lieferketten-Audit-Tiefe ist die sichtbarste Lücke.",
                "tool": "", "query": "", "status": "", "id": "r2",
            },
        ],
        "answer": (
            "ESG-Check Contoso (basierend auf veröffentlichten Angaben):\n\n"
            "Emissionen — GUT: Scope 1/2 werden quartalsweise berichtet, SBTi-Ziel "
            "ist eingetragen. LÜCKE: Scope-3-Kategorien 4–11 sind nur teilweise "
            "abgedeckt, Unterlieferanten fehlen fast ganz.\n\n"
            "Lieferkette — LÜCKE: Erststufen-Lieferanten sind auditiert, aber die "
            "tiefere Tier-2/3-Stufe hat keine veröffentlichte Ausfallquote oder "
            "korrigierende Maßnahmen.\n\n"
            "Governance — GUT: ESG-KPIs sind an Vorstands-Vergütung gekoppelt; "
            "Bericht folgt CSRD-Struktur.\n\n"
            "Wichtigste Lücke: Scope-3-Tiefe und Lieferketten-Transparenz jenseits "
            "der Tier-1-Ebene."
        ),
    },
    ("contoso", "web_research"): {
        "model": "demo-replay",
        "steps": [
            {
                "kind": "reasoning",
                "text": "Ich suche aktuelle Nachrichten und trenne positive von kritischen Quellen.",
                "tool": "", "query": "", "status": "", "id": "r1",
            },
            {
                "kind": "tool", "tool": "web_search",
                "query": "Contoso news sustainability 2026 positive",
                "status": "completed", "id": "t1", "text": "",
            },
            {
                "kind": "tool", "tool": "web_search",
                "query": "Contoso criticism recycling claims greenwashing",
                "status": "completed", "id": "t2", "text": "",
            },
            {
                "kind": "reasoning",
                "text": "Berichtet wird positiv über Recyclat-Quote und Service-Modell, kritisch über die Scope-3-Lücke.",
                "tool": "", "query": "", "status": "", "id": "r2",
            },
        ],
        "answer": (
            "Aktuelle Contoso-Berichterstattung zur Nachhaltigkeit:\n\n"
            "Positiv:\n"
            "• TechReview hebt das Pay-per-Use-Modell als „konsequentesten "
            "Circular-Ansatz der Branche” hervor.\n"
            "• Eine Industrie-Studie zitiert Contosos 62 %-Recyclat-Quote als "
            "Benchmark.\n\n"
            "Kritisch:\n"
            "• GreenWatch hinterfragt, ob die Scope-3-Bilanz die Tier-2/3-Zulieferer "
            "vollständig einschließt (Greenwashing-Risiko).\n"
            "• Eine NGO fordert detailliertere Lieferketten-Audit-Daten.\n\n"
            "Bild: Contoso gilt als Vorreiter in Produktdesign, steht aber unter "
            "Druck bei Mess-Tiefe und Transparenz."
        ),
    },
    ("contoso", "competitor_compare"): {
        "model": "demo-replay",
        "steps": [
            {
                "kind": "reasoning",
                "text": "Ich vergleiche Contoso mit einem realen Wettbewerber entlang Kreislauf-Kriterien.",
                "tool": "", "query": "", "status": "", "id": "r1",
            },
            {
                "kind": "tool", "tool": "web_search",
                "query": "competitor circular economy recyclate rate service model",
                "status": "completed", "id": "t1", "text": "",
            },
            {
                "kind": "tool", "tool": "web_search",
                "query": "Contoso vs competitor lifecycle takeback comparison",
                "status": "completed", "id": "t2", "text": "",
            },
            {
                "kind": "reasoning",
                "text": "Contoso führt bei Service-Modell und Recyclat-Quote, hinkt bei Offenlegung der Tier-2/3-Kette hinterher.",
                "tool": "", "query": "", "status": "", "id": "r2",
            },
        ],
        "answer": (
            "Contoso vs. ein realer Wettbewerber (Kreislaufwirtschaft):\n\n"
            "Contoso führend in:\n"
            "• Produkt-als-Service-Umsatzanteil (geschätzt >30 % vs. ~12 %).\n"
            "• Recyclat-Quote in Gehäusen (62 % vs. ~40 %).\n\n"
            "Wettbewerber führend in:\n"
            "• Öffentlicher Lieferketten-Tiefe (Tier-2/3-Audit-Daten sind "
            "veröffentlicht, Contoso nur andeutungsweise).\n"
            "• Dritter verifizierter Scope-3-Report (Contoso in Arbeit).\n\n"
            "Fazit: Contoso gewinnt beim Geschäftsmodell, verliert bei der "
            "Mess-Transparenz — genau dort sollte die nächste ESG-Arbeit ansetzen."
        ),
    },
}


# Used as a generic fallback when no token is present and no matching key was
# supplied (e.g. free-form prompt in the Playground).
GENERIC_DEMO = {
    "model": "demo-replay",
    "steps": [
        {
            "kind": "reasoning",
            "text": "Hinweis: Es ist kein Live-Foundry-Token konfiguriert. Ich zeige einen Demo-Replay-Trace, damit die Bühne nicht leer bleibt.",
            "tool": "", "query": "", "status": "", "id": "r1",
        },
        {
            "kind": "tool", "tool": "web_search",
            "query": "demo replay (no live token)",
            "status": "completed", "id": "t1", "text": "",
        },
        {
            "kind": "reasoning",
            "text": "Demo-Antwort wird aus einem aufgezeichneten Trace gerendert.",
            "tool": "", "query": "", "status": "", "id": "r2",
        },
    ],
    "answer": (
        "Demo-Replay (kein Live-Token). Dies ist eine aufgezeichnete Antwort aus "
        "einem Contoso-Beispiel-Trace, nicht die Ausgabe des Live-Agenten.\n\n"
        "Für echte Live-Ergebnisse `idun login` ausführen (gültigen "
        "FOUNDRY_TOKEN setzen) und die Demo erneut starten. Der Trace-Ablauf, "
        "das Rendering und die UI sind identisch zum Live-Pfad."
    ),
}


def get_demo(pack: str, key: str):
    """Return the demo trace dict for (pack, key), or None if unknown."""
    return DEMO_TRACES.get((pack, key))


def first_demo_key():
    """(pack, key) of the first recorded trace — used as generic fallback."""
    for (pack, key) in DEMO_TRACES:
        return (pack, key)
    return (None, None)
