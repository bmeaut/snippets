using FluentAssertions;
using NSubstitute.Core.Arguments;
using NSubstitute.Exceptions;
using TddShop.Core;

namespace TddShop.Tests;

public class ShopTests
{
    [Fact]
    public void alapfeladat()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('C', 20);
        shop.RegisterProduct('E', 50);
        var price = shop.GetPrice("ACEE");
        price.Should().Be(130);
    }

    [Fact]
    public void mennyiseg_kedvezmeny()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('B', 100);
        shop.RegisterAmountDiscount('A', 5, 0.9,false);
        var price = shop.GetPrice("AAAAAAB");
        price.Should().Be(154);
    }

    [Fact]
    public void harmatatfizet_negyetvihet_akcio(){
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('E', 50);
        shop.RegisterCountDiscount('A', 3, 4,false);
        var price = shop.GetPrice("AAAAAEEE");
        price.Should().Be(4*10+3*50);

    }

    [Fact]
    public void kombo_kedvezmeny(){
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('B', 20);
        shop.RegisterProduct('C', 50);
        shop.RegisterProduct('D', 100);
        shop.RegisterComboDiscount("ABC", 60, false);
        var price = shop.GetPrice("CAAAABB");
        price.Should().Be(60+3*10+20);
    }

    [Fact]
    public void tagsag(){
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('B', 20);
        var price = shop.GetPrice("AtB");
        price.Should().Be(30*0.9);
    }

    [Fact]
    public void tagsag_kombo1(){
            var shop = new Shop();
            shop.RegisterProduct('A', 10);
            shop.RegisterProduct('B', 20);
            shop.RegisterProduct('C', 50);
            shop.RegisterProduct('D', 100);
            shop.RegisterComboDiscount("ABC", 60, true);
            var price = shop.GetPrice("CAAAABB");
            price.Should().Be(130);
    }

    [Fact]
    public void tagsag_kombo2(){
            var shop = new Shop();
            shop.RegisterProduct('A', 10);
            shop.RegisterProduct('B', 20);
            shop.RegisterProduct('C', 50);
            shop.RegisterProduct('D', 100);
            shop.RegisterComboDiscount("ABC", 60, true);
            var price = shop.GetPrice("CAAAtABB");
            price.Should().Be(99);
    }

    [Fact]
    public void userid_pontgyujtes(){
            var shop = new Shop();
            shop.RegisterProduct('A', 10);
            shop.RegisterProduct('B', 20);
            shop.RegisterProduct('C', 50);
            var price = shop.GetPrice("AApABC4");
            price.Should().Be(99);
    }

    [Fact]
    public void egyszerre_tobb_kedvezmeny1(){
            var shop = new Shop();
            shop.RegisterProduct('A', 10);
            shop.RegisterProduct('B', 20);
            shop.RegisterProduct('C', 50);
            shop.RegisterAmountDiscount('A', 5, 0.5,false);
            shop.RegisterComboDiscount("ABC", 60, false);
            shop.RegisterCountDiscount('A', 3, 4, false);
            var price = shop.GetPrice("AAAAABC");
            price.Should().Be(5*5 +20 +50);
    }

    [Fact]
    public void egyszerre_tobb_kedvezmeny2(){
            var shop = new Shop();
            shop.RegisterProduct('A', 10);
            shop.RegisterProduct('B', 20);
            shop.RegisterProduct('C', 50);
            shop.RegisterAmountDiscount('A', 5, 0.5,false);
            shop.RegisterComboDiscount("ABC", 10, false);
            shop.RegisterCountDiscount('A', 3, 4, false);
            var price = shop.GetPrice("AAAAABC");
            price.Should().Be(4*10 + 10);
    }

   [Fact]
    public void egyszerre_tobb_kedvezmeny3(){
            var shop = new Shop();
            shop.RegisterProduct('A', 30);
            shop.RegisterProduct('B', 20);
            shop.RegisterProduct('C', 10);
            shop.RegisterAmountDiscount('A', 5, 0.9,false);
            shop.RegisterComboDiscount("ABC", 80, false);
            shop.RegisterCountDiscount('A', 1, 5,false);
            var price = shop.GetPrice("AAAAABC");
            price.Should().Be(30 + 20+10);
    }
   
   

      [Fact]
    public void user_id_klubtagsag1()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('B', 20);
        shop.RegisterProduct('C', 50);
        var price = shop.GetPrice("AAv421ABC");
        price.Should().Be(100*0.9);
    }

      [Fact]
    public void user_id_klubtagsag2()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('B', 20);
        shop.RegisterProduct('C', 50);
        var price = shop.GetPrice("AAv421ABpC");
        price.Should().Be(99*0.9);
    }

    [Fact]
    public void kedvezmeny_nem_ervenyes1()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10); 
        shop.RegisterProduct('B', 20);  
        shop.RegisterProduct('C', 40);   
        shop.RegisterAmountDiscount('A', 5, 0.9,true);
        shop.RegisterCountDiscount('B', 3, 4,true);
        shop.RegisterComboDiscount("ABC", 60, true);
        var price = shop.GetPrice("AAAAABBBBBCCCCC");
        price.Should().Be(5*10+5*20+5*40);
    }
     [Fact]
    public void kedvezmeny_nem_ervenyes2()
    {
       var shop = new Shop();
            shop.RegisterProduct('A', 30);
            shop.RegisterProduct('B', 20);
            shop.RegisterProduct('C', 10);
            shop.RegisterAmountDiscount('A', 5, 0.9,false);
            shop.RegisterComboDiscount("ABC", 80, true);
            shop.RegisterCountDiscount('A', 1, 5,false);
            var price = shop.GetPrice("AAAAABCv123");
            price.Should().Be((30 + 20+10)*0.9);;
    }

     [Fact]
    public void kedvezmeny_nem_ervenyes3()
    {
       var shop = new Shop();
            shop.RegisterProduct('A', 30);
            shop.RegisterProduct('B', 20);
            shop.RegisterProduct('C', 10);
            shop.RegisterAmountDiscount('A', 5, 0.9,true);
            shop.RegisterComboDiscount("ABC", 80, false);
            shop.RegisterCountDiscount('A', 1, 5,true);
            var price = shop.GetPrice("AAAAABCv123");
            price.Should().Be((30 + 20+10)*0.9);
    }

    [Fact]
    public void ures_kosar_dobjon_kivetelt()
    {
        var shop = new Shop();
        Action act = () => shop.GetPrice("");
        act.Should().Throw<ArgumentException>();
    }

    [Fact]
    public void csak_meta_karakterek_dobjanak_kivetelt()
    {
        var shop = new Shop();
        Action act = () => shop.GetPrice("tpv123");
        act.Should().Throw<ArgumentException>();
    }

    [Fact]
    public void ismeretlen_termekkod_dobjon_kivetelt()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        Action act = () => shop.GetPrice("AZ");
        act.Should().Throw<ArgumentException>();
    }

    [Fact]
    public void darabos_kedvezmeny_hatarertekek()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterCountDiscount('A', 3, 4, false);
        shop.GetPrice("AAA").Should().Be(30);
        shop.GetPrice("AAAA").Should().Be(30);
        shop.GetPrice("AAAAA").Should().Be(40);
    }

    [Fact]
    public void darabos_kedvezmeny_tobb_teljes_csoport()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterCountDiscount('A', 3, 4, false);
        var price = shop.GetPrice("AAAAAAAA");
        price.Should().Be(60);
    }

    [Fact]
    public void kombo_tobbszor_is_alkalmazhato()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('B', 20);
        shop.RegisterProduct('C', 50);
        shop.RegisterComboDiscount("ABC", 60, false);
        var price = shop.GetPrice("AABBCC");
        price.Should().Be(120);
    }

    [Fact]
    public void kombo_utan_maradek_termekek_is_helyesen_szamolodnak()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('B', 20);
        shop.RegisterProduct('C', 50);
        shop.RegisterComboDiscount("ABC", 60, false);
        var price = shop.GetPrice("AABCC");
        price.Should().Be(120);
    }

    [Fact]
    public void egyedi_kupon(){
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('B', 20);
        shop.RegisterCoupon("112554", 0.9); 
        var price1 = shop.GetPrice("AABk112554");
        var price2 = shop.GetPrice("AABk112554");
        price1.Should().Be(40*0.9);
        price2.Should().Be(40);
    }

    [Fact]

    public void termek_db(){
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('B', 20);
        shop.RegisterProduct('C', 50);
        var price = shop.GetPrice("A3B3C");
        price.Should().Be(3*10 + 3*20 + 50);
    }
    
    [Fact]
    public void termek_gramm(){
        var shop = new Shop();
        shop.RegisterProduct('A', 10,100);
        shop.RegisterProduct('B', 20);
        shop.RegisterProduct('C', 50,200);
        var price = shop.GetPrice("A300B3");
        price.Should().Be(300/100*10 + 3*20);
        var price2 = shop.GetPrice("C300");
        price2.Should().Be(300/200*50);
    }

    [Fact]
