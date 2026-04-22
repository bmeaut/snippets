namespace TddShop.Core;

public interface IPaymentNotifier
{
    void NotifySuccessfulPayment(double amount);
}
