namespace TddShop.Core;

public class Costumer
{
    public string Id { get; }
    public double wallet { get; set; }

    public Costumer(string id)
    {
        if (string.IsNullOrWhiteSpace(id))
            throw new ArgumentException("Costumer ID must not be empty.");
        
        Id = id;
        wallet = 0;
    }

    public void setwallet(double amount)
    {
        if (amount < 0)
            throw new ArgumentException("Wallet amount must be non-negative.");
        
        wallet = amount;
    }
}