public void vasarlas_utan_a_leltar_frissul_a_megfelelo_darabszamokkal()
{
    var spyInventory = new SpyInventory();
    var shop = new Shop(spyInventory); 
    shop.RegisterProduct('A', 10);
    shop.RegisterProduct('B', 20);   
    shop.GetPrice("AAB");
    spyInventory.UpdatedProducts['A'].Should().Be(-2);
    spyInventory.UpdatedProducts['B'].Should().Be(-1);
}

    [Fact]
public void vasarlas_utan_a_termeket_visszahozza1()
{
    var costumer = new Costumer("v234");
    costumer.setwallet(1000);
    var spyInventory = new SpyInventory();
    var shop = new Shop(spyInventory); 
    shop.RegisterProduct('A', 10);
    shop.RegisterProduct('B', 20);   
    shop.Buy(costumer, "AAB");
    costumer.wallet.Should().Be(1000-40);
    spyInventory.UpdatedProducts['A'].Should().Be(-2);
    spyInventory.UpdatedProducts['B'].Should().Be(-1);
    shop.ReturnProducts(costumer,"AB");
    spyInventory.UpdatedProducts['A'].Should().Be(-1);
    spyInventory.UpdatedProducts['B'].Should().Be(0);
    costumer.wallet.Should().Be(960+30);
}

    [Fact]
