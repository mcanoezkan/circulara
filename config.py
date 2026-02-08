# config.py - Leitfragen v6 Modell (Circular Readiness Assessment)
# Vollständig abgebildet als Multiple Choice mit Erklärungen aus dem PDF

DEFAULT_WEIGHTS = {
    "Design": 0.35,
    "Strategie": 0.20,
    "Wirtschaftlichkeit": 0.15,
    "Regulatorik": 0.15,
    "Systemische Befähiger": 0.15,
}

MATURITY_LEVELS = [
    {
        "min_score": 0.0,
        "max_score": 0.2,
        "name": "Sehr gering",
        "emoji": "🔴",
        "description": "Die Zirkularitätsreife ist aktuell sehr gering.",
    },
    {
        "min_score": 0.2,
        "max_score": 0.4,
        "name": "Gering",
        "emoji": "🟠",
        "description": "Ansätze sind erkennbar, es bestehen umfangreiche Potenziale.",
    },
    {
        "min_score": 0.4,
        "max_score": 0.6,
        "name": "Mittel",
        "emoji": "🟡",
        "description": "Zirkuläre Ansätze sind entwickelt, aber noch nicht konsequent umgesetzt.",
    },
    {
        "min_score": 0.6,
        "max_score": 0.8,
        "name": "Fortgeschritten",
        "emoji": "🟢",
        "description": "Das Produkt ist in vielen Bereichen gut auf Zirkularität vorbereitet.",
    },
    {
        "min_score": 0.8,
        "max_score": 1.01,
        "name": "Sehr hoch",
        "emoji": "🟣",
        "description": "Das Produkt weist eine sehr hohe Circular Readiness auf.",
    },
]

QUESTION_TYPES = ["mc"]

