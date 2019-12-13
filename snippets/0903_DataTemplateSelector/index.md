---
layout: default
codename: DataTemplateSelector
title: DataTemplateSelector használata ListView elemekhez
tags: xaml, snippet
authors: Faragó Timea
---

# DataTemplateSelector használata ListView elemekhez
Gyakran adódhat olyan, hogy egy heterogén kollekció elemeit kell megjelenítenünk egy listában és a lista egyes elemeinek máshogy kinézniük, más tulajdonságokat kell megjeleníteni a konkrét típusoktól függetlenül. Ehhez nézzünk most egy szemléltető példát.
## Lista
Az elemeket egy ListView-ban tároljuk. Ez nem ritkaság XAML technológiás alkalmazásoknál.
Először részletezzük egy kicsit a példát és a hozzá tartozó "mesét".
### Model osztályok
Egy madarakat nyilvántartó rendszerünk van. A madarakról egységesen nyilvántartjuk az alábbi tulajdonságokat:
* név (Name),
* kor (Age),
* személyiség (Personality),
* elégedettsége (Satisfaction).
Egy maradat lehet
* etetni (Feed) és
* megijeszteni (Scare)
Etetés és megijesztés hatására a madarunk fajtól függően változik valahogyan egy 1-5 skálán. Személyiség egy enum.
```csharp
    public interface IBird
    {
        public string Name { get; set; }
        public int Age { get; set; }
        public Personality Personality { get; set; }
        public int Satisfaction { get; set; }

        public void Feed();
        public void Scare();
    }
    public enum Personality
    {
        Wise,
        PeaceLoving,
        Showy
    }
```
Közös interface a madarak leírására az IBird. Mivel a különböző fajtájú madarak máshogy reagálnak az etetésre és megijesztésre, ezért más az implementációjuk, külön osztályokba kerülnek. Lesz egy Bagoly, Owl és egy Galamb, Dove osztályunk most, amelyek megvalósítják az IBird interface-t.
### Mintaadatok
Az egyszerűség kedvéért most a mintaadatokat a code-behind fájlba vesszük fel, nem használunk MVVM mintát, nem annak az ismertetése a cél. Ne felejtsük el beállítani a DataContext-et, property-ként egy ObservabeCollection-t használni a listához és ezt inicializálni!
```csharp
    public partial class MainWindow : Window
    {
        public ObservableCollection<IBird> Birds { get; set; }
        public MainWindow()
        {
            InitializeComponent();
            DataContext = this;
            Birds = new ObservableCollection<IBird>();
            Birds.Add(new Owl()
            {
                Name = "Uhu",
                Age = 2,
                Personality = Personality.Wise,
                Satisfaction = 3
            });
            Birds.Add(new Dove()
            {
                Name = "Tubi",
                Age = 1,
                Personality = Personality.PeaceLoving,
                Satisfaction = 5
            });
        }
    }
```
*Megjegyzés: a jelenlegi példa WPF technológiát használ, UWP technológiánál ez egy Page objektumra fog vonatkozni, nem egy Window-ra. DataTemplete bemutatása szempontjából ez nem befolyásol semmit.*
### ListView
Adjunk hozzá a megjelenő MainWindow-hoz (WPF)/MainPage-hez(UWP) egy ListView-t és csináljuk meg hozzá az adatkötést!
```xml
<ListView ItemsSource="{Binding Birds}" Grid.Row="0"/>
```
## DataTemplate
Ahhoz, hogy típus alapján tudjunk megjelenítést módosítani először definiáljuk a használandó template-eket, sablonokat XAML kódban.
*Megjegyzés: WPF esetén ``<Window.Resources>``, UWP esetén ``<Page.Resources>`` használandó!*
```xml
    <Window.Resources>
        <DataTemplate x:Key="OwlDataTemplate">
            <StackPanel Orientation="Horizontal" Background="Beige">
                <TextBlock Text="{Binding Name}" FontSize="15" FontWeight="Bold" Margin="10" Width="150"/>
                <TextBlock Text="{Binding Age}" Margin="10" Width="150"/>
                <TextBlock Text="{Binding Personality}" Margin="10" Width="150"/>
                <TextBlock Text="{Binding Satisfaction}" Margin="10" Width="150"/>
            </StackPanel>
        </DataTemplate>
        <DataTemplate x:Key="DoveDataTemplate">
            <StackPanel Orientation="Horizontal" Background="LightGray">
                <TextBlock Text="{Binding Name}" Margin="10" Width="150"/>
                <TextBlock Text="{Binding Age}" Margin="10" Width="150"/>
                <TextBlock Text="{Binding Personality}" Margin="10" Width="150"/>
                <TextBlock Text="{Binding Satisfaction}" Margin="10" Width="150"/>
            </StackPanel>
        </DataTemplate>
        <DataTemplate x:Key="DefaultDataTemplate">
            <StackPanel Orientation="Horizontal" Background="White">
                <TextBlock Text="{Binding Name}" Margin="10" Width="150" FontStyle="Italic"/>
                <TextBlock Text="{Binding Age}" Margin="10" Width="150"/>
                <TextBlock Text="{Binding Personality}" Margin="10" Width="150"/>
                <TextBlock Text="{Binding Satisfaction}" Margin="10" Width="150"/>
            </StackPanel>
        </DataTemplate>
    </Window.Resources>
```
Ez mit is csinál? Lesz egy OwlDataTemplate, egy DoveDataTemplate és egy DefaultDataTemplate DataTemplate-ünk, amelyek stílusozásban egy kicsit eltérnek egymástól (pl. háttérszín).
## DataTemplateSelector
A program nem fogja magától kitalálni, hogy Owl típus esetén az OwlDataTemplate-et használja. Ehhez meg kell írnunk egy saját DataTemplateSelector-t.
```csharp
    public class BirdDataTemplateSelector : DataTemplateSelector
    {
        public override DataTemplate SelectTemplate(object item, DependencyObject container)
        {
            FrameworkElement containr = container as FrameworkElement;
            IBird bird = item as IBird;
            switch (bird.GetType().Name)
            {
                case ("Owl"):
                    return containr.FindResource("OwlDataTemplate") as DataTemplate;

                case ("Dove"):
                    return containr.FindResource("DoveDataTemplate") as DataTemplate;

                default:
                    return containr.FindResource("DefaultDataTemplate") as DataTemplate;
            }
        }
    }
```
Ügyeljünk arra, hogy a switch-case default ága is ott legyen!
## ... és az egész összecsatolása
Az elkészült részeket "legózzuk" össze.
### App.xaml
Először is az App.xaml-ben kell felvennünk erőforrásként a DataTemplateSelector-t.
```xml
    <Application.Resources>
        <local:BirdDataTemplateSelector x:Key="BirdDataTemplateSelector"/>
    </Application.Resources>
```
Ezzel az alkalmazáson belül hivatkozhatóvá, használhatóvá tettük a DataTemplateSelector-t.
### ListView módosítása
Már megvan az ItemsSource, most jön az ItemTemplateSelector.
```xml
<ListView ItemsSource="{Binding Birds}" Grid.Row="0" ItemTemplateSelector="{StaticResource BirdDataTemplateSelector}"/>
```
Ezzel készen is vagyunk.
## Későbbi módosítás
Ha szeretnénk más típusú madarakat is nyilvántartani, akkor azoknak is lesz egy alapértelmezett megjelenése, ennek szemléltetésére vegyünk fel egy új madár fajt és adjunk hozzá egy ilyet a listánkhoz, majd nézzük meg az eredményt!
## További információk
A DataTemplateSelector hivatalos dokumentációja [itt](https://docs.microsoft.com/en-us/dotnet/api/system.windows.controls.datatemplateselector?view=netcore-3.0).
