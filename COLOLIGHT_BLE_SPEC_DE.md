# Cololight BLE-Steuerungsprotokoll - Deutsche Übersetzung

🇬🇧 [English version](COLOLIGHT_BLE_SPEC_ENGLISH.md)

## BLE-UUID

**Cololight Custom UUID:** `91be3ad5-2c4a-4e82-8a1c-bae9c9116593`

---

## Characteristics

### Characteristic 1 (IDX1) - Ein/Aus- und Helligkeitssteuerung

**UUID:** `b4d64c4f-c5a0-4a1b-afea-306b66269750`

**Eigenschaften:** Write, Read, Notify, Write-Without-Response

**Funktion:** Steuert und liest Geräte-IO-P1

**Parameter:** `type(1 Byte) + value(1 Byte)`

**Befehle:**
- **Ein/Aus:**
  - Type: `0x80` (aus) / `0x81` (an)
  - Value: `0` (aus) / `1` (an)

- **Ein/Aus + Helligkeit:**
  - Type: `0xce` (aus mit Helligkeit) / `0xcf` (an mit Helligkeit)
  - Value: Helligkeit `0-255` (Helligkeitsstufe der Lampe)

---

### Characteristic 2 (IDX2) - Lichteffekt-Steuerung

**UUID:** `2edcf977-60ac-49b0-aa2a-ed75abd74ea3`

**Eigenschaften:** Write, Read, Notify, Write-Without-Response

**Funktion:** Steuert und liest Geräte-IO-P2

**Parameter:** `type(1 Byte) + value(4 Byte)`

**Befehle:**
- **Ein/Aus:**
  - Type: `0x80` (aus) / `0x81` (an)
  - Value: `0` / `1`

- **Ein/Aus + Effekt setzen:**
  - Type: `0xfe` (aus mit Effekt) / `0xff` (an mit Effekt)
  - Value: `1 Byte (Modus) + 3 Byte (Parameter)`
    - Erstes Byte: Modus-Typ
    - Letzte 3 Byte: Parameter für diesen Modus

---

## Modus- und Parameterdefinitionen

### Modus 0x00 - Einfarbmodus

**Format:** `[0xff] [0x00] [RR] [GG] [BB]`

- **RR GG BB:** RGB-Farbwerte (je 0x00-0xFF)

**Beispiel:** `0xff 0x00 0xff 0x00 0x00` = Reines Rot

---

### Modus 0x01 - Dynamischer Gesamtmodus

**Format:** `[0xff] [0x01] [AA] [BB] [CC]`

- **AA:** Index des dynamischen Effekts (siehe Effektliste unten)
- **BB:** Wechselgeschwindigkeit (0x00-0xFF, höherer Wert = langsamer)
- **CC:** Variationsmodus (0x00-0x0F), Standard: 0x00

**Beispiel:** `0xff 0x01 0x80 0x0a 0x00`
- Modus: 0x01 (dynamisch)
- Effekt: 0x80 (Rot-Grün-Blau-Atmen)
- Geschwindigkeit: 0x0a (Standardgeschwindigkeit)
- Variation: 0x00 (Standard)

---

### Modus 0x03 - Spezieller dynamischer Gesamtmodus

**Format:** `[0xff] [0x03] [AA] [BB] [CD]`

- **AA:** Effekt-Index (wie bei Modus 0x01)
- **BB:** Wechselgeschwindigkeit, typischerweise 0x0a
- **C:** Variationsmodus (0-F)
- **D:** Farbsprung-Modus (0-F), Standard: 0

**Variationsmodi (C):**
- `0x0` - Gesamter dynamischer Effekt
- `0x1` - Äußerer Kreis zu innerem Verlauf
- `0x2` - Dynamik am Mittelpunkt
- `0x3` - Innerer Kreis, gesamter dynamischer Effekt
- `0x4` - Äußerer Kreis, gesamter dynamischer Effekt
- `0x5` - Verlauf von beiden Seiten zur Mittellinie
- `0x6` - Diagonal zur Mittellinie, gesamter dynamischer Effekt
- `0x7` - Diagonale Mittellinie, beide Seiten, gesamter dynamischer Effekt
- `0x8` - Diagonale äußere zwei Linien, gesamter dynamischer Effekt
- `0x9` - Verlauf von oben nach unten, dynamisch
- `0xa` - Untere Seite, eine Linie, gesamter dynamischer Effekt
- `0xb` - Horizontale Mittellinie, untere Linie, gesamter dynamischer Effekt
- `0xc` - Horizontale Mittellinie, gesamter dynamischer Effekt
- `0xd` - Horizontale Mittellinie, obere Linie, gesamter dynamischer Effekt
- `0xe` - Obere Seite, eine Linie, gesamter dynamischer Effekt
- `0xf` - Blütenform, gesamter dynamischer Effekt

