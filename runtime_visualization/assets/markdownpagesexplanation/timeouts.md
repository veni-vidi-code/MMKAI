# Timeouts

In dieser Grafik wird der prozentuale Anteil an Timeouts in Abhängigkeit von der Anzahl an Gegenständen, der Anzahl an
Gewichtsklassen und der Anzahl an Rucksäcken aufgetragen. Der Prozentuale Anteil an Timeouts wird durch die Größe der
Datenpunkte dargestellt. Die Legende zeigt die Farben der einzelnen Algorithmen an. Die Achse der Anzahl an Gegeständen
ist logarithmisch skaliert. Die beiden anderen Achsen sind linear skaliert. Die Datenpunkte, bei denen kein Timeout
aufgetreten ist, sind standardmäßig nicht sichtbar. Um diese anzuzeigen kann die entsprechende Legende angeklickt
werden. Diese Datenpunkte werden dann mit der Größe von $5%$ der maximalen Größe der Datenpunkte dargestellt.

Um einen guten Überblick zu erhalten ist es empfehlenswert, die dreidimensionalen Graphen zu drehen und aus verschiedenen
Winkeln zu betrachten. Dies ist durch das Bewegen der Maus bei gedrückter linker Maustaste möglich. Außerdem kann durch
das Scrollen mit dem Mausrad gezoomt werden und durch das Bewegen der Maus auf einen Datenpunkt die genauen Werte
dieses Datenpunktes angezeigt werden. Hierbei gibt Size die Größe des Datenpunktes in Prozentpunkten an.

#### Anmerkungen zum Graphen
In dem Graph zeigt sich, dass die Timeouts des MTM EXENDED hauptsächlich durch die Anzahl an Gegenständen beeinflusst
werden. Darüber hinaus lässt sich erkennen, dass die Anzahl an Rucksäcken einen deutlich stärkeren Einfluss auf die
Timeouts des MMKAI hat als auf die des MTM EXTENDED. Dies zeigt insbesondere bei $10000$ Gegenständen und wenigen
Geiwchtksklassen. 

Außderdem wird deutlich, dass der MMKAI zwar auch von der Anzahl an Gegenständen abhängt jedoch deutlich stärker von der
Anzahl an Gewichtsklassen und Ruksäcken. Dies ist auch zu erwarten, da diese beiden im Exponenten der Laufzeit des
MMKAI Algorithmus auftreten, während die Anzahl an Gegenständen nur in der Basis auftritt.