public void vasarlas_utan_a_termeket_visszahozza2()
{
    var costumer = new Costumer("v234");
    costumer.setwallet(1000);
    var spyInventory = new SpyInventory();
    var shop = new Shop(spyInventory); 
    shop.RegisterProduct('A', 10);
    shop.RegisterProduct('B', 20);  
    shop.RegisterComboDiscount("AB", 20, false); 
    shop.Buy(costumer, "AAB");
    costumer.wallet.Should().Be(1000-30);
    spyInventory.UpdatedProducts['A'].Should().Be(-2);
    spyInventory.UpdatedProducts['B'].Should().Be(-1);
    shop.ReturnProducts(costumer,"AB");
    spyInventory.UpdatedProducts['A'].Should().Be(-1);
    spyInventory.UpdatedProducts['B'].Should().Be(0);
    costumer.wallet.Should().Be(970+20);
}
    [Fact]
public void vasarlas_utan_a_termeket_visszahozza3()
{
    var costumer = new Costumer("v234");
    costumer.setwallet(1000);
    var spyInventory = new SpyInventory();
    var shop = new Shop(spyInventory); 
    shop.RegisterProduct('A', 30);
    shop.RegisterProduct('B',5);  
    shop.RegisterComboDiscount("AB", 17, false); 
    shop.RegisterAmountDiscount('A', 5, 0.5,false);
    shop.Buy(costumer, "AABAAAA");
    costumer.wallet.Should().Be(1000-15*5-17);
    spyInventory.UpdatedProducts['A'].Should().Be(-2);
    spyInventory.UpdatedProducts['B'].Should().Be(-1);
    shop.ReturnProducts(costumer,"AAB");
    spyInventory.UpdatedProducts['A'].Should().Be(-1);
    spyInventory.UpdatedProducts['B'].Should().Be(0);
    costumer.wallet.Should().Be(908+17+15);
}

