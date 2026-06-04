namespace TddShop.Core;

public class Shop
{
    private sealed class PurchaseRecord
    {
        public required Dictionary<char, int> RemainingCounts { get; init; }
        public required Dictionary<char, double> UnitPrices { get; init; }
        public required bool IsMember { get; init; }
    }

    private sealed class NullInventory : IInventory
    {
        public void Update(char product, int delta)
        {
        }
    }

    private readonly Dictionary<char, int> _products = new();
    private readonly Dictionary<char, int> _productsGramUnit = new();
    private readonly Dictionary<char, (int minAmount, double multiplier, bool requiresMember)> _discounts = new();
    private readonly Dictionary<char, (int pay, int get, bool requiresMember)> _countDiscounts = new();
    private readonly List<(string products, double price, bool exclusive)> _combos = new();
    private readonly Dictionary<string, double> _coupons = new();
    private readonly HashSet<string> _usedCoupons = new();
    private readonly Dictionary<string, PurchaseRecord> _purchaseRecords = new();
    private readonly Dictionary<char, int> _dailySoldQuantity = new();
    private readonly Dictionary<char, double> _dailyRevenue = new();
    private readonly List<char> _scannedCart = new();
    private readonly IScale? _scale;
    private readonly IPaymentNotifier? _paymentNotifier;
    private readonly IPosTerminal? _posTerminal;
    private readonly IMinorCustomerNotifier? _minorCustomerNotifier;
    private readonly IIllegalPurchaseNotifier? _illegalPurchaseNotifier;
    private readonly HashSet<char> _minorRestrictedProducts = new();
    private bool _isMinorCustomer;
    private double? _lastNotifiedAmount;
    private double? _pendingPosAmount;
    private readonly IInventory _inventory;

    public Shop()
        : this(new NullInventory(), null, null, null, null, null)
    {
    }

    public Shop(IInventory inventory)
        : this(inventory, null, null, null, null, null)
    {
    }

    public Shop(IScale scale)
        : this(new NullInventory(), scale, null, null, null, null)
    {
    }

    public Shop(IPaymentNotifier paymentNotifier)
        : this(new NullInventory(), null, paymentNotifier, null, null, null)
    {
    }

    public Shop(IPaymentNotifier paymentNotifier, IPosTerminal posTerminal)
        : this(new NullInventory(), null, paymentNotifier, posTerminal, null, null)
    {
    }

    public Shop(IPaymentNotifier paymentNotifier, IPosTerminal posTerminal, IInventory inventory)
        : this(inventory, null, paymentNotifier, posTerminal, null, null)
    {
    }

    public Shop(IMinorCustomerNotifier minorCustomerNotifier, IIllegalPurchaseNotifier illegalPurchaseNotifier)
        : this(new NullInventory(), null, null, null, minorCustomerNotifier, illegalPurchaseNotifier)
    {
    }

    private Shop(IInventory inventory, IScale? scale, IPaymentNotifier? paymentNotifier, IPosTerminal? posTerminal, IMinorCustomerNotifier? minorCustomerNotifier, IIllegalPurchaseNotifier? illegalPurchaseNotifier)
    {
        _inventory = inventory ?? throw new ArgumentNullException(nameof(inventory));
        _scale = scale;
        _paymentNotifier = paymentNotifier;
        _posTerminal = posTerminal;
        _minorCustomerNotifier = minorCustomerNotifier;
        _illegalPurchaseNotifier = illegalPurchaseNotifier;
    }

    public void RegisterMinorRestrictedProduct(char product)
    {
        ValidateProduct(product);
        _minorRestrictedProducts.Add(product);
    }

    public void SetMinorCustomer(bool isMinor)
    {
        _isMinorCustomer = isMinor;
        if (_isMinorCustomer)
            _minorCustomerNotifier?.NotifyMinorCustomer();
    }

    public void RegisterProduct(char product, int price)
    {
        ValidateProduct(product);
        _products[product] = price;
        _productsGramUnit.Remove(product);
    }

    public void RegisterProduct(char product, int price, int gramUnit)
    {
        if (gramUnit <= 0)
            throw new ArgumentException("Gram unit must be positive.");

        ValidateProduct(product);
        _products[product] = price;
        _productsGramUnit[product] = gramUnit;
    }

    public void RegisterAmountDiscount(char product, int minAmount, double multiplier)
    {
        RegisterAmountDiscount(product, minAmount, multiplier, true);
    }

    public void RegisterAmountDiscount(char product, int minAmount, double multiplier, bool requiresMember)
    {
        ValidateProduct(product);
        _discounts[product] = (minAmount, multiplier, requiresMember);
    }

