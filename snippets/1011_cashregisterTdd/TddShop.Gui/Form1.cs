using System.Text;
using TddShop.Core;

namespace TddShop.Gui;

public partial class Form1 : Form
{
    private readonly ListView _summaryList = new();
    private readonly TextBox _logTextBox = new();
    private readonly TextBox _productCodeTextBox = new();
    private readonly TextBox _productPriceTextBox = new();
    private readonly TextBox _gramUnitTextBox = new();
    private readonly CheckBox _restrictedForMinorCheckBox = new();
    private readonly CheckBox _minorCustomerCheckBox = new();
    private readonly TextBox _scanTextBox = new();
    private readonly Label _cartLabel = new();

    private readonly StringBuilder _scannedCart = new();
    private readonly GuiMinorNotifier _minorNotifier;
    private readonly GuiIllegalPurchaseNotifier _illegalNotifier;
    private Shop _shop;

    public Form1()
    {
        InitializeComponent();

        _minorNotifier = new GuiMinorNotifier(AppendLog);
        _illegalNotifier = new GuiIllegalPurchaseNotifier(AppendLog);
        _shop = new Shop(_minorNotifier, _illegalNotifier);

        BuildLayout();
        UpdateCartLabel();
    }

    private void BuildLayout()
    {
        Text = "TddShop - Grafikus Proba";
        Width = 1200;
        Height = 760;

        var root = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 2,
            RowCount = 1,
            Padding = new Padding(12)
        };
        root.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 48));
        root.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 52));
        Controls.Add(root);

        var leftPanel = BuildControlPanel();
        var rightPanel = BuildReportPanel();

        root.Controls.Add(leftPanel, 0, 0);
        root.Controls.Add(rightPanel, 1, 0);
    }

    private Control BuildControlPanel()
    {
        var panel = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 1,
            RowCount = 8
        };

        for (int i = 0; i < panel.RowCount; i++)
            panel.RowStyles.Add(new RowStyle(SizeType.AutoSize));

        panel.Controls.Add(CreateTitle("Bolt Muveletek"), 0, 0);
        panel.Controls.Add(BuildRegisterSection(), 0, 1);
        panel.Controls.Add(BuildMinorSection(), 0, 2);
        panel.Controls.Add(BuildScanSection(), 0, 3);
        panel.Controls.Add(BuildPaymentSection(), 0, 4);
        panel.Controls.Add(BuildCartSection(), 0, 5);
        panel.Controls.Add(BuildUtilitySection(), 0, 6);

        return panel;
    }

    private Control BuildReportPanel()
    {
        var panel = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 1,
            RowCount = 4
        };
        panel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        panel.RowStyles.Add(new RowStyle(SizeType.Percent, 50));
        panel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        panel.RowStyles.Add(new RowStyle(SizeType.Percent, 50));

        panel.Controls.Add(CreateTitle("Napi Osszesites"), 0, 0);

        _summaryList.Dock = DockStyle.Fill;
        _summaryList.View = View.Details;
        _summaryList.FullRowSelect = true;
        _summaryList.GridLines = true;
        _summaryList.Columns.Add("Termek", 120);
        _summaryList.Columns.Add("Eladott db", 140);
        _summaryList.Columns.Add("Bevetel", 160);
        panel.Controls.Add(_summaryList, 0, 1);

        panel.Controls.Add(CreateTitle("Esemenynaplo"), 0, 2);

        _logTextBox.Dock = DockStyle.Fill;
        _logTextBox.Multiline = true;
        _logTextBox.ScrollBars = ScrollBars.Vertical;
        _logTextBox.ReadOnly = true;
        panel.Controls.Add(_logTextBox, 0, 3);

        return panel;
    }

    private Control BuildRegisterSection()
    {
        var group = new GroupBox { Text = "Termek regisztracio", Dock = DockStyle.Top, AutoSize = true };
        var p = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2, AutoSize = true, Padding = new Padding(8) };
        p.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 130));
        p.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));

        _productCodeTextBox.Text = "A";
        _productPriceTextBox.Text = "100";
        _gramUnitTextBox.PlaceholderText = "pl. 100";
        _restrictedForMinorCheckBox.Text = "Kiskorunak tiltott";

        p.Controls.Add(new Label { Text = "Kod (A-Z):", AutoSize = true }, 0, 0);
        p.Controls.Add(_productCodeTextBox, 1, 0);
        p.Controls.Add(new Label { Text = "Ar:", AutoSize = true }, 0, 1);
        p.Controls.Add(_productPriceTextBox, 1, 1);
        p.Controls.Add(new Label { Text = "Gram egyseg:", AutoSize = true }, 0, 2);
        p.Controls.Add(_gramUnitTextBox, 1, 2);
        p.Controls.Add(_restrictedForMinorCheckBox, 1, 3);

        var registerButton = new Button { Text = "Termek felvetele", AutoSize = true };
        registerButton.Click += (_, _) => RegisterProduct();
        p.Controls.Add(registerButton, 1, 4);

        group.Controls.Add(p);
        return group;
    }

    private Control BuildMinorSection()
    {
        var group = new GroupBox { Text = "Vasarlo", Dock = DockStyle.Top, AutoSize = true };
        var p = new FlowLayoutPanel { Dock = DockStyle.Fill, AutoSize = true, Padding = new Padding(8) };

        _minorCustomerCheckBox.Text = "Kiskoru vasarlo";
        _minorCustomerCheckBox.CheckedChanged += (_, _) =>
        {
            _shop.SetMinorCustomer(_minorCustomerCheckBox.Checked);
            AppendLog($"Vasarlo allapot: {(_minorCustomerCheckBox.Checked ? "kiskoru" : "nagykoru")}");
        };

        p.Controls.Add(_minorCustomerCheckBox);
        group.Controls.Add(p);
        return group;
    }

    private Control BuildScanSection()
    {
        var group = new GroupBox { Text = "Szkenneles", Dock = DockStyle.Top, AutoSize = true };
        var p = new FlowLayoutPanel { Dock = DockStyle.Fill, AutoSize = true, Padding = new Padding(8) };

        _scanTextBox.Width = 100;
        _scanTextBox.Text = "A";

        var scanButton = new Button { Text = "Scan", AutoSize = true };
        scanButton.Click += (_, _) => ScanItem();

        p.Controls.Add(new Label { Text = "Karakter:", AutoSize = true, Padding = new Padding(0, 6, 0, 0) });
        p.Controls.Add(_scanTextBox);
        p.Controls.Add(scanButton);

        group.Controls.Add(p);
        return group;
    }

    private Control BuildPaymentSection()
    {
        var group = new GroupBox { Text = "Fizetes", Dock = DockStyle.Top, AutoSize = true };
        var p = new FlowLayoutPanel { Dock = DockStyle.Fill, AutoSize = true, Padding = new Padding(8) };

        var cashButton = new Button { Text = "Keszpenzes fizetes", AutoSize = true };
        cashButton.Click += (_, _) =>
        {
            _shop.ProcessCashPayment();
            _scannedCart.Clear();
            UpdateCartLabel();
            RefreshSummary();
            AppendLog("Keszpenzes fizetes meghivva.");
        };

        var checkoutButton = new Button { Text = "Checkout", AutoSize = true };
        checkoutButton.Click += (_, _) =>
        {
            double total = _shop.Checkout();
            _scannedCart.Clear();
            UpdateCartLabel();
            RefreshSummary();
            AppendLog($"Checkout osszeg: {total:F2}");
        };

        var stornoButton = new Button { Text = "Storno", AutoSize = true };
        stornoButton.Click += (_, _) =>
        {
            _shop.Storno();
            _scannedCart.Clear();
            UpdateCartLabel();
            AppendLog("Storno lefutott.");
        };

        p.Controls.Add(cashButton);
        p.Controls.Add(checkoutButton);
        p.Controls.Add(stornoButton);

        group.Controls.Add(p);
        return group;
    }

    private Control BuildCartSection()
    {
        var group = new GroupBox { Text = "Aktualis kosar", Dock = DockStyle.Top, AutoSize = true };
        var p = new FlowLayoutPanel { Dock = DockStyle.Fill, AutoSize = true, Padding = new Padding(8) };

        _cartLabel.AutoSize = true;
        _cartLabel.Font = new Font(_cartLabel.Font, FontStyle.Bold);
        p.Controls.Add(_cartLabel);

        group.Controls.Add(p);
        return group;
    }

    private Control BuildUtilitySection()
    {
        var p = new FlowLayoutPanel { Dock = DockStyle.Top, AutoSize = true, Padding = new Padding(0, 8, 0, 0) };

        var summaryButton = new Button { Text = "Napi osszesites frissites", AutoSize = true };
        summaryButton.Click += (_, _) => RefreshSummary();

        var resetButton = new Button { Text = "Uj bolt indul", AutoSize = true };
        resetButton.Click += (_, _) =>
        {
            _shop = new Shop(_minorNotifier, _illegalNotifier);
            _scannedCart.Clear();
            _minorCustomerCheckBox.Checked = false;
            _summaryList.Items.Clear();
            AppendLog("Uj bolti allapot inicializalva.");
            UpdateCartLabel();
        };

        var clearLogButton = new Button { Text = "Naplo torles", AutoSize = true };
        clearLogButton.Click += (_, _) => _logTextBox.Clear();

        p.Controls.Add(summaryButton);
        p.Controls.Add(resetButton);
        p.Controls.Add(clearLogButton);

        return p;
    }

    private static Label CreateTitle(string text)
    {
        return new Label
        {
            Text = text,
            AutoSize = true,
            Font = new Font("Segoe UI", 12, FontStyle.Bold),
            Padding = new Padding(0, 0, 0, 8)
        };
    }

    private void RegisterProduct()
    {
        try
        {
            char code = ParseProductCode(_productCodeTextBox.Text);
            int price = int.Parse(_productPriceTextBox.Text);

            if (!string.IsNullOrWhiteSpace(_gramUnitTextBox.Text))
            {
                int gramUnit = int.Parse(_gramUnitTextBox.Text);
                _shop.RegisterProduct(code, price, gramUnit);
            }
            else
            {
                _shop.RegisterProduct(code, price);
            }

            if (_restrictedForMinorCheckBox.Checked)
                _shop.RegisterMinorRestrictedProduct(code);

            AppendLog($"Termek regisztralva: {code}, ar={price}" +
                      (string.IsNullOrWhiteSpace(_gramUnitTextBox.Text) ? "" : $", gramEgyseg={_gramUnitTextBox.Text}") +
                      (_restrictedForMinorCheckBox.Checked ? ", kiskorunak tiltott" : ""));
        }
        catch (Exception ex)
        {
            ShowError(ex);
        }
    }

    private void ScanItem()
    {
        try
        {
            char code = ParseAnyChar(_scanTextBox.Text);
            _shop.Scan(code);
            _scannedCart.Append(code);
            UpdateCartLabel();
            AppendLog($"Szkennelt: {code}");
        }
        catch (Exception ex)
        {
            ShowError(ex);
        }
    }

    private void RefreshSummary()
    {
        _summaryList.Items.Clear();

        var summary = _shop.GetEndOfDaySummary();
        foreach (var entry in summary.OrderBy(e => e.Key))
        {
            var item = new ListViewItem(entry.Key.ToString());
            item.SubItems.Add(entry.Value.Quantity.ToString());
            item.SubItems.Add(entry.Value.Revenue.ToString("F2"));
            _summaryList.Items.Add(item);
        }

        AppendLog("Napi osszesites frissitve.");
    }

    private void UpdateCartLabel()
    {
        _cartLabel.Text = _scannedCart.Length == 0 ? "(ures)" : _scannedCart.ToString();
    }

    private void AppendLog(string message)
    {
        _logTextBox.AppendText($"[{DateTime.Now:HH:mm:ss}] {message}{Environment.NewLine}");
    }

    private void ShowError(Exception ex)
    {
        AppendLog($"HIBA: {ex.Message}");
        MessageBox.Show(ex.Message, "Hiba", MessageBoxButtons.OK, MessageBoxIcon.Error);
    }

    private static char ParseProductCode(string text)
    {
        if (string.IsNullOrWhiteSpace(text) || text.Trim().Length != 1)
            throw new ArgumentException("A termekkod pontosan 1 karakter legyen.");

        char c = text.Trim()[0];
        if (c < 'A' || c > 'Z')
            throw new ArgumentException("A termekkod A-Z kozotti nagybetu legyen.");

        return c;
    }

    private static char ParseAnyChar(string text)
    {
        if (string.IsNullOrWhiteSpace(text) || text.Trim().Length != 1)
            throw new ArgumentException("A szkennelt ertek pontosan 1 karakter legyen.");

        return text.Trim()[0];
    }

    private sealed class GuiMinorNotifier(Action<string> logger) : IMinorCustomerNotifier
    {
        public void NotifyMinorCustomer()
        {
            logger("Kiskoru vasarlo jelzes erkezett.");
        }
    }

    private sealed class GuiIllegalPurchaseNotifier(Action<string> logger) : IIllegalPurchaseNotifier
    {
        public void NotifyIllegalPurchase(char product)
        {
            logger($"ILLEGALIS VASARLAS: {product} termek kiskorunak tiltott.");
            MessageBox.Show($"Kiskoru vasarlo nem veheti meg a(z) {product} termeket.", "Illegalis vasarlas", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }
    }
}
