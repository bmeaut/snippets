using TddShop.Core;

namespace TddShop.Tests;

public class SpyInventory : IInventory
{
    public Dictionary<char, int> UpdatedProducts { get; } = new();

    public void Update(char product, int delta)
    {
        UpdatedProducts[product] = UpdatedProducts.GetValueOrDefault(product, 0) + delta;
    }
}