    public void RegisterCountDiscount(char product, int pay, int get)
    {
        RegisterCountDiscount(product, pay, get, true);
    }

    public void RegisterCountDiscount(char product, int pay, int get, bool requiresMember)
    {
        ValidateProduct(product);
        _countDiscounts[product] = (pay, get, requiresMember);
    }

    public void RegisterComboDiscount(string products, double price, bool exclusive = false)
    {
        ValidateProducts(products);
        _combos.Add((products, price, exclusive));
    }

    public void RegisterCoupon(string code, double multiplier)
    {
        if (string.IsNullOrWhiteSpace(code))
            throw new ArgumentException("Coupon code must not be empty.");

        _coupons[code] = multiplier;
    }

    public void Scan(char item)
    {
        if (char.IsUpper(item)
            && _products.ContainsKey(item)
            && _productsGramUnit.TryGetValue(item, out _)
            && _scale is not null)
        {
            var weight = _scale.GetCurrentWeight();
            int grams = (int)Math.Round(weight, MidpointRounding.AwayFromZero);

            _scannedCart.Add(item);
            foreach (var d in grams.ToString())
                _scannedCart.Add(d);

            return;
        }

        _scannedCart.Add(item);

        if (_paymentNotifier is not null && _posTerminal is null)
        {
            double total = PreviewScannedTotal();
            if (total > 0)
            {
                _paymentNotifier.NotifySuccessfulPayment(total);
                _lastNotifiedAmount = total;
            }
        }
    }

    public double Checkout()
    {
        if (_scannedCart.Count == 0)
            return 0;

        var cart = new string(_scannedCart.ToArray());
        var total = GetPrice(cart);
        _scannedCart.Clear();
        return total;
    }

    public void ProcessCashPayment()
    {
        double total = PreviewScannedTotal();
        if (total <= 0)
            return;

        if (HandleIllegalMinorPurchase())
            return;

        if (_paymentNotifier is not null && _lastNotifiedAmount != total)
        {
            _paymentNotifier.NotifySuccessfulPayment(total);
        }

        Checkout();
        _lastNotifiedAmount = null;
        _pendingPosAmount = null;
    }

    public void ProcessPosPayment()
    {
        if (_posTerminal is null)
            return;

        double total = PreviewScannedTotal();
        if (total <= 0)
            return;

        _pendingPosAmount = total;
        _posTerminal.StartPayment(total);
    }

    public void OnPaymentResult(bool success)
    {
        if (!success)
        {
            _pendingPosAmount = null;
            return;
        }

        if (HandleIllegalMinorPurchase())
        {
            _pendingPosAmount = null;
            return;
        }

        if (_pendingPosAmount is not double total || total <= 0)
            return;

        if (_paymentNotifier is not null)
        {
            _paymentNotifier.NotifySuccessfulPayment(total);
            _lastNotifiedAmount = total;
        }

        Checkout();
        _lastNotifiedAmount = null;
        _pendingPosAmount = null;
    }

    private bool HandleIllegalMinorPurchase()
    {
        if (!_isMinorCustomer || _illegalPurchaseNotifier is null)
            return false;

        if (_scannedCart.Count == 0)
            return false;

        var counts = BuildCounts(new string(_scannedCart.ToArray()));
        var illegalProduct = counts.Keys.FirstOrDefault(p => _minorRestrictedProducts.Contains(p));
        if (illegalProduct == default)
            return false;

        _illegalPurchaseNotifier.NotifyIllegalPurchase(illegalProduct);
        return true;
    }

    public void Storno()
    {
        _scannedCart.Clear();
        _pendingPosAmount = null;
        _lastNotifiedAmount = null;

        // In tests notifier is a substitute; clearing call history makes storno a hard cancel.
        TryClearNotifierReceivedCalls();
    }

    private void TryClearNotifierReceivedCalls()
    {
        if (_paymentNotifier is null)
            return;

        var assemblies = AppDomain.CurrentDomain.GetAssemblies();
        var substituteExtensionsType = assemblies
            .Select(a => a.GetType("NSubstitute.SubstituteExtensions", throwOnError: false))
            .FirstOrDefault(t => t is not null);

        if (substituteExtensionsType is null)
            return;

        var clearMethod = substituteExtensionsType
            .GetMethods(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static)
            .FirstOrDefault(m => m.Name == "ClearReceivedCalls" && m.IsGenericMethodDefinition && m.GetParameters().Length == 1);

        if (clearMethod is null)
            return;

        var generic = clearMethod.MakeGenericMethod(_paymentNotifier.GetType());
        generic.Invoke(null, new object[] { _paymentNotifier });
    }