**Beispiel:** `0xff 0x03 0xaf 0x0a 0x20`
- Modus: 0x03 (speziell, gesamt)
- Effekt: 0xaf (Freunde beim Essen)
- Geschwindigkeit: 0x0a
- Variation: 0x2 (Mittelpunkt)
- Sprung: 0x0 (Standard)

---

### Modus 0x04 - Spezieller dynamischer Einzelmodus

**Format:** `[0xff] [0x04] [AA] [BB] [CD]`

- **AA:** Effekt-Index (wie bei Modus 0x01)
- **BB:** Wechselgeschwindigkeit, typischerweise 0x0a
- **C:** Variationsmodus (0-F)
- **D:** Farbsprung-Modus (0-F), Standard: 0

**Variationsmodi (C):**
- `0x0` - Gesamter Punktdynamik-Effekt
- `0x1` - Dynamik am Mittelpunkt
- `0x2` - Innerer Kreis, Punktdynamik
- `0x3` - Äußerer Kreis, Punktdynamik
- `0x4` - Zwei Blöcke als Basis, äußerer Kreis, Punktdynamik
- `0x5` - Drei Blöcke als Basis, äußerer Kreis, Punktdynamik

---

### Modus 0x05 - Sanfter Übergang von Modus 0x03

Gleiche Parameter wie Modus 0x03, aber mit sanften Übergängen zwischen den Zuständen.

---

### Modus 0x06 - Sanfter Übergang von Modus 0x04

Gleiche Parameter wie Modus 0x04, aber mit sanften Übergängen zwischen den Zuständen.

---

## Effektindex-Liste (Parameter AA für Modus 0x01)

### Atem-Effekte (Breathing)

- `0x80` - Rot-Grün-Blau atmend
- `0x81` - Rot-Orange-Gelb-Grün-Cyan-Blau-Violett atmend (7 Farben)
- `0x82` - Grün atmend
- `0x83` - Cyan atmend
- `0x84` - Blau atmend
- `0x85` - Violett atmend
- `0x86` - Rot atmend
- `0x87` - Orange atmend
- `0x88` - Gelb atmend
- `0x89` - Weiß atmend

### Verlaufseffekte (Gradient)

- `0x8a` - Verlauf Rot zu Gelb
- `0x8b` - Verlauf Rot zu Grün
- `0x8d` - Verlauf Rot zu Blau
- `0x8e` - Verlauf Grün zu Gelb
- `0x8f` - Verlauf Grün zu Cyan
- `0x90` - Verlauf Grün zu Blau
- `0x91` - Verlauf Blau zu Cyan
- `0x92` - Verlauf Blau zu Violett
- `0x93` - Verlauf Gelb zu Weiß
- `0x94` - Verlauf Rot zu Weiß
- `0x95` - Verlauf Grün zu Weiß
- `0x96` - Verlauf Cyan zu Weiß
- `0x97` - Verlauf Blau zu Weiß
- `0x98` - Verlauf Violett zu Weiß

### Blitz-Effekte (Flash)

- `0x99` - Rot-Grün-Blau blitzend
- `0x9a` - 7-Farben blitzend
- `0x9b` - Grün blitzend
- `0x9c` - Cyan blitzend
- `0x9d` - Blau blitzend
- `0x9e` - Violett blitzend
- `0x9f` - Rot blitzend
- `0xa0` - Orange blitzend
- `0xa1` - Gelb blitzend
- `0xa2` - Weiß blitzend

### Schnelle Blitz-Effekte (Fast Flash)

- `0xa3` - Rot-Grün-Blau schnell blitzend
- `0xa4` - 7-Farben schnell blitzend
- `0xa5` - Grün schnell blitzend
- `0xa6` - Cyan schnell blitzend
- `0xa7` - Blau schnell blitzend
- `0xa8` - Violett schnell blitzend
- `0xa9` - Rot schnell blitzend
- `0xaa` - Orange schnell blitzend
- `0xab` - Gelb schnell blitzend
- `0xac` - Weiß schnell blitzend

