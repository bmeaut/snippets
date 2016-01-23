---
layout: default
---

# UML GitHub-ra Gravizo-val

UML diagrammok készítése webes markdown-ba, github readme-be. Hyperlink beágyazása, serveren generál képet, itt betölti.

## Alapok

    ![Alt text](http://g.gravizo.com/g?
      ide jön a tartalom
    )

Példa:

    ![Alt text](http://g.gravizo.com/g?
      class QObject {}
    )

Ez így ejlenik meg:

![Alt text](http://g.gravizo.com/g?
  class QObject {}
)

## Class diagram


    ![Alt text](http://g.gravizo.com/g?
    /**FooBar
     *@opt all
     */
    class FooBar{
        int foo;
        public int foo%28%29;
        protected void foo%28int bar%29;
        private int dummy_func%28int dummyy_param%29;
    })


![Alt text](http://g.gravizo.com/g?
/**FooBar
 *@opt all
 */
class FooBar{
    int foo;
    public int foo%28%29;
    protected void foo%28int bar%29;
    private int dummy_func%28int dummyy_param%29;
})

### Leszármazás

Java syntax, `extends` kulcsszó.

    ![Alt text](http://g.gravizo.com/g?
    /**Foo
     *@opt all
     */
    class Foo{
        int foo;
        public int foo%28%29;
    }
    /**Bar
     *@opt all
     */
    class Bar extends Foo{
        int bar;
        public int bar%28%29;
    })

![Alt text](http://g.gravizo.com/g?
/**Foo
 *@opt all
 */
class Foo{
    int foo;
    public int foo%28%29;
}
/**Bar
 *@opt all
 */
class Bar extends Foo{
    int bar;
    public int bar%28%29;
})

## Sequence diagram

    ![Alt text](http://g.gravizo.com/g?
    @startuml;
    actor User;
    participant "GUI" as A;
    participant "WorkerClass" as B;
    User -> A: click;
    activate A;
    A -> B: doWork;
    activate B;
    B --> A: result;
    deactivate B;
    A --> User: beep;
    deactivate A;
    @enduml
    )

![Alt text](http://g.gravizo.com/g?
@startuml;
actor User;
participant "GUI" as A;
participant "WorkerClass" as B;
User -> A: click;
activate A;
A -> B: doWork;
activate B;
B --> A: result;
deactivate B;
A --> User: beep;
deactivate A;
@enduml
)