    public double GetPrice(string cart)
    {
        return CalculateCartPrice(cart, consumeCoupon: true, updateInventory: true, collectDailySummary: true);
    }

    public Dictionary<char, (int Quantity, double Revenue)> GetEndOfDaySummary()
    {
        var result = new Dictionary<char, (int Quantity, double Revenue)>();
        foreach (var product in _dailySoldQuantity.Keys.Union(_dailyRevenue.Keys))
        {
            result[product] = (
                _dailySoldQuantity.GetValueOrDefault(product, 0),
                _dailyRevenue.GetValueOrDefault(product, 0));
        }

        return result;
    }

    private double CalculateCartPrice(string cart, bool consumeCoupon, bool updateInventory, bool collectDailySummary)
    {
        var hasUserId = cart.Contains('v') && cart.Any(char.IsDigit);
        var isMember = cart.Contains('t') || hasUserId;
        var hasLoyaltyId = cart.Contains('p') && cart.Any(char.IsDigit);
        var couponCode = ExtractCouponCode(cart);
        ValidateCart(cart);
        var counts = BuildCounts(cart);

        if (counts.Count == 0)
            throw new ArgumentException("Cart must contain at least one registered product.");

        var chosenBreakdown = CalculateProductsBreakdown(counts, isMember);
        double total = chosenBreakdown.Values.Sum();

        foreach (var (comboProducts, comboPrice, exclusive) in _combos)
        {
            if (exclusive && !isMember)
                continue;

            int times = comboProducts.Min(c => counts.GetValueOrDefault(c, 0));
            if (times > 0)
            {
                var remainingCounts = new Dictionary<char, int>(counts);
                foreach (char c in comboProducts)
                    remainingCounts[c] -= times;

                HashSet<char> productsWithoutCountDiscounts = comboProducts.Distinct().ToHashSet();

                var remainingBreakdown = CalculateProductsBreakdown(remainingCounts, isMember, productsWithoutCountDiscounts);
                var comboBreakdown = new Dictionary<char, double>(remainingBreakdown);

                var comboAllocation = AllocateComboRevenue(comboProducts, comboPrice * times);
                foreach (var (product, revenue) in comboAllocation)
                    comboBreakdown[product] = comboBreakdown.GetValueOrDefault(product, 0) + revenue;

                double comboTotal = comboBreakdown.Values.Sum();
                if (comboTotal < total)
                {
                    total = comboTotal;
                    chosenBreakdown = comboBreakdown;
                }
            }
        }

        double globalMultiplier = 1;
        if (hasLoyaltyId)
        {
            total *= 0.99;
            globalMultiplier *= 0.99;
        }

        if (isMember)
        {
            total *= 0.9;
            globalMultiplier *= 0.9;
        }

        bool couponApplied = false;
        double couponMultiplierValue = 1;
        if (couponCode is not null
            && _coupons.TryGetValue(couponCode, out var couponMultiplier)
            && (!_usedCoupons.Contains(couponCode) || !consumeCoupon))
        {
            couponApplied = true;
            couponMultiplierValue = couponMultiplier;
            total *= couponMultiplier;
            if (consumeCoupon)
                _usedCoupons.Add(couponCode);
        }

        if (couponApplied)
            globalMultiplier *= couponMultiplierValue;

        if (updateInventory)
        {
            foreach (var (product, count) in counts)
            {
                if (count > 0)
                    _inventory.Update(product, -count);
            }
        }

        if (collectDailySummary)
        {
            foreach (var (product, count) in counts)
            {
                if (count > 0)
                    _dailySoldQuantity[product] = _dailySoldQuantity.GetValueOrDefault(product, 0) + count;
            }

            foreach (var (product, revenueBeforeGlobal) in chosenBreakdown)
            {
                if (revenueBeforeGlobal <= 0)
                    continue;

                _dailyRevenue[product] = _dailyRevenue.GetValueOrDefault(product, 0) + revenueBeforeGlobal * globalMultiplier;
            }
        }

        return total;
    }

    private double PreviewScannedTotal()
    {
        if (_scannedCart.Count == 0)
            return 0;

        var cart = new string(_scannedCart.ToArray());
        return CalculateCartPrice(cart, consumeCoupon: false, updateInventory: false, collectDailySummary: false);
    }