### Szenen-Effekte (Party-Modus - P)

- `0xad` - Geburtstagsfeier
- `0xae` - Mädelsrunde / Nachmittagstee
- `0xaf` - Freunde beim Essen
- `0xb0` - Kollegen beim Essen
- `0xb1` - Familienessen
- `0xb2` - Date zu zweit

### Stimmungsfarben-Effekte (P)

- `0xb3` - Stimmungsfarbe - Rot
- `0xb4` - Stimmungsfarbe - Orange
- `0xb5` - Stimmungsfarbe - Gelb
- `0xb6` - Stimmungsfarbe - Grün
- `0xb7` - Stimmungsfarbe - Cyan
- `0xb8` - Stimmungsfarbe - Himmelblau
- `0xb9` - Stimmungsfarbe - Blau
- `0xba` - Stimmungsfarbe - Pink
- `0xbb` - Stimmungsfarbe - Gold
- `0xbc` - Stimmungsfarbe - Bunt
- `0xbd` - Stimmungsfarbe - Vollfarbe

### Natur-/Tageszeit-Effekte

- `0xbe` - Sonnenaufgang 0
- `0xbf` - Wolkenaufzug
- `0xc0` - Grünes Feld
- `0xc1` - Sonnenaufgang
- `0xc2` - Sternenhimmel
- `0xc3` - Macaron
- `0xc4` - Blau-Grün atmend

---

## Protokoll-Hinweise

### Geschwindigkeitsparameter (BB)
- Bereich: `0x00` - `0xFF`
- Höherer Wert = langsamere Geschwindigkeit
- Standard/Empfohlen: `0x0a`

### Variationsmodus (CC oder C)
- Bereich: `0x0` - `0xF`
- Steuert das Muster, in dem der Effekt dargestellt wird
- Standard: `0x00`

### Farbsprung-Modus (D)
- Bereich: `0x0` - `0xF`
- Steuert, wie Farben übergehen
- Standard: `0x0`

---

## Übersicht der gängigsten Befehle

| Befehl | Type-Byte | Modus | Parameter | Beschreibung |
|---------|-----------|------|------------|-------------|
| **Einfarbig** | `0xff` | `0x00` | `[RR][GG][BB]` | RGB-Farbe setzen |
| **Dynamischer Effekt** | `0xff` | `0x01` | `[AA][BB][CC]` | Dynamischen Effekt setzen |
| **Speziell gesamt** | `0xff` | `0x03` | `[AA][BB][CD]` | Erweiterte Mustersteuerung |
| **Speziell einzeln** | `0xff` | `0x04` | `[AA][BB][CD]` | Einzel-LED-Steuerung |
| **Sanft gesamt** | `0xff` | `0x05` | `[AA][BB][CD]` | Modus 03 mit Weichzeichnung |
| **Sanft einzeln** | `0xff` | `0x06` | `[AA][BB][CD]` | Modus 04 mit Weichzeichnung |
| **Einschalten** | `0x81` | - | `[0x01]` | Einschalten |
| **Ausschalten** | `0x80` | - | `[0x00]` | Ausschalten |
| **Helligkeit** | `0xcf` | - | `[0-255]` | Helligkeit setzen (an) |

---

## Beispiele

### Beispiel 1: Reines Rot setzen
```
Befehl: ff 00 ff 00 00
- Type: 0xff (an mit Effekt)
- Modus: 0x00 (Einfarbig)
- Rot: 0xff (255)
- Grün: 0x00 (0)
- Blau: 0x00 (0)
```

### Beispiel 2: Weiß-Atem-Effekt
```
Befehl: ff 01 89 0a 00
- Type: 0xff (an mit Effekt)
- Modus: 0x01 (dynamisch)
- Effekt: 0x89 (weiß atmend)
- Geschwindigkeit: 0x0a (Standard)
- Variation: 0x00 (Standard)
```

### Beispiel 3: Geburtstagsfeier mit Mittelpunkt
```
Befehl: ff 03 ad 0a 20
- Type: 0xff (an mit Effekt)
- Modus: 0x03 (speziell, gesamt)
- Effekt: 0xad (Geburtstagsfeier)
- Geschwindigkeit: 0x0a (Standard)
- Variation: 0x2 (Mittelpunkt)
- Sprung: 0x0 (Standard)
```