CIRCULAR_MODEL = {
    "Design": {
        "1.1 Operative Demontierbarkeit": {
            "description": "Bewertet die physische Eignung des Produkts für technische Kreisläufe und Werterhalt durch zerstörungsfreie Demontage.",
            "questions": [
                {
                    "code": "1.1.1",
                    "text": "Zerstörungsfreie Demontage: Können Module und Komponenten zerstörungsfrei demontiert werden?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Das Produkt ist untrennbar verklebt oder verschweißt; eine Demontage führt zwangsläufig zur Zerstörung.",
                            "score": 0.0,
                        },
                        {
                            "label": "Module sind teilweise durch irreversible Verbindungen (z. B. Nieten) verbunden, die nur mit erheblichem Aufwand oder Spezialgerät lösbar sind.",
                            "score": 0.5,
                        },
                        {
                            "label": "Sämtliche Module und Komponenten können einfach und vollkommen zerstörungsfrei demontiert werden.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "1.1.2",
                    "text": "Benötigte Werkzeuge: Welche Werkzeuge werden für die Kernkomponenten benötigt?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Die Demontage erfordert den Einsatz schwerer, stationärer Industriemaschinen.",
                            "score": 0.0,
                        },
                        {
                            "label": "Für den Zugriff auf Kernkomponenten ist herstellerspezifisches Spezialwerkzeug zwingend erforderlich.",
                            "score": 0.3,
                        },
                        {
                            "label": "Das Produkt kann mit gewöhnlichem Standardwerkzeug (z. B. Schraubendreher) zerlegt werden.",
                            "score": 0.7,
                        },
                        {
                            "label": "Das Design ermöglicht eine werkzeuglose Demontage allein mit den Händen.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "1.1.3",
                    "text": "Zeitaufwand: Wie hoch ist der Zeitaufwand für den Zugriff auf die wertvollste Kernkomponente (z. B. Motor, PCB)?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Die Demontage dauert länger als 60 Minuten und ist für Aufbereitungszwecke völlig unwirtschaftlich.",
                            "score": 0.0,
                        },
                        {
                            "label": "Der Zugriff auf die Kernkomponente erfordert einen sehr hohen Zeitaufwand zwischen 30 und 60 Minuten.",
                            "score": 0.25,
                        },
                        {
                            "label": "Die Demontage ist moderat komplex und dauert zwischen 10 und 30 Minuten.",
                            "score": 0.5,
                        },
                        {
                            "label": "Die Komponente ist in einem schnellen Prozess von 5 bis 10 Minuten zugänglich.",
                            "score": 0.75,
                        },
                        {
                            "label": "Der Zugriff auf die wertvollste Komponente erfolgt in weniger als 5 Minuten.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "1.2 Modularität & Upgrade-Fähigkeit": {
            "description": "Bewertet die Möglichkeit, einzelne Module auszutauschen und das Produkt mit neuen Komponenten zu upgraden.",
            "questions": [
                {
                    "code": "1.2.1",
                    "text": "Modul-Entnehmbarkeit: Sind defekte oder veraltete Module einzeln entnehmbar, ohne das Gesamtsystem zu schwächen?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Das System ist monolithisch aufgebaut; einzelne Module können nicht entnommen werden.",
                            "score": 0.0,
                        },
                        {
                            "label": "Ein Austausch ist eingeschränkt möglich, erfordert jedoch tiefe Eingriffe in die Systemstruktur.",
                            "score": 0.5,
                        },
                        {
                            "label": "Das Produkt ist voll modular; defekte oder veraltete Module lassen sich wie Bausteine entnehmen.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "1.2.2",
                    "text": "Architektur-Upgrade: Erlaubt die Architektur den Austausch von Modulen gegen leistungsfähigere Komponenten?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Die Architektur ist starr; ein Austausch gegen leistungsfähigere Komponenten ist technisch ausgeschlossen.",
                            "score": 0.0,
                        },
                        {
                            "label": "Upgrades sind nur für sehr spezifische Komponenten unter hohem Aufwand möglich.",
                            "score": 0.5,
                        },
                        {
                            "label": "Die Architektur erlaubt den flexiblen Austausch von Modulen gegen modernere Versionen.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "1.2.3",
                    "text": "Schnittstellen für Erweiterungen: Sind physische oder digitale Schnittstellen für zukünftige Upgrades vorhanden?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es sind keine physische oder digitale Schnittstellen für zukünftige Upgrades vorhanden.",
                            "score": 0.0,
                        },
                        {
                            "label": "Schnittstellen für Erweiterungen befinden sich aktuell in der Konzeptionsphase oder Planung.",
                            "score": 0.5,
                        },
                        {
                            "label": "Schnittstellen sind bereits standardmäßig integriert und für zukünftige Funktionserweiterungen bereit.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "1.3 Materialprofil & Verschleiß": {
            "description": "Bewertet die Materialzusammensetzung, Restfestigkeit und Oberflächenpflege.",
            "questions": [
                {
                    "code": "1.3.1",
                    "text": "Anteil recycelter Materialien: Wie hoch ist der Anteil an recycelten/wiederverwendeten Materialien (nach Kosten)?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es werden ausschließlich Primärrohstoffe verwendet (0% Recyclinganteil).",
                            "score": 0.0,
                        },
                        {
                            "label": "Der Anteil an Sekundärmaterialien liegt bei 1% bis 19%.",
                            "score": 0.25,
                        },
                        {
                            "label": "Es werden zwischen 20% und 39% recycelte Materialien eingesetzt.",
                            "score": 0.5,
                        },
                        {
                            "label": "Der Anteil an Sekundärmaterialien liegt bei 40% bis 69%.",
                            "score": 0.75,
                        },
                        {
                            "label": "Das Produkt besteht fast vollständig (70% bis 100%) aus recycelten Stoffen.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "1.3.2",
                    "text": "Restfestigkeit für 2. Zyklus: Weisen die tragenden Strukturen nach der Erstnutzung eine ausreichende Restfestigkeit für einen zweiten Zyklus auf?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es liegt deutliche Materialermüdung vor; tragende Strukturen sind nach der Erstnutzung brüchig.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es ist sichtbare Abnutzung vorhanden, die Strukturen bleiben jedoch stabil und belastbar.",
                            "score": 0.5,
                        },
                        {
                            "label": "Die Strukturen weisen eine Restfestigkeit auf, die nahezu dem Neuzustand entspricht.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "1.3.3",
                    "text": "Oberflächenauffrischung: Wie einfach lassen sich Oberflächen reinigen oder optisch auffrischen?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Eine optische Auffrischung ist unmöglich oder völlig unwirtschaftlich.",
                            "score": 0.0,
                        },
                        {
                            "label": "Die Oberflächen lassen sich mit moderatem Aufwand reinigen oder aufarbeiten.",
                            "score": 0.5,
                        },
                        {
                            "label": "Oberflächen sind so gestaltet, dass sie sehr einfach in einen neuwertigen Zustand versetzt werden können.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "1.3.4",
                    "text": "Kritische Materialien: Enthält das Produkt kritische Materialien (seltene Erden) oder Konfliktmineralien?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Das Produkt enthält hohe Mengen an Konfliktmineralien oder seltenen Erden.",
                            "score": 0.0,
                        },
                        {
                            "label": "Kritische Materialien sind nur in geringen Mengen im Produkt vorhanden.",
                            "score": 0.5,
                        },
                        {
                            "label": "Das Produkt ist vollkommen frei von kritischen Materialien oder Konfliktmineralien.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "1.3.5",
                    "text": "Reine Materialfraktionen: Enthält das Produkt leicht identifizierbare, reine Materialfraktionen ohne störende Beschichtungen?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es werden unbekannte Verbundstoffe verwendet, die nicht getrennt werden können.",
                            "score": 0.0,
                        },
                        {
                            "label": "Die Materialien liegen in vermischter Form vor, was das Recycling ausgedienter Bauteile erschwert.",
                            "score": 0.5,
                        },
                        {
                            "label": "Es liegen sortenreine, klar gekennzeichnete Materialfraktionen ohne störende Beschichtungen vor.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "1.3.6",
                    "text": "Schadstoff-Isolierung: Sind Schadstoffe (SVHC) so verbaut, dass sie bei der Zerlegung sicher isoliert werden können?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es besteht die Gefahr der Kontamination, da Schadstoffe fest verbaut sind.",
                            "score": 0.0,
                        },
                        {
                            "label": "Die Isolierung von Schadstoffen erfordert Sonderprozesse oder persönliche Schutzausrüstung (PSA).",
                            "score": 0.5,
                        },
                        {
                            "label": "Schadstoffe sind so verbaut, dass sie bei der Zerlegung sicher und einfach isoliert werden können.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "1.4 Standardisierung": {
            "description": "Bewertet die Verwendung von Normteilen und Rückwärtskompatibilität.",
            "questions": [
                {
                    "code": "1.4.1",
                    "text": "Anteil an Normteilen: Wie hoch ist der Anteil an herstellerübergreifenden Normteilen?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es werden ausschließlich herstellerspezifische Sonderanfertigungen verwendet.",
                            "score": 0.0,
                        },
                        {
                            "label": "Der Anteil an herstellerübergreifenden Normteilen ist sehr gering.",
                            "score": 0.25,
                        },
                        {
                            "label": "Es wird ein mittlerer Anteil an Normteilen eingesetzt.",
                            "score": 0.5,
                        },
                        {
                            "label": "Ein Großteil der Komponenten besteht aus standardisierten Normteilen.",
                            "score": 0.75,
                        },
                        {
                            "label": "Es werden überwiegend (> 80%) herstellerübergreifende Normteile verwendet.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "1.4.2",
                    "text": "Rückwärtskompatibilität: Besteht eine Rückwärtskompatibilität von Ersatzteilen über Generationen hinweg?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es besteht keinerlei Kompatibilität zwischen verschiedenen Produktgenerationen.",
                            "score": 0.0,
                        },
                        {
                            "label": "Die Kompatibilität von Ersatzteilen ist nur für ausgewählte Modellreihen gegeben.",
                            "score": 0.5,
                        },
                        {
                            "label": "Ersatzteile weisen eine vollständige Rückwärtskompatibilität über Generationen hinweg auf.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "1.5 Emotionale Haltbarkeit": {
            "description": "Bewertet die Fähigkeit des Designs, langfristige Nutzerbindung zu fördern.",
            "questions": [
                {
                    "code": "1.5.1",
                    "text": "Langfristige Bindung: Fördert das Design eine langfristige Bindung (z. B. durch zeitlose Ästhetik oder Personalisierung)?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Das Design folgt kurzlebigen Trends und veraltet optisch sehr schnell.",
                            "score": 0.0,
                        },
                        {
                            "label": "Das Design fördert teilweise eine Bindung, ist aber nicht durchgängig zeitlos.",
                            "score": 0.5,
                        },
                        {
                            "label": "Das Design fördert durch zeitlose Ästhetik oder Personalisierung eine langfristige Nutzerbindung.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
    },
    "Strategie": {
        "2.1 Marktfähigkeit und Verfügbarkeit": {
            "description": "Bewertet den Sekundärmarkt und die Verfügbarkeit von Ersatzteilen.",
            "questions": [
                {
                    "code": "2.1.1",
                    "text": "Aktiver Sekundärmarkt: Existiert für das spezifische Produkt-Modell ein aktiver Sekundärmarkt?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es existiert kein relevanter Sekundärmarkt für das Produkt; Altgeräte werden fast ausschließlich entsorgt.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es gibt einen informellen Gebrauchtmarkt (z. B. Privatverkäufe), aber keine professionelle Nachfrage.",
                            "score": 0.25,
                        },
                        {
                            "label": "Ein moderater Sekundärmarkt ist vorhanden, jedoch liegen die Wiederverkaufspreise weit unter dem Potenzial.",
                            "score": 0.5,
                        },
                        {
                            "label": "Es besteht eine stabile professionelle Nachfrage nach Gebrauchtgeräten durch spezialisierte Händler.",
                            "score": 0.75,
                        },
                        {
                            "label": "Es existiert eine hohe Nachfrage mit Wiederverkaufspreisen von über 50% des Neupreises.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "2.1.2",
                    "text": "Ersatzteilverfügbarkeit: Sind kritische Ersatzteile für dieses Produkt-Modell am Markt verfügbar?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Kritische Ersatzteile sind am freien Markt nicht lieferbar oder werden vom Hersteller zurückgehalten.",
                            "score": 0.0,
                        },
                        {
                            "label": "Ersatzteile sind nur sporadisch oder über Umwege mit extrem langen Wartezeiten beziehbar.",
                            "score": 0.3,
                        },
                        {
                            "label": "Die meisten Ersatzteile sind mit moderaten Wartezeiten über offizielle Kanäle verfügbar.",
                            "score": 0.7,
                        },
                        {
                            "label": "Alle kritischen Ersatzteile sind sofort ab Lager verfügbar, was eine schnelle Instandsetzung ermöglicht.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "2.2 Ressourcen & Know-how": {
            "description": "Bewertet die verfügbaren finanziellen und personellen Ressourcen für zirkuläres Design.",
            "questions": [
                {
                    "code": "2.2.1",
                    "text": "Projektbudget: Ist ein dediziertes Budget für Aufbereitungsprojekte vorhanden?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es ist kein zusätzliches Budget für Aufbereitungsprojekte vorgesehen.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es werden ad-hoc finanzielle Mittel für einzelne Pilotprojekte bereitgestellt, jedoch ohne feste Planung.",
                            "score": 0.3,
                        },
                        {
                            "label": "Ein Budget für Aufbereitung ist vorhanden und bereits in der Finanzplanung initiiert.",
                            "score": 0.7,
                        },
                        {
                            "label": "Ein dediziertes Budget ist fest zugewiesen und dauerhaft integriert.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "2.2.2",
                    "text": "Demontage-Know-how des Personals: Verfügt das Personal über spezifisches Demontage-Know-how?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Das Personal verfügt über keine spezifischen Kenntnisse oder Fähigkeiten in Bezug auf die Produktdemontage.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es ist lediglich theoretisches Grundwissen vorhanden, die praktische Umsetzung scheitert an fehlender Übung.",
                            "score": 0.25,
                        },
                        {
                            "label": "Das Personal verfügt über Basiskenntnisse und kann einfache Demontageschritte durchführen.",
                            "score": 0.5,
                        },
                        {
                            "label": "Die Mitarbeitenden sind fortgeschritten geschult und können komplexe Baugruppen sicher zerlegen.",
                            "score": 0.75,
                        },
                        {
                            "label": "Das Personal besitzt Expertenstatus; Demontageprozesse sind hochgradig standardisiert und effizient.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "2.2.3",
                    "text": "Diagnose-Tools und Reparaturanleitungen: Verfügt das Personal über die notwendigen Diagnose-Tools und Reparaturanleitungen?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es existieren keine spezifischen Anleitungen oder Diagnose-Werkzeuge für das Produktmodell.",
                            "score": 0.0,
                        },
                        {
                            "label": "Dokumentationen und Werkzeuge sind teilweise vorhanden, aber lückenhaft oder schwer zugänglich.",
                            "score": 0.5,
                        },
                        {
                            "label": "Vollständige Diagnose-Tools und detaillierte Reparaturanleitungen stehen dem Personal zur Verfügung.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "2.3 Kundenforschung & Entscheidungsfindung": {
            "description": "Bewertet die Analyse von Kundenanforderungen und die strategische Entscheidungsfindung.",
            "questions": [
                {
                    "code": "2.3.1",
                    "text": "Analyse der Kundenanforderungen: Werden Änderungen bei den Kundenanforderungen für nachfolgende Nutzungszyklen für Aufbereitungsmodelle analysiert?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Kundenanforderungen für nachfolgende Nutzungszyklen werden in der Planung nicht berücksichtigt.",
                            "score": 0.0,
                        },
                        {
                            "label": "Erste Analysen für nachfolgende Nutzungszyklen wurden initiiert, sind aber noch nicht abgeschlossen.",
                            "score": 0.3,
                        },
                        {
                            "label": "Es existieren konkrete Planungen für nachfolgende Nutzungszyklen basierend auf Marktforschung.",
                            "score": 0.7,
                        },
                        {
                            "label": "Konkrete Planungen für nachfolgende Nutzungszyklen sind als Standardprozess in der Aufbereitungs-Operation verankert.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "2.3.2",
                    "text": "Strategische Definition des Aussonderungsgrundes: Was ist der Hauptgrund für die Aussonderung (Defekt vs. Obsoleszenz)?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Entscheidungen über die Aussonderung von Produkten erfolgen rein ad-hoc ohne strategische Grundlage.",
                            "score": 0.0,
                        },
                        {
                            "label": "Bestimmte Merkmale für das Ende der Erstnutzung sind teilweise definiert, aber nicht konsequent umgesetzt.",
                            "score": 0.5,
                        },
                        {
                            "label": "Der Hauptgrund für die Aussonderung ist strategisch über klare technische oder wirtschaftliche Merkmale definiert.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "2.3.3",
                    "text": "Strategische Kategorisierung der Produkte nach Aufbereitungsstrategien: Wie werden die gebrauchten Produkte nach unterschiedlichen Aufbereitungsstrategien kategorisiert?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Entscheidungen über die Kategorisierung von Produkten erfolgen rein ad-hoc ohne strategische Grundlage.",
                            "score": 0.0,
                        },
                        {
                            "label": "Bestimmte Merkmale für das Ende der Erstnutzung sind teilweise definiert, aber nicht konsequent umgesetzt.",
                            "score": 0.5,
                        },
                        {
                            "label": "Entscheidungen über die Kategorisierung von Produkten sind strategisch über klare technische oder wirtschaftliche Merkmale definiert.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "2.4 Stakeholder und Soziale Integration": {
            "description": "Bewertet das Partnernetzwerk und die Förderung lokaler Wertschöpfung.",
            "questions": [
                {
                    "code": "2.4.1",
                    "text": "Partnernetzwerk für Aufarbeitung: Sind Partner (Recycler, Aufbereitungsdienstleister, Lieferanten) vertraglich angebunden?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es bestehen keine Kontakte zu Partnern.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es gibt eine Liste potenzieller Partner, aber noch keine aktive Kontaktaufnahme.",
                            "score": 0.25,
                        },
                        {
                            "label": "Es bestehen lose, projektbezogene Kontakte zu Partnern.",
                            "score": 0.5,
                        },
                        {
                            "label": "Ein Netzwerk ist vorhanden und arbeitet regelmäßig zusammen, jedoch ohne feste Verträge.",
                            "score": 0.75,
                        },
                        {
                            "label": "Partner sind über ein integriertes Netzwerk fest vertraglich angebunden.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "2.4.2",
                    "text": "Förderung lokaler Arbeitsplätze: Fördert die Zirkularitätsstrategie aktiv lokale Arbeitsplätze?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Die Zirkularitätsstrategie verfolgt keine sozialen Ziele in Bezug auf den Arbeitsmarkt.",
                            "score": 0.0,
                        },
                        {
                            "label": "Die Strategie hat lediglich indirekte Effekte auf lokale Arbeitsplätze (z. B. durch allgemeine Logistik).",
                            "score": 0.5,
                        },
                        {
                            "label": "Die Strategie schafft aktiv lokale Wertschöpfung durch regionale Reparatur- oder Aufbereitungszentren.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
    },
    "Wirtschaftlichkeit": {
        "3.1 Kosteneffizienz": {
            "description": "Prüft die finanzielle Rentabilität der Sekundärteilverwertung.",
            "questions": [
                {
                    "code": "3.1.1",
                    "text": "Preisverhältnis Sekundärteile zu Neuteilen: Wie verhalten sich Kosten für Sekundärteile zu Neuteilen?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Sekundärteile sind gleich teuer oder teurer als Neuteile, wodurch kein ökonomischer Anreiz für deren Verwendung besteht.",
                            "score": 0.0,
                        },
                        {
                            "label": "Sekundärteile sind geringfügig günstiger als Neuteile, was die Wirtschaftlichkeit nur minimal verbessert.",
                            "score": 0.5,
                        },
                        {
                            "label": "Sekundärteile sind deutlich günstiger als Neuteile (> 50% Ersparnis), was die Zirkularität ökonomisch hochattraktiv macht.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "3.1.2",
                    "text": "Aufarbeitungskosten im Verhältnis zum Neupreis: Wie verhalten sich Gesamtkosten der Aufarbeitung zum Neupreis?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Die Aufarbeitungskosten liegen über 80% des Neupreises.",
                            "score": 0.0,
                        },
                        {
                            "label": "Die Aufarbeitungskosten sind hoch (60% bis 80% des Neupreises).",
                            "score": 0.25,
                        },
                        {
                            "label": "Die Aufarbeitungskosten sind moderat und bewegen sich zwischen 30% und 60% des Neupreises.",
                            "score": 0.5,
                        },
                        {
                            "label": "Die Kosten sind niedrig (15% bis 30% des Neupreises).",
                            "score": 0.75,
                        },
                        {
                            "label": "Die Aufarbeitung ist hocheffizient und kostet weniger als 15% des Neupreises.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "3.1.3",
                    "text": "Reduktion realer Umwelt- und Sozialkosten: Werden diese (z.B. CO2-Fußabdruck) im Vergleich zum Vorgänger reduziert?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es erfolgt keine Reduktion im Vergleich zum Vorgängerprodukt.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es wird eine geringe Reduktion der externalisierten Kosten (z. B. CO2-Fußabdruck) erreicht.",
                            "score": 0.5,
                        },
                        {
                            "label": "Es erfolgt eine signifikante Reduktion (> 20%) der realen Umwelt- und Sozialkosten.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "3.2 Erlöspotenzial und Wertstabilität": {
            "description": "Bewertet Erlöspotenzial und Wertstabilität über die Zeit.",
            "questions": [
                {
                    "code": "3.2.1",
                    "text": "Wiederverkaufspreis nach Aufbereitung: Welcher Wiederverkaufspreis ist nach Aufbereitung (mit Garantie) erzielbar?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Das Produkt erzielt nach der Aufbereitung lediglich den reinen Schrott- oder Materialwert.",
                            "score": 0.0,
                        },
                        {
                            "label": "Der erzielbare Restwert ist gering und deckt kaum die Kosten des Aufbereitungsprozesses.",
                            "score": 0.3,
                        },
                        {
                            "label": "Es wird ein moderater Wiederverkaufspreis erzielt, der eine stabile wirtschaftliche Zweitvermarktung erlaubt.",
                            "score": 0.7,
                        },
                        {
                            "label": "Das aufbereitete Produkt (mit Garantie) erzielt einen hohen Restwert nahe am Preis eines Neuprodukts.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "3.2.2",
                    "text": "Effizienz der Wertstabilität durch Aufbereitung: Wie effizient kann der Marktwert stabil gehalten werden?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Das Produkt unterliegt einem extrem schnellen Marktwertverlust, der durch Aufbereitung nicht aufgefangen werden kann.",
                            "score": 0.0,
                        },
                        {
                            "label": "Die Wertstabilität ist minimal; das Produkt veraltet technisch oder modisch schnell.",
                            "score": 0.25,
                        },
                        {
                            "label": "Eine moderate Wertstabilität wird erreicht, sofern kontinuierlich in die Aufbereitung investiert wird.",
                            "score": 0.5,
                        },
                        {
                            "label": "Durch gezielte Aufbereitungsprozesse kann der Marktwert über längere Zeiträume stabilisiert werden.",
                            "score": 0.75,
                        },
                        {
                            "label": "Das Modell ermöglicht eine exzellente Wertstabilität; das Produkt behält über mehrere Zyklen hinweg einen hohen Marktwert.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "3.3 Logistik- & Lagerkosten": {
            "description": "Bewertet den Einfluss von Lagerdauer auf die Wirtschaftlichkeit.",
            "questions": [
                {
                    "code": "3.3.1",
                    "text": "Einfluss der Lagerdauer auf die Wirtschaftlichkeit: Welchen Einfluss hat die Lagerdauer?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Die Wirtschaftlichkeit leidet massiv unter einer hohen Lagerdauer und der damit verbundenen hohen Kapitalbindung.",
                            "score": 0.0,
                        },
                        {
                            "label": "Der Einfluss der Lagerdauer ist moderat; die Umschlagshäufigkeit der zirkulären Produkte ist zufriedenstellend.",
                            "score": 0.5,
                        },
                        {
                            "label": "Die Lagerdauer hat durch hocheffiziente Logistik und schnellen Umschlag kaum negativen Einfluss auf die Rentabilität.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "3.4 Wirtschaftliches Risiko": {
            "description": "Bewertet das Risiko von technischen Folgeschäden nach Reparatur.",
            "questions": [
                {
                    "code": "3.4.1",
                    "text": "Risiko technischer Folgeschäden nach Reparatur: Wie hoch ist das Risiko basierend auf der Modellhistorie?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Das Risiko für unvorhersehbare und teure technische Folgeschäden nach einer Aufbereitung ist unberechenbar hoch.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es treten regelmäßig Folgeschäden auf, was hohe finanzielle Rücklagen für Garantieleistungen erfordert.",
                            "score": 0.3,
                        },
                        {
                            "label": "Das Risiko technischer Folgeschäden ist bekannt und durch standardisierte Prozesse kalkulierbar.",
                            "score": 0.7,
                        },
                        {
                            "label": "Das Risiko technischer Folgeschäden ist aufgrund der langjährigen Modellhistorie als sehr gering einzustufen.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
    },
    "Regulatorik": {
        "4.1 Stoffrecht & Sicherheit": {
            "description": "Bewertet rechtliche Konformität und Sicherheit bei der Demontage.",
            "questions": [
                {
                    "code": "4.1.1",
                    "text": "SVHC (Substances of Very High Concern) - Stoffe und Grenzwerte: Enthält das Produkt SVHC-Stoffe mit verschärften Grenzwerten?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Das Produkt enthält SVHC-Stoffe, deren Mengen kritisch sind oder Grenzwerte nur knapp einhalten.",
                            "score": 0.0,
                        },
                        {
                            "label": "Das Produkt enthält SVHC-Stoffe, wobei alle aktuell geltenden Grenzwerte sicher eingehalten werden.",
                            "score": 0.5,
                        },
                        {
                            "label": "Das Produkt ist vollkommen konform und enthält nachweislich keinerlei SVHC-Stoffe oder gefährliche Chemikalien.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "4.1.2",
                    "text": "Sicherheit bei der Demontage: Sind gefährliche Stoffe für Techniker ohne Spezial-PSA zugänglich?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Gefährliche Stoffe sind für Techniker bei der Demontage direkt zugänglich, was ein hohes Gesundheitsrisiko darstellt.",
                            "score": 0.0,
                        },
                        {
                            "label": "Der Zugriff auf gefährliche Stoffe ist nur unter Einsatz spezieller persönlicher Schutzausrüstung (PSA) sicher möglich.",
                            "score": 0.5,
                        },
                        {
                            "label": "Das Design stellt sicher, dass gefährliche Stoffe bei der Zerlegung physisch isoliert bleiben.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "4.1.3",
                    "text": "Regulatorische Barrieren für die Wiederverwendung: Gibt es regulatorische Barrieren (z. B. Hygienerichtlinien), die eine Wiederverwendung ausschließen?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es bestehen starke regulatorische Verbote, die eine Wiederverwendung des Produkts rechtlich nahezu unmöglich machen.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es existieren erhebliche rechtliche Hürden, deren Überwindung derzeit einen unwirtschaftlichen Aufwand erfordert.",
                            "score": 0.25,
                        },
                        {
                            "label": "Die rechtliche Lage für die Wiederverwendung ist unklar oder durch teilweise Einschränkungen gekennzeichnet.",
                            "score": 0.5,
                        },
                        {
                            "label": "Es bestehen nur geringfügige regulatorische Auflagen, die durch standardisierte Prüfprozesse erfüllt werden können.",
                            "score": 0.75,
                        },
                        {
                            "label": "Es sind keine regulatorischen Barrieren bekannt; das Design erlaubt eine uneingeschränkte rechtliche Wiederverwendung.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "4.2 Zertifizierung & Status": {
            "description": "Bewertet die Gültigkeit von Zertifikaten und den rechtlichen Status wiederaufbereiteter Produkte.",
            "questions": [
                {
                    "code": "4.2.1",
                    "text": "Gültigkeit von Sicherheitszertifikaten: Bleiben Sicherheitszertifikate (z. B. CE, VDE) nach der fachgerechten Aufbereitung rechtlich gültig?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Sicherheitszertifikate erlöschen nach einer Aufarbeitung unwiderruflich und können nicht erneuert werden.",
                            "score": 0.0,
                        },
                        {
                            "label": "Nach einer fachgerechten Aufarbeitung ist eine aufwendige und kostenintensive Neuabnahme erforderlich.",
                            "score": 0.5,
                        },
                        {
                            "label": "Die Sicherheitszertifikate bleiben nach einer fachgerechten Aufarbeitung rechtlich vollumfänglich gültig.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "4.2.2",
                    "text": "Rechtlicher Status (Abfall vs. Produkt): Kann das Produkt rechtlich als 'Gebrauchtware' eingestuft werden?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Das rückgeführte Produkt wird rechtlich zwingend als Abfall eingestuft, was eine hochwertige Aufarbeitung verhindert.",
                            "score": 0.0,
                        },
                        {
                            "label": "Das Ende der Abfalleigenschaft ist theoretisch möglich, aber mit extrem hohen bürokratischen Hürden verbunden.",
                            "score": 0.25,
                        },
                        {
                            "label": "Der Rechtsstatus als 'Gebrauchtware' wird erst nach einer zeitaufwendigen Einzelfallprüfung durch Behörden geklärt.",
                            "score": 0.5,
                        },
                        {
                            "label": "Das Produkt kann unter definierten Bedingungen (z. B. Funktionsprüfung) unkompliziert als Gebrauchtware deklariert werden.",
                            "score": 0.75,
                        },
                        {
                            "label": "Das Produkt behält über den gesamten Rückführungsprozess hinweg sofort und unproblematisch seinen Produktstatus.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "4.3 Software-Compliance & Rechte": {
            "description": "Bewertet die Übertragbarkeit von Software-Lizenzen.",
            "questions": [
                {
                    "code": "4.3.1",
                    "text": "Übertragbarkeit von Software-Lizenzen: Erlauben Lizenzbedingungen die Übertragung auf Zweitbesitzer?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Lizenzbedingungen schließen eine Übertragung der Software auf Zweitbesitzer kategorisch aus.",
                            "score": 0.0,
                        },
                        {
                            "label": "Eine Übertragung der Lizenzen ist nur gegen erhebliche Gebühren oder hohen administrativen Aufwand möglich.",
                            "score": 0.5,
                        },
                        {
                            "label": "Die Software-Lizenzen können uneingeschränkt und ohne Zusatzkosten auf nachfolgende Besitzer übertragen werden.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "4.4 Dokumentationspflichten": {
            "description": "Bewertet die Lesbarkeit und Dauerhaftigkeit von Kennzeichnungen.",
            "questions": [
                {
                    "code": "4.4.1",
                    "text": "Lesbarkeit und Dauerhaftigkeit der Kennzeichnung: Sind Kennzeichnungen (Seriennummern/Warnhinweise) dauerhaft lesbar?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Kennzeichnungen sind nicht vorhanden oder nach der Nutzung unlesbar.",
                            "score": 0.0,
                        },
                        {
                            "label": "Kennzeichnungen sind teilweise beschädigt, was die eindeutige Identifizierung erschwert.",
                            "score": 0.3,
                        },
                        {
                            "label": "Alle regulatorisch relevanten Kennzeichnungen sind vorhanden und physisch gut lesbar.",
                            "score": 0.7,
                        },
                        {
                            "label": "Sämtliche Kennzeichnungen sind dauerhaft lesbar und zusätzlich digital (z. B. via RFID/QR) hinterlegt.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "4.5 Compliance mit Rückverfolgbarkeitsstandards": {
            "description": "Bewertet die Erfüllung von Daten-Rückverfolgbarkeit (z. B. ESPR).",
            "questions": [
                {
                    "code": "4.5.1",
                    "text": "Erfüllung von Daten-Rückverfolgbarkeit (z. B. ESPR): Erfüllt das Produkt die Anforderungen?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es existiert keine Transparenz oder Dokumentation über die Materialherkunft in der Lieferkette.",
                            "score": 0.0,
                        },
                        {
                            "label": "Die Rückverfolgbarkeit ist nur bis zu den direkten Zulieferern (Tier-1) gewährleistet.",
                            "score": 0.5,
                        },
                        {
                            "label": "Die Anforderungen an die Rückverfolgbarkeit werden über die gesamte Lieferkette voll erfüllt.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
    },
    "Systemische Befähiger": {
        "5.1 Digitale Identität & IoT & Prognose": {
            "description": "Bewertet die digitale Infrastruktur und Zustandsüberwachung.",
            "questions": [
                {
                    "code": "5.1.1",
                    "text": "Digitaler Produktpass (DPP): Existiert ein DPP oder kann über eine Kennung (QR, RFID) auf Materialdaten zugegriffen werden?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es existiert keine digitale Identität oder Möglichkeit zum Datenzugriff für das Produkt.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es ist eine einfache physische Kennung (z. B. Seriennummer) vorhanden, die jedoch nicht digital verknüpft ist.",
                            "score": 0.25,
                        },
                        {
                            "label": "Über eine Kennung (QR/RFID) kann auf statische Basisdaten (z. B. Handbuch, Materialliste) zugegriffen werden.",
                            "score": 0.5,
                        },
                        {
                            "label": "Ein DPP ist implementiert und bietet Zugriff auf dynamische Lebenszyklusdaten (z. B. Reparaturhistorie).",
                            "score": 0.75,
                        },
                        {
                            "label": "Es besteht voller Datenzugriff via DPP, konform zu EU-Standards (ESPR) mit allen relevanten Material- und Kreislaufdaten.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "5.1.2",
                    "text": "Zustandsüberwachung via IoT: Zeichnen Sensoren den Verschleiß (Betriebsstunden/Zyklen/Fehler) auf?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es findet keine Aufzeichnung von Nutzungs- oder Verschleißdaten durch Sensoren statt.",
                            "score": 0.0,
                        },
                        {
                            "label": "Verschleißdaten werden aufgezeichnet, erfordern jedoch ein manuelles, punktuelles Auslesen vor Ort.",
                            "score": 0.5,
                        },
                        {
                            "label": "Sensoren stellen Echtzeitdaten über den Zustand, Fehler und Nutzungszyklen drahtlos zur Verfügung.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "5.1.3",
                    "text": "Predictive Maintenance: Ermöglichen die digitalen Systeme/Sensoren vorausschauende Wartung?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Eine Integration digitaler Systeme zur vorausschauenden Wartung existiert nicht.",
                            "score": 0.0,
                        },
                        {
                            "label": "Digitale Systeme erlauben lediglich ein reaktives Auslesen von Fehlern nach deren Eintreten.",
                            "score": 0.5,
                        },
                        {
                            "label": "Voll integrierte Systeme ermöglichen eine vorausschauende Wartung zur Vermeidung von Ausfällen.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "5.1.4",
                    "text": "Restlebensdauer-Prognose: Ermöglichen die digitalen Systeme eine Vorhersage der verbleibenden Restlebensdauer?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Eine Diagnose oder Prognose der verbleibenden Lebensdauer ist technisch nicht möglich.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es sind einfache reaktive Statusanzeigen vorhanden, die den aktuellen Zustand grob schätzen.",
                            "score": 0.5,
                        },
                        {
                            "label": "Es existieren präzise Prognosemodelle, die die Restlebensdauer von Schlüsselkomponenten exakt vorhersagen.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "5.2 Rückführungs-Infrastruktur": {
            "description": "Bewertet die Logistics und Dokumentation von Rückflüssen.",
            "questions": [
                {
                    "code": "5.2.1",
                    "text": "Planbare Rückflussquote: Wie hoch ist die planbare Rückflussquote für dieses Modell?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Der Rückfluss von Altprodukten ist gering, rein zufällig und wird nicht aktiv gesteuert.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es wird eine geringe, aber messbare Rückflussquote von bis zu 10% erreicht.",
                            "score": 0.25,
                        },
                        {
                            "label": "Es wird eine moderate, planbare Rückflussquote zwischen 10% und 49% erzielt.",
                            "score": 0.5,
                        },
                        {
                            "label": "Die Rückflussquote ist hoch und liegt stabil zwischen 50% und 79%.",
                            "score": 0.75,
                        },
                        {
                            "label": "Es wird eine sehr hohe und präzise planbare Rückflussquote von 80% bis 100% erreicht.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "5.2.2",
                    "text": "Zirkuläre Rückversand-Verpackung: Wird eine wiederverwendbare Verpackung für den Rückversand bereitgestellt?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Für den Rückversand wird keine spezielle Verpackung bereitgestellt; der Kunde muss selbst vorsorgen.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es wird eine Einweg-Ersatzverpackung bereitgestellt, die für den einmaligen Rücktransport optimiert ist.",
                            "score": 0.5,
                        },
                        {
                            "label": "Es wird eine robuste, mehrfach wiederverwendbare Verpackung für den sicheren Rückversand zur Verfügung gestellt.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "5.2.3",
                    "text": "Dokumentation kritischer Komponenten: Ist der Ursprung der verbauten kritischen Komponenten über die Lieferkette dokumentiert?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Der Ursprung und Verbleib verbauter kritischer Komponenten ist innerhalb der Lieferkette unbekannt.",
                            "score": 0.0,
                        },
                        {
                            "label": "Die Dokumentation der Lieferkette ist teilweise vorhanden, weist jedoch Lücken bei Sub-Lieferanten auf.",
                            "score": 0.5,
                        },
                        {
                            "label": "Der Ursprung aller kritischen Komponenten ist über die gesamte Lieferkette hinweg lückenlos dokumentiert.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "5.3 Nutzung und Support": {
            "description": "Bewertet den Endnutzer-Support und die Nutzungsintensität.",
            "questions": [
                {
                    "code": "5.3.1",
                    "text": "Aktives Offboarding-Support: Wird der Endnutzer aktiv bei der Rückgabe (Offboarding) unterstützt?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Der Endnutzer erhält keine Unterstützung bei der Rückgabe oder Entsorgung des Produkts.",
                            "score": 0.0,
                        },
                        {
                            "label": "Es wird eine teilweise Unterstützung angeboten (z. B. Informationen über Entsorgungsstellen).",
                            "score": 0.5,
                        },
                        {
                            "label": "Das Unternehmen bietet volle Unterstützung beim Offboarding durch aktive Rückhollogistik oder Trade-In-Services.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "5.3.2",
                    "text": "Belohnungssystem für Produktrückgabe: Existiert ein Belohnungssystem für die Rückgabe des Produkts?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es existiert kein System, das Kunden zur Rückgabe ausgedienter Produkte motiviert.",
                            "score": 0.0,
                        },
                        {
                            "label": "Ein Belohnungssystem befindet sich aktuell in der Konzeptions- oder Planungsphase.",
                            "score": 0.3,
                        },
                        {
                            "label": "Es werden erste Anreize geboten (z. B. Rabatt auf Neukauf), die jedoch noch nicht flächendeckend wirken.",
                            "score": 0.7,
                        },
                        {
                            "label": "Ein etabliertes Anreizsystem (z. B. garantierter Rückkauf) ist erfolgreich implementiert.",
                            "score": 1.0,
                        },
                    ],
                },
                {
                    "code": "5.3.3",
                    "text": "Nutzungsintensität (Sharing/PaaS): Wird das Produkt im Vergleich zum Marktdurchschnitt intensiver genutzt?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Das Produkt weist viele Leerlaufzeiten auf und wird rein privat/einzeln genutzt.",
                            "score": 0.0,
                        },
                        {
                            "label": "Die Nutzungsintensität entspricht dem Marktdurchschnitt.",
                            "score": 0.5,
                        },
                        {
                            "label": "Durch Sharing-Modelle oder intensive gewerbliche Nutzung wird das Produkt deutlich über dem Durchschnitt ausgelastet.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
        "5.4 Datenaustausch": {
            "description": "Bewertet den Austausch von Zirkularitätsdaten mit externen Partnern.",
            "questions": [
                {
                    "code": "5.4.1",
                    "text": "Datenaustausch in der Lieferkette: Gibt es Kanäle zum Austausch von Zirkularitätsdaten mit externen Partnern?",
                    "type": "mc",
                    "options": [
                        {
                            "label": "Es findet kein Austausch von Zirkularitätsdaten mit externen Partnern statt.",
                            "score": 0.0,
                        },
                        {
                            "label": "Ein Datenaustausch erfolgt nur unregelmäßig oder auf explizite Anfrage.",
                            "score": 0.5,
                        },
                        {
                            "label": "Es findet ein standardisierter, automatisierter Austausch von Zirkularitätsdaten mit allen relevanten Partnern statt.",
                            "score": 1.0,
                        },
                    ],
                },
            ],
        },
    },
}