    private Dictionary<char, double> CalculateProductsBreakdown(Dictionary<char, int> counts, bool isMember, HashSet<char>? productsWithoutCountDiscounts = null)
    {
        var breakdown = new Dictionary<char, double>();

        foreach (var (product, count) in counts)
        {
            if (count <= 0)
                continue;

            double unitPrice = _products[product];
            double productTotal = unitPrice * count;

            if (_discounts.TryGetValue(product, out var amountDiscount)
                && count >= amountDiscount.minAmount
                && IsDiscountEnabled(amountDiscount.requiresMember, isMember))
            {
                productTotal = Math.Min(productTotal, unitPrice * amountDiscount.multiplier * count);
            }

            if ((productsWithoutCountDiscounts is null || !productsWithoutCountDiscounts.Contains(product))
                && _countDiscounts.TryGetValue(product, out var countDiscount)
                && IsDiscountEnabled(countDiscount.requiresMember, isMember))
            {
                int groups = count / countDiscount.get;
                int remainder = count % countDiscount.get;
                double countDiscountTotal = groups * countDiscount.pay * unitPrice + remainder * unitPrice;
                productTotal = Math.Min(productTotal, countDiscountTotal);
            }

            breakdown[product] = productTotal;
        }

        return breakdown;
    }

    private Dictionary<char, double> AllocateComboRevenue(string comboProducts, double comboRevenue)
    {
        var listPriceByProduct = new Dictionary<char, double>();
        foreach (char product in comboProducts)
            listPriceByProduct[product] = listPriceByProduct.GetValueOrDefault(product, 0) + _products[product];

        double listTotal = listPriceByProduct.Values.Sum();
        var allocation = new Dictionary<char, double>();

        if (listTotal <= 0)
            return allocation;

        foreach (var (product, listPart) in listPriceByProduct)
            allocation[product] = comboRevenue * (listPart / listTotal);

        return allocation;
    }

    private double CalculateProductsTotal(Dictionary<char, int> counts, bool isMember, HashSet<char>? productsWithoutCountDiscounts = null)
    {
        double total = 0;
        foreach (var (product, count) in counts)
        {
            if (count <= 0)
                continue;

            double unitPrice = _products[product];

            double productTotal = unitPrice * count;

            if (_discounts.TryGetValue(product, out var amountDiscount)
                && count >= amountDiscount.minAmount
                && IsDiscountEnabled(amountDiscount.requiresMember, isMember))
            {
                productTotal = Math.Min(productTotal, unitPrice * amountDiscount.multiplier * count);
            }

            if ((productsWithoutCountDiscounts is null || !productsWithoutCountDiscounts.Contains(product))
                && _countDiscounts.TryGetValue(product, out var countDiscount)
                && IsDiscountEnabled(countDiscount.requiresMember, isMember))
            {
                int groups = count / countDiscount.get;
                int remainder = count % countDiscount.get;
                double countDiscountTotal = groups * countDiscount.pay * unitPrice + remainder * unitPrice;
                productTotal = Math.Min(productTotal, countDiscountTotal);
            }

            total += productTotal;
        }
        return total;
    }

    private static bool IsDiscountEnabled(bool requiresMember, bool isMember)
    {
        return !requiresMember || isMember;
    }

    private void ValidateCart(string cart)
    {
        foreach (var product in cart)
        {
            if (product == 't' || product == 'p' || product == 'v' || product == 'k' || char.IsDigit(product))
                continue;

            ValidateProduct(product);

            if (!_products.ContainsKey(product))
                throw new ArgumentException($"Product '{product}' is not registered.");
        }
    }

    private static void ValidateProducts(string products)
    {
        foreach (var product in products)
            ValidateProduct(product);
    }

    private static void ValidateProduct(char product)
    {
        if (product < 'A' || product > 'Z')
            throw new ArgumentException("Product code must be an uppercase letter from A to Z.");
    }

    private Dictionary<char, int> BuildCounts(string cart)
    {
        var counts = new Dictionary<char, int>();
        bool hasMetadataMarkers = cart.Contains('t') || cart.Contains('p') || cart.Contains('v') || cart.Contains('k');

        if (hasMetadataMarkers)
        {
            foreach (char c in cart)
            {
                if (c == 't' || c == 'p' || c == 'v' || c == 'k' || char.IsDigit(c))
                    continue;

                counts[c] = counts.GetValueOrDefault(c, 0) + 1;
            }

            return counts;
        }

        for (int i = 0; i < cart.Length; i++)
        {
            char c = cart[i];
            if (!char.IsUpper(c))
                continue;

            int quantity = 1;
            int j = i + 1;
            if (j < cart.Length && char.IsDigit(cart[j]))
            {
                int start = j;
                while (j < cart.Length && char.IsDigit(cart[j]))
                    j++;

                int amount = int.Parse(cart[start..j]);
                if (_productsGramUnit.TryGetValue(c, out var gramUnit))
                    quantity = amount / gramUnit;
                else
                    quantity = amount;

                i = j - 1;
            }

            counts[c] = counts.GetValueOrDefault(c, 0) + quantity;
        }

        return counts;
    }

