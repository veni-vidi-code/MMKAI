# Laufzeit nach Gewichtsklassen

In dieser Grafik werden die einzelnen Laufzeiten beider Algorithmen für eine feste Anzahl an Gewichtsklassen gegen die Anzahl
an Gegenständen und die Anzahl an Rucksäcken aufgetragen. Der Legende sind die Farben der einzelnen Algorithmen zu
entnehmen. Timeouts sind mit einem anderen Symbol versehen (siehe Legende) und haben eine Laufzeit von $300$ Sekunden
zugewiesen bekommen um diese besser von den anderen Datenpunkten unterscheiden zu können.
Die Achse der Anzahl an Gegeständen ist logarithmisch skaliert. Die beiden anderen Achsen sind linear skaliert.

Um einen guten Überblick zu erhalten ist es empfehlenswert die dreidimensionalen Graphen zu drehen und aus verschiedenen
Winkeln zu betrachten. Dies ist durch das Bewegen der Maus mit gedrückter linker Maustaste möglich.

#### Anmerkungen zu den Graphen

In diesen Graphen wird deutlich, dass zwar beide Algorithmen von der Anzahl an Rucksäcken abhängen, der MMKAI
Algorithmus jedoch deutlich stärker. Dies ist auch zu erwarten, da mit jedem Rucksack die Anzahl an möglichen
Zuweisungen steigt. Es ist zu sehen, dass der MMKAI Algorithmus deutlich stärker von der Anzahl an Rucksäcken
abhängt als der MTM EXTENDED Algorithmus. Dies lässt sich insbesondere bei $2$ Gewichtsklassen gut erkennen. Deutlicher 
wird dies jedoch in den Graphen zu den Timeouts.

Für einen besseren Überblick kann stets einer der beiden Algorithmen ausgeblendet werden. Dies ist durch einen Klick auf
die entsprechende Legende möglich. 