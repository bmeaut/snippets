# AppMakers csapat tanulságai #
### Segmentation fault a program indulásakor ###

A Qt programunk futtatásakor rögtön az elején SIGSEGV-t dobott, még meg sem jelent semmi. Debugger csak annyit mondott, hogy az alkalmazás .exec(); -ig jut el, a többi a qt library-n belül van, ahonnan a jogosulatlan memória hivatkozás történt. [Stackoverflow](https://stackoverflow.com/questions/47330449/qt-segmentation-fault-at-exec) segített végül: a QApplication construktorának az argc referencia szerint kell (ez valóban le van írva a [dokumentációjában](https://doc.qt.io/qt-5/qapplication.html#QApplication), viszont a [példaprogramban](https://github.com/csorbakristof/alkalmazasfejlesztes/blob/af964ed7e9bf1a8f6c1b1838eb39d9a5491e4f6c/SimpleTelemetryVisualizer/main.cpp#L7) nem így volt).

    QApplication::QApplication(int &argc, char **argv)

### QML GroupBox: Binding loop detected for property "implicitWidth" ###

[https://doc.qt.io/qt-5/qml-qtquick-controls-groupbox.html](https://doc.qt.io/qt-5/qml-qtquick-controls-groupbox.html): The implicit size of the GroupBox is calculated based on the size of its content. A GroupBox mérete a tartalma alapján határozódik meg. Azaz a benne lévő dolgok méreteinek meghatározása a GroupBox méretének tudata nélkül kell, hogy kiszámolható legyen. Ezért például nem lehet egy child elemének anchors.left: parent.left és anchors.right: parent.right is. Ha olyat akarsz, hogy a szülő határozza meg a tartalma méretét, akkor ne GroupBox-ot használj!


### QML GroupBox title ###

Ha QML-ben egy GroupBox-nak nem akarod, hogy title-je legyen, akkor se hagyd üresen ezt a paramétert, mert feljebb fog csúszni a tényleges tartalom, kilógva a keretből. Egy szóköz segít: title: " "

### Kép beszúrása gráfra ###
Ha képet szeretnél beszúrni gráfra és azt később dinamikusan változtatni, akkor azt a következő módon teheted meg:

    Image{
    id: image1
    visible: false
    source: 'kiscica.png'
    }

A fenti kód segítségével hozd létre a képet, objektumot és rejtsd el(visible:false), mindezt a canvason belül. Ezután id segítségével tudsz rá hivatkozni és manipulálni:

    context.drawImage(image1, width, height, width, height);

Mivel ez javascript, ezért rengeteg lehetőséget biztosít különféle módosításokhoz a képpel.
Dokumentáció: [https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/drawImage](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/drawImage) 

### Doxygen binárisok ###

Régebbi Doxygen binárisok letöltése: [https://sourceforge.net/projects/doxygen/files/](https://sourceforge.net/projects/doxygen/files/)  
(mi linuxon végül a 1.8.11-es verzióval csináltuk).