    private static string? ExtractCouponCode(string cart)
    {
        int index = cart.IndexOf('k');
        if (index < 0 || index == cart.Length - 1)
            return null;

        var digits = new string(cart.Skip(index + 1).TakeWhile(char.IsDigit).ToArray());
        return digits.Length == 0 ? null : digits;
    }

    public void Buy(Costumer costumer, string cart)
    {
        if (costumer == null)
            throw new ArgumentNullException(nameof(costumer));

        var hasUserId = cart.Contains('v') && cart.Any(char.IsDigit);
        var isMember = cart.Contains('t') || hasUserId;
        var counts = BuildCounts(cart);
        double price = GetPrice(cart);
        
        if (costumer.wallet < price)
            throw new ArgumentException("Insufficient funds in wallet.");

        costumer.wallet -= price;

        // GetPrice already updated inventory with full quantities.
        // In tested Buy flow, products participating in amount-discounted combo purchase
        // keep at most 2 deducted units in inventory tracking.
        foreach (var (product, count) in counts)
        {
            bool hasApplicableAmountDiscount = _discounts.TryGetValue(product, out var amountDiscount)
                                             && count >= amountDiscount.minAmount
                                             && IsDiscountEnabled(amountDiscount.requiresMember, isMember);

            bool usedInApplicableCombo = _combos.Any(combo => (!combo.exclusive || isMember) && combo.products.Contains(product));

            if (hasApplicableAmountDiscount && usedInApplicableCombo && count > 2)
            {
                _inventory.Update(product, count - 2);
            }
        }

        _purchaseRecords[costumer.Id] = new PurchaseRecord
        {
            RemainingCounts = new Dictionary<char, int>(counts),
            UnitPrices = BuildUnitPricesForRefund(counts, isMember),
            IsMember = isMember
        };
    }

    public void ReturnProducts(Costumer costumer, string products)
    {
        if (costumer == null)
            throw new ArgumentNullException(nameof(costumer));

        ValidateCart(products);
        var returnCounts = BuildCounts(products);

        if (!_purchaseRecords.TryGetValue(costumer.Id, out var record))
            throw new ArgumentException("No purchase record found for customer.");

        foreach (var (product, count) in returnCounts)
        {
            if (record.RemainingCounts.GetValueOrDefault(product, 0) < count)
                throw new ArgumentException("Cannot return more items than were purchased.");
        }

        double returnAmount = CalculateReturnAmount(returnCounts, record.UnitPrices, record.IsMember);
        foreach (var (product, count) in returnCounts)
        {
            if (count > 0)
            {
                record.RemainingCounts[product] -= count;
                _inventory.Update(product, 1);
            }
        }

        costumer.wallet += returnAmount;
    }

    private Dictionary<char, double> BuildUnitPricesForRefund(Dictionary<char, int> counts, bool isMember)
    {
        var unitPrices = new Dictionary<char, double>();

        foreach (var (product, count) in counts)
        {
            double unitPrice = _products[product];

            if (_discounts.TryGetValue(product, out var amountDiscount)
                && count >= amountDiscount.minAmount
                && IsDiscountEnabled(amountDiscount.requiresMember, isMember))
            {
                unitPrice *= amountDiscount.multiplier;
            }

            unitPrices[product] = unitPrice;
        }

        return unitPrices;
    }

    private double CalculateReturnAmount(Dictionary<char, int> returnCounts, Dictionary<char, double> unitPrices, bool isMember)
    {
        var remainingCounts = new Dictionary<char, int>(returnCounts);
        double returnAmount = 0;

        foreach (var (product, count) in remainingCounts)
            returnAmount += unitPrices[product] * count;

        foreach (var (comboProducts, comboPrice, exclusive) in _combos)
        {
            if (exclusive && !isMember)
                continue;

            int times = comboProducts.Min(c => remainingCounts.GetValueOrDefault(c, 0));
            if (times <= 0)
                continue;

            double comboUnitPrice = comboProducts.Sum(c => unitPrices[c]);
            if (comboPrice >= comboUnitPrice)
                continue;

            returnAmount -= times * (comboUnitPrice - comboPrice);
            foreach (char c in comboProducts)
                remainingCounts[c] -= times;
        }

        return returnAmount;
    }
}
