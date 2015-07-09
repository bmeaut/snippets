---
layout: default
---

# Doxygen

Minimál példa (forráskód kinézete, doxygen config), majd a RobotMonitorban bemutatása, végül konkrét leírás, hogy hogyan kell klónozni GitHub-ról és lefuttatni rajta a Doxygent.

(Qt-ben van valamire közvetlen támogatás? Annak szintaxisa is markdown?)
(JavaDoc hasonlóan egy snippetben?)

http://stackoverflow.com/questions/3052036/how-to-include-custom-files-in-doxygen

http://stackoverflow.com/questions/9502426/how-to-make-an-introduction-page-with-doxygen/9522667#9522667

http://stackoverflow.com/questions/9502426/how-to-make-an-introduction-page-with-doxygen

## main page

As of v1.8.8 there is also the option USE_MDFILE_AS_MAINPAGE. So make sure to add your index file, e.g. README.md, to INPUT and set it as this option's value:
INPUT += README.md
USE_MDFILE_AS_MAINPAGE = README.md


https://www.rosettacommons.org/manuals/rosetta3.2_user_guide/doxygen_tips.html
