# Laufzeit nach Rucksäcken

In dieser Grafik werden die einzelnen Laufzeiten beider Algorithmen für eine feste Anzahl an Rucksäcken gegen die Anzahl
an Gegenständen und die Anzahl an Gewichtsklassen aufgetragen. Der Legende sind die Farben der einzelnen Algorithmen zu
entnehmen. Timeouts sind mit einem anderen Symbol versehen (siehe Legende) und haben eine Laufzeit von $300$ Sekunden
zugewiesen bekommen um diese besser von den anderen Datenpunkten unterscheiden zu können.
Die Achse der Anzahl an Gegeständen ist logarithmisch skaliert. Die beiden anderen Achsen sind linear skaliert.

Um einen guten Überblick zu erhalten ist es empfehlenswert die dreidimensionalen Graphen zu drehen und aus verschiedenen
Winkeln zu betrachten. Dies ist durch das Bewegen der Maus mit gedrückter linker Maustaste möglich.

#### Anmerkungen zu den Graphen

In den Graphen wird deutlich, dass die Laufzeit des MMKAI Algorithmus stark von der Anzahl an Gewichtsklassen abhängt.
Es zeigt sich, dass der MMKAI bei einer geringen Anzahl an Gewichtsklassen und einer geringen Anzahl an Rucksäcken
deutlich schneller ist als der MTM EXTENDED Algorithmus. Außerdem lässt sich gut sehen, dass der MTM EXTENDED
deutlich weniger von der Anzahl an Gewichtsklassen abhängt als der MMKAI Algorithmus. Dies ist auch zu erwarten, da
der MTM EXTENDED anders als der MMKAI Algorithmus nicht über die Anzahl an Gewichtsklassen arbeitet.