[Fact]
public void esemenyvezerelt1()
{
    var shop = new Shop();
    shop.RegisterProduct('A', 10);
    shop.RegisterProduct('C', 20);
    shop.Scan('A');
    shop.Scan('C');
    shop.Scan('A');
    var total = shop.Checkout();
    total.Should().Be(40); 
}

[Fact]
public void esemenyvezerelt2()
{
    var shop = new Shop();
    shop.RegisterProduct('A', 10);
    shop.RegisterProduct('B', 20);
    shop.RegisterProduct('C', 50);
    shop.RegisterComboDiscount("ABC", 60, false);
    shop.Scan('C');
    shop.Scan('A');
    shop.Scan('B');
    shop.Scan('A');
    shop.Checkout().Should().Be(60 + 10);
}

[Fact]
public void esemenyvezerelt3()
{
    var shop = new Shop();
    shop.RegisterProduct('A', 10);
    
    shop.Scan('A');
    shop.Scan('t');
    shop.Scan('A');
    shop.Checkout().Should().Be(18);
}

[Fact]
public void checkout_utan_a_kosar_kiurul()
{
    var shop = new Shop();
    shop.RegisterProduct('A', 10);
    shop.Scan('A');
    shop.Checkout().Should().Be(10);
    shop.Checkout().Should().Be(0); 
}

[Fact]
public void merleg1()
{
    var mockScale = Substitute.For<IScale>();
    var shop = new Shop(mockScale);
    shop.RegisterProduct('A', 10, 100); 
    mockScale.GetCurrentWeight().Returns(300);
    shop.Scan('A');
    var total = shop.Checkout();
    total.Should().Be(30);
    mockScale.Received(1).GetCurrentWeight();
}

[Fact]
public void merleg2()
{
    var mockScale = Substitute.For<IScale>();
    var shop = new Shop(mockScale);
    shop.RegisterProduct('B', 100); 
    shop.Scan('B');
    shop.Checkout();
    mockScale.DidNotReceive().GetCurrentWeight();
}

[Fact]
public void fizetes_esemeny_utan_a_fopenztaros_ertesul_a_vegosszegrol()
{

    var mockNotifier = Substitute.For<IPaymentNotifier>();
    var shop = new Shop(mockNotifier);
    shop.RegisterProduct('A', 100);
    shop.Scan('A');
    shop.Scan('A');
    mockNotifier.Received(1).NotifySuccessfulPayment(200);
}

[Fact]
public void ures_kosar_eseten_nincs_fizetesi_ertesites()
{
    var mockNotifier = Substitute.For<IPaymentNotifier>();
    var shop = new Shop(mockNotifier);
    shop.ProcessCashPayment();
    mockNotifier.DidNotReceive().NotifySuccessfulPayment(Arg.Any<double>());
}

[Fact]
public void sikeres_fizetes_utan_a_kosar_kiurul()
{
    
    var mockNotifier = Substitute.For<IPaymentNotifier>();
    var shop = new Shop(mockNotifier);
    shop.RegisterProduct('A', 100);
    shop.Scan('A');
    shop.ProcessCashPayment();
    shop.ProcessCashPayment();
    mockNotifier.Received(1).NotifySuccessfulPayment(100);
}

