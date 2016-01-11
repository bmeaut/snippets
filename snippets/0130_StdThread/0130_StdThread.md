---
layout: default
---

# Az std::thread használata röviden

Gyakori eset, hogy valami műveletet egy másik szálon akarunk lefuttatni, vagyis programunk nagy része nem több szálon fut, csak egy művelet hatékonyabb, ha több magot is ki tud használni, akkor az std::thread egy igen egyszerű választás.

A [GrainAutLine](http://bmeaut.github.io/grainautline/) alkalmazásban szükség volt egy olyan függvényre, mely képeket (rétegeket) tud egymásra keverni. Mivel ez a megjelenítés egyik fontos lépése, nem árt, ha gyorsan befejeződik. Mivel ezt pixelenként ugyanúgy és egymástól függetlenül kell elvégezni, ezért ez egy kiváló lehetőség a párhuzamosításra.

## Képek egymásra keverése több szálon

Az ezt megvalósító ImageBlender osztály lényegi része az alábbi:

    class ImageBlender
    {
    public:
    [...]
        // Meghatározza az összekevert képet
        cv::Mat GetBlendedImage();

    private:
        // Az egyes rétegek képei
        std::vector<const cv::Mat*> images;
        // Rétegenként az átlátszóság értéke
        std::vector<float> opacities;
        // Egy kisebb képrészre elvégzi az összekeverést
        void GetBlendedImage(cv::Mat &resultImage, const cv::Rect roi);
        // A használt szálak száma
        const int NumberOfThreads;
    };

Az OpenCV cv::Mat formában tárolja a képeket. A ImageBlender::GetBlendedImage() végzi el ténylegesen a rétegek képeinek (ImageBlender::images) az összekeverését, amihez ImageBlender::opacities tárolja az átlátszóságukat.

Az ImageBlender::GetBlendedImage() egy kis előkészület után feldarabolja a képet részterületekre (vízszintes sávokra, mert így dolgoznak majd az egyes szálak (amennyire lehet) folytonos memóriaterületen, majd minden sávra meghívja a ImageBlender::GetBlendedImage(cv::Mat &resultImage, const cv::Rect roi) metódust. Ennek első paramétere az, hogy az eredmény hova kerüljön (ez egy Mat, amit a GetBlendedImage hoz létre), valamint a RoI, vagyis Region of Interest: az a téglalap, amin ennek a szálnak le kell futnia.

A feladat szétosztó kódrészlet az alábbi:

	// Mérjük a futásidőt, hogy a metódus végén meg tudjuk jeleníteni
    QElapsedTimer timer;
    timer.start();

	// Itt rakjuk össze a végeredményt.
    cv::Mat resultImage(images[0]->rows, images[0]->cols, CV_8UC3);

	[...]

	// Itt tároljuk a szálakat
    std::vector<std::thread> threads(NumberOfThreads);
	// Egy téglalap magassága
    const int sliceHeight = images[0]->rows / NumberOfThreads;
	// Az utolsó téglalap magassága eltérhet
    const int lastSliceHeight = images[0]->rows - (NumberOfThreads - 1) * sliceHeight;
	// A téglalapok szélessége a kép szélességének felel meg.
    const int width = images[0]->cols;

	// Minden szálra
    for(int i = 0; i < NumberOfThreads; i++)
    {
		// A munkaterület
        cv::Rect roi(
                    0,
                    i*sliceHeight,
                    width,
                    ( i == NumberOfThreads - 1 ? lastSliceHeight : sliceHeight )
                    );
		// A szál indítása        
		threads[i] = std::thread([this, &resultImage, roi](){ GetBlendedImage(resultImage, roi); });
    }

	// A fő szál nem tesz  mást, mint megvárja a többieket.
    for(int i = 0; i < NumberOfThreads; i++)
    {
        threads[i].join();
    }

	// Kiírjuk az eltelt időt
    qDebug() << "ImageBlender::GetBlendedImage(): total elapsed time: " << timer.elapsed();

	// Visszaadjuk a végeredményt. (Move szemantikával.)
    return resultImage;
 
A lényegi rész az a sor, ahol elindítjuk a szálakat. Itt az std::thread konstruktorának átadunk egy lambda kifejezést, melyet az a szál végre fog hajtani. A lambda kifejezés három része külön-külön:

	[this, &resultImage, roi]
	()
	{ GetBlendedImage(resultImage, roi); }

A lamda kifejezésnek szüksége lesz három változóra: a this pointerre, mivel a this->GetBlendedImage meghívásához az is kell, mint rejtett paraméter. A resultImage-re, amit referenciaként veszünk át (értékként másolni kellene a cv::Mat objektumot), valamint a roi-t, vagyis a munkaterületet.

Ezután az egyes szálak kiszámolják a rájuk eső képrészletet és ha mind végzett, visszaadjuk az eredményt.

Érdemes megfigyelni az alábbiakat:

  * A végén a lokális resultImage objektumot adjuk vissza, ami viszont utána meg is semmisülne, így C++11-ben a move szemantika értelmében nem másolódik le a visszatérési értékhez, hanem az adattartalom átmozgatódik. Vagyis az itteni return nem másolja le a Mat-ot az érték szerinti átadáshoz.
  * A futási idő méréséhez a kódrészlet a QElapsedTimer osztályt használja, amivel igen könnyű az ilyesmi.
  * A fenti kódrészlet minden lefutáskor újra létre hozza a szálakat. Mivel ez egy elég költséges művelet, továbbfejlesztésként érdemes megfontolni a Thread Pool használatát, vagyis a szálak újrahasznosítását.

## Tanulságos hiba

A fejlesztés során volt egy tanulságos hiba: kezdetben a szál indítás az alábbi volt:

	threads[i] = std::thread([this, &resultImage, &roi](){ GetBlendedImage(resultImage, roi); });

Vagyis a roi paramétert nem érték, hanem referencia szerint vette át a lamda kifejezés. A hivatkozott roi objektumok viszont a ciklusmagon belül voltak deklarálva, így a következő iterációra az életciklusuk lejárt (az objektumok megszűntek), a rájuk hivatkozó referenciák kiértékelése később a threadekben nem definiált viselkedés. A fordító ugyanazt a memóriaterületet hasznosította újra minden roi-objektumhoz, mivel időben nem fednek át az életciklusaik. Mivel a referencia mutatóként van megvalósítva, az összes szál az indulásakor ugyanarra a roi objektumra az utolsóként létrehozottra hivatkozott, ami akkor életciklusa szerint már megszűnt, de a hozzá tartozó memóriaterületet még nem írta felül a program.

Kívülről annyi látszott, hogy a képnek csak az alja készül el. (De az valójában többször is.) A megoldás az volt, hogy a roi-t a lamda kifejezés értékként kapja meg, vagyis az std::thread konstruktor hívásakor a roi másolódjon le és ne egy már megszűnt referenciára hivatkozzon mind. Így már minden szál azon a területen dolgozott, amit a for ciklus kijelölt neki.

<small>Szerzők, verziók: Csorba Kristóf. Javítás: Palotás Boldizsár</small>