[Fact]
    public void pos_fizetes_gomb_meghivja_a_terminalt_a_megfelelo_osszeggel()
    {
        var mockNotifier = Substitute.For<IPaymentNotifier>();
        var mockPos = Substitute.For<IPosTerminal>();
        var shop = new Shop(mockNotifier, mockPos);        
        shop.RegisterProduct('A', 500);
        shop.Scan('A');
        shop.ProcessPosPayment(); 
        mockPos.Received(1).StartPayment(500);
    }

    [Fact]
    public void sikeres_pos_visszaigazolas_eseten_lejelenti_a_fizetest_es_uriti_a_kosarat()
    {
        var mockNotifier = Substitute.For<IPaymentNotifier>();
        var mockPos = Substitute.For<IPosTerminal>();
        var shop = new Shop(mockNotifier, mockPos);
        shop.RegisterProduct('A', 100);
        shop.Scan('A');
        shop.ProcessPosPayment(); 
        shop.OnPaymentResult(true); 
        mockNotifier.Received(1).NotifySuccessfulPayment(100);
        shop.ProcessCashPayment(); 
        mockNotifier.Received(1).NotifySuccessfulPayment(Arg.Any<double>()); 
    }

    [Fact]
    public void sikertelen_pos_visszaigazolas_eseten_nincs_jelentes_es_a_kosar_megmarad()
    {
        var mockNotifier = Substitute.For<IPaymentNotifier>();
        var mockPos = Substitute.For<IPosTerminal>();
        var shop = new Shop(mockNotifier, mockPos);
        shop.RegisterProduct('A', 100);
        shop.Scan('A');
        shop.ProcessPosPayment(); 
        shop.OnPaymentResult(false); 
        mockNotifier.DidNotReceive().NotifySuccessfulPayment(Arg.Any<double>());
        shop.ProcessCashPayment();
        mockNotifier.Received(1).NotifySuccessfulPayment(100);
    }

[Fact]
    public void storno_gomb_uriti_a_kosarat()
    {
        
        var mockNotifier = Substitute.For<IPaymentNotifier>();
        var shop = new Shop(mockNotifier);
        shop.RegisterProduct('A', 100);

        shop.Scan('A');
        shop.Scan('A'); 
        
        
        shop.Storno(); 

        
        shop.ProcessCashPayment();

        
        mockNotifier.DidNotReceive().NotifySuccessfulPayment(Arg.Any<double>());
        
        
        shop.Checkout().Should().Be(0);
    }

    [Fact]
    public void storno_eseten_a_leltarbol_nem_vonodik_le_a_termek()
    {
        
        var spyInventory = new SpyInventory();
        var mockNotifier = Substitute.For<IPaymentNotifier>();
        var shop = new Shop(mockNotifier, Substitute.For<IPosTerminal>(), spyInventory);
        
        shop.RegisterProduct('A', 100);
        
        
        shop.Scan('A');
        shop.Scan('A');
        shop.Storno(); 
        
        shop.ProcessCashPayment(); 

        
        
        
        if (spyInventory.UpdatedProducts.ContainsKey('A')) 
        {
            spyInventory.UpdatedProducts['A'].Should().Be(0);
        }
    }

    [Fact]
    public void pos_fizetes_alatt_torteno_storno_megszakitja_a_folyamatot()
    {
        
        var mockNotifier = Substitute.For<IPaymentNotifier>();
        var mockPos = Substitute.For<IPosTerminal>();
        var shop = new Shop(mockNotifier, mockPos);
        shop.RegisterProduct('A', 100);
        
        shop.Scan('A');
        
        
        shop.ProcessPosPayment(); 
        shop.Storno();            
        
        
        shop.OnPaymentResult(true); 

        
        
        
        mockNotifier.DidNotReceive().NotifySuccessfulPayment(Arg.Any<double>());
    }

    [Fact]
    public void napi_osszesites_keszpenzes_fizetes_utan_tartalmazza_a_darabszamot_es_bevetelt()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('B', 20);

        shop.Scan('A');
        shop.Scan('A');
        shop.Scan('B');
        shop.ProcessCashPayment();

        var report = GetEndOfDaySummary(shop);

        report['A'].Quantity.Should().Be(2);
        report['A'].Revenue.Should().Be(20);
        report['B'].Quantity.Should().Be(1);
        report['B'].Revenue.Should().Be(20);
    }

    [Fact]
    public void napi_osszesitesbe_csak_sikeres_ertekesites_szamit_storno_nem()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);

        shop.Scan('A');
        shop.Storno();
        shop.ProcessCashPayment();

        var report = GetEndOfDaySummary(shop);
        report.Should().BeEmpty();
    }

    [Fact]
    public void napi_osszesites_kombo_eseten_aranyosan_osztja_fel_a_bevetelt_listaarak_szerint()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('B', 20);
        shop.RegisterProduct('C', 50);
        shop.RegisterComboDiscount("ABC", 60, false);

        shop.Scan('A');
        shop.Scan('B');
        shop.Scan('C');
        shop.ProcessCashPayment();

        var report = GetEndOfDaySummary(shop);

        report['A'].Quantity.Should().Be(1);
        report['B'].Quantity.Should().Be(1);
        report['C'].Quantity.Should().Be(1);
        report['A'].Revenue.Should().BeApproximately(7.5, 0.0001);
        report['B'].Revenue.Should().BeApproximately(15, 0.0001);
        report['C'].Revenue.Should().BeApproximately(37.5, 0.0001);
    }

    [Fact]
    public void napi_osszesites_kombo_plusz_maradek_termekek_eseten_is_helyes()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.RegisterProduct('B', 20);
        shop.RegisterProduct('C', 50);
        shop.RegisterComboDiscount("ABC", 60, false);

        foreach (var item in "CAAAABB")
            shop.Scan(item);

        shop.ProcessCashPayment();

        var report = GetEndOfDaySummary(shop);

        report['A'].Quantity.Should().Be(4);
        report['B'].Quantity.Should().Be(2);
        report['C'].Quantity.Should().Be(1);
        report['A'].Revenue.Should().BeApproximately(37.5, 0.0001);
        report['B'].Revenue.Should().BeApproximately(35, 0.0001);
        report['C'].Revenue.Should().BeApproximately(37.5, 0.0001);
    }

    [Fact]
    public void napi_osszesites_pos_hiba_utan_nem_no_de_kesobbi_sikeres_fizetes_utan_igen()
    {
        var notifier = Substitute.For<IPaymentNotifier>();
        var pos = Substitute.For<IPosTerminal>();
        var shop = new Shop(notifier, pos);
        shop.RegisterProduct('A', 100);

        shop.Scan('A');
        shop.ProcessPosPayment();
        shop.OnPaymentResult(false);
        GetEndOfDaySummary(shop).Should().BeEmpty();

        shop.ProcessCashPayment();

        var report = GetEndOfDaySummary(shop);
        report['A'].Quantity.Should().Be(1);
        report['A'].Revenue.Should().Be(100);
    }

    [Fact]
    public void napi_osszesites_lekerdezese_nem_nullazza_az_adatokat()
    {
        var shop = new Shop();
        shop.RegisterProduct('A', 10);
        shop.Scan('A');
        shop.ProcessCashPayment();

        var first = GetEndOfDaySummary(shop);
        var second = GetEndOfDaySummary(shop);

        first['A'].Quantity.Should().Be(1);
        first['A'].Revenue.Should().Be(10);
        second['A'].Quantity.Should().Be(1);
        second['A'].Revenue.Should().Be(10);
    }

    [Fact]
    public void crd_x02_kiskoru_es_illegalis_vasarlas_interfeszek_leteznek()
    {
        var minorNotifierType = GetRequiredCoreType("IMinorCustomerNotifier");
        var illegalNotifierType = GetRequiredCoreType("IIllegalPurchaseNotifier");

        minorNotifierType.GetMethod("NotifyMinorCustomer", Type.EmptyTypes)
            .Should().NotBeNull("kiskoru eseten kulon esemenyt kell jelezni");

        illegalNotifierType.GetMethod("NotifyIllegalPurchase", new[] { typeof(char) })
            .Should().NotBeNull("illegalis vasarlas jelzeset interfeszen keresztul kell intezni");
    }

    [Fact]
    public void crd_x02_a_shop_tud_kiskoru_ugyfelet_es_kiskorunak_tiltott_termeket_kezelni()
    {
        var minorNotifierType = GetRequiredCoreType("IMinorCustomerNotifier");
        var illegalNotifierType = GetRequiredCoreType("IIllegalPurchaseNotifier");

        var ctor = typeof(Shop).GetConstructor(new[] { minorNotifierType, illegalNotifierType });
        ctor.Should().NotBeNull("a Shop kapjon ket kulon interfeszt a kiskoru es illegalis vasarlas esemenyekhez");

        typeof(Shop).GetMethod("RegisterMinorRestrictedProduct", new[] { typeof(char) })
            .Should().NotBeNull("termekenkent beallithato legyen a kiskoru tiltasa");

        typeof(Shop).GetMethod("SetMinorCustomer", new[] { typeof(bool) })
            .Should().NotBeNull("kulon esemeny jelzeshez lehessen beallitani, hogy a vasarlo kiskoru");
    }

    [Fact]
    public void crd_x02_kiskoru_tiltott_termek_vasarlasa_illegalis_vasarlas_jelzest_kuld()
    {
        var minorNotifierType = GetRequiredCoreType("IMinorCustomerNotifier");
        var illegalNotifierType = GetRequiredCoreType("IIllegalPurchaseNotifier");

        var minorNotifier = Substitute.For(new[] { minorNotifierType }, Array.Empty<object>());
        var illegalNotifier = Substitute.For(new[] { illegalNotifierType }, Array.Empty<object>());

        var shop = CreateShopForMinorRules(minorNotifierType, illegalNotifierType, minorNotifier, illegalNotifier);
        shop.RegisterProduct('A', 100);

        InvokeRequired(shop, "RegisterMinorRestrictedProduct", 'A');
        InvokeRequired(shop, "SetMinorCustomer", true);
        shop.Scan('A');
        shop.ProcessCashPayment();

        CountReceivedCallsByName(minorNotifier, "NotifyMinorCustomer").Should().BeGreaterThan(0);
        CountReceivedCallsByName(illegalNotifier, "NotifyIllegalPurchase").Should().Be(1);

        var args = GetReceivedCallArgs(illegalNotifier, "NotifyIllegalPurchase");
        args.Should().ContainSingle();
        args[0].Should().BeOfType<char>();
        ((char)args[0]).Should().Be('A');
    }

    [Fact]
    public void crd_x02_nem_tiltott_termek_kiskorunal_nem_kuld_illegalis_jelzest()
    {
        var minorNotifierType = GetRequiredCoreType("IMinorCustomerNotifier");
        var illegalNotifierType = GetRequiredCoreType("IIllegalPurchaseNotifier");

        var minorNotifier = Substitute.For(new[] { minorNotifierType }, Array.Empty<object>());
        var illegalNotifier = Substitute.For(new[] { illegalNotifierType }, Array.Empty<object>());

        var shop = CreateShopForMinorRules(minorNotifierType, illegalNotifierType, minorNotifier, illegalNotifier);
        shop.RegisterProduct('B', 100);

        InvokeRequired(shop, "SetMinorCustomer", true);
        shop.Scan('B');
        shop.ProcessCashPayment();

        CountReceivedCallsByName(illegalNotifier, "NotifyIllegalPurchase").Should().Be(0);
    }

    [Fact]
    public void crd_x02_nagykoru_tiltott_termeket_is_megveheti_illegalis_jelzes_nelkul()
    {
        var minorNotifierType = GetRequiredCoreType("IMinorCustomerNotifier");
        var illegalNotifierType = GetRequiredCoreType("IIllegalPurchaseNotifier");

        var minorNotifier = Substitute.For(new[] { minorNotifierType }, Array.Empty<object>());
        var illegalNotifier = Substitute.For(new[] { illegalNotifierType }, Array.Empty<object>());

        var shop = CreateShopForMinorRules(minorNotifierType, illegalNotifierType, minorNotifier, illegalNotifier);
        shop.RegisterProduct('A', 100);

        InvokeRequired(shop, "RegisterMinorRestrictedProduct", 'A');
        InvokeRequired(shop, "SetMinorCustomer", false);
        shop.Scan('A');
        shop.ProcessCashPayment();

        CountReceivedCallsByName(illegalNotifier, "NotifyIllegalPurchase").Should().Be(0);
    }

    private static Dictionary<char, (int Quantity, double Revenue)> GetEndOfDaySummary(Shop shop)
    {
        var method = typeof(Shop).GetMethod("GetEndOfDaySummary");
        method.Should().NotBeNull("a Shop osztalynak tudnia kell nap vegi osszesitest adni");

        var result = method!.Invoke(shop, null);
        result.Should().NotBeNull();

        var typed = result as Dictionary<char, (int Quantity, double Revenue)>;
        typed.Should().NotBeNull("a visszateresi tipus legyen Dictionary<char, (int Quantity, double Revenue)>");
        return typed!;
    }

    private static Type GetRequiredCoreType(string typeName)
    {
        var type = typeof(Shop).Assembly.GetType($"TddShop.Core.{typeName}");
        type.Should().NotBeNull($"a {typeName} interfesznek leteznie kell a TddShop.Core nevtérben");
        return type!;
    }

    private static Shop CreateShopForMinorRules(Type minorNotifierType, Type illegalNotifierType, object minorNotifier, object illegalNotifier)
    {
        var ctor = typeof(Shop).GetConstructor(new[] { minorNotifierType, illegalNotifierType });
        ctor.Should().NotBeNull("a Shop-nak fogadnia kell a ket uj interfeszt");

        var instance = ctor!.Invoke(new[] { minorNotifier, illegalNotifier });
        instance.Should().BeOfType<Shop>();
        return (Shop)instance;
    }

    private static object? InvokeRequired(object target, string methodName, params object[] args)
    {
        var argTypes = args.Select(a => a.GetType()).ToArray();
        var method = target.GetType().GetMethod(methodName, argTypes);
        method.Should().NotBeNull($"a {methodName} API-nak leteznie kell");
        return method!.Invoke(target, args);
    }

    private static int CountReceivedCallsByName(object substitute, string methodName)
    {
        return GetReceivedCalls(substitute).Count(c => GetMethodName(c) == methodName);
    }

    private static object[] GetReceivedCallArgs(object substitute, string methodName)
    {
        var call = GetReceivedCalls(substitute).FirstOrDefault(c => GetMethodName(c) == methodName);
        if (call is null)
            return Array.Empty<object>();

        var getArguments = call.GetType().GetMethod("GetArguments", Type.EmptyTypes);
        var args = getArguments?.Invoke(call, null) as object[];
        return args ?? Array.Empty<object>();
    }

    private static List<object> GetReceivedCalls(object substitute)
    {
        var extType = AppDomain.CurrentDomain.GetAssemblies()
            .Select(a => a.GetType("NSubstitute.SubstituteExtensions", false))
            .FirstOrDefault(t => t is not null);

        extType.Should().NotBeNull("a NSubstitute extension tipusnak elerhetonek kell lennie");

        var receivedCallsMethod = extType!
            .GetMethods(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static)
            .FirstOrDefault(m => m.Name == "ReceivedCalls" && m.IsGenericMethodDefinition && m.GetParameters().Length == 1);

        receivedCallsMethod.Should().NotBeNull("a ReceivedCalls extension metodusnak leteznie kell");

        var generic = receivedCallsMethod!.MakeGenericMethod(substitute.GetType());
        var calls = generic.Invoke(null, new[] { substitute }) as System.Collections.IEnumerable;
        calls.Should().NotBeNull();

        var result = new List<object>();
        foreach (var call in calls!)
            if (call is not null)
                result.Add(call);

        return result;
    }

    private static string GetMethodName(object call)
    {
        var method = call.GetType().GetMethod("GetMethodInfo", Type.EmptyTypes);
        var methodInfo = method?.Invoke(call, null) as System.Reflection.MethodInfo;
        return methodInfo?.Name ?? string.Empty;
    }

}